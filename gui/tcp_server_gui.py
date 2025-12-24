"""
TCP Server GUI - Server CLI bilan birga ishlash uchun
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import json
import threading
import time
from datetime import datetime
import sys
import os

# Project root'ni path'ga qo'shish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class TCPServerGUI:
    """TCP Server GUI - Server bilan socket orqali muloqot"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("C2 TCP Server - Controller")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1e1e1e')
        
        # Server connection
        self.server_host = '127.0.0.1'
        self.server_port = 9999
        self.connected = False
        self.agents = {}
        
        self.setup_ui()
        self.start_refresh_thread()
        
    def setup_ui(self):
        """UI yaratish"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top panel - Server info and controls
        self.create_top_panel(main_frame)
        
        # Middle panel - Agents list and details
        middle_frame = tk.Frame(main_frame, bg='#1e1e1e')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left - Agents list
        left_frame = tk.Frame(middle_frame, bg='#2d2d2d')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right - Commands and console
        right_frame = tk.Frame(middle_frame, bg='#2d2d2d')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_agents_panel(left_frame)
        self.create_commands_panel(right_frame)
        
        # Bottom - Console
        self.create_console_panel(main_frame)
        
    def create_top_panel(self, parent):
        """Top panel - server status"""
        top_frame = tk.Frame(parent, bg='#2d2d2d', height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Server info
        info_frame = tk.Frame(top_frame, bg='#2d2d2d')
        info_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(info_frame, text="🎯 TCP C2 Server", 
                bg='#2d2d2d', fg='#00ff00', font=('Consolas', 14, 'bold')).pack(anchor='w')
        
        self.status_label = tk.Label(info_frame, text=f"Server: {self.server_host}:{self.server_port}", 
                                     bg='#2d2d2d', fg='#ffffff', font=('Consolas', 10))
        self.status_label.pack(anchor='w')
        
        # Buttons
        btn_frame = tk.Frame(top_frame, bg='#2d2d2d')
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh", command=self.manual_refresh,
                 bg='#404040', fg='#ffffff', font=('Consolas', 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📋 Commands", command=self.show_commands,
                 bg='#404040', fg='#ffffff', font=('Consolas', 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
    def create_agents_panel(self, parent):
        """Agents list panel"""
        # Header
        header = tk.Frame(parent, bg='#3d3d3d', height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 Active Agents", bg='#3d3d3d', fg='#ffffff',
                font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.agent_count_label = tk.Label(header, text="0", bg='#3d3d3d', fg='#00ff00',
                                          font=('Consolas', 10, 'bold'))
        self.agent_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Treeview for agents
        tree_frame = tk.Frame(parent, bg='#2d2d2d')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ('status', 'hostname', 'platform', 'last_seen')
        self.agents_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings',
                                       yscrollcommand=scrollbar.set, selectmode='browse')
        
        self.agents_tree.heading('#0', text='Agent ID')
        self.agents_tree.heading('status', text='Status')
        self.agents_tree.heading('hostname', text='Hostname')
        self.agents_tree.heading('platform', text='Platform')
        self.agents_tree.heading('last_seen', text='Last Seen')
        
        self.agents_tree.column('#0', width=150)
        self.agents_tree.column('status', width=80)
        self.agents_tree.column('hostname', width=120)
        self.agents_tree.column('platform', width=100)
        self.agents_tree.column('last_seen', width=100)
        
        self.agents_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.agents_tree.yview)
        
        # Context menu
        self.agents_tree.bind('<Button-3>', self.show_agent_context_menu)
        self.agents_tree.bind('<<TreeviewSelect>>', self.on_agent_select)
        
        # Agent actions
        action_frame = tk.Frame(parent, bg='#2d2d2d')
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(action_frame, text="🚫 Remove", command=self.remove_agent,
                 bg='#ff4444', fg='#ffffff', font=('Consolas', 9),
                 relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="⚡ Kill", command=self.kill_agent,
                 bg='#ff0000', fg='#ffffff', font=('Consolas', 9),
                 relief=tk.FLAT, padx=10, pady=3).pack(side=tk.LEFT, padx=2)
        
    def create_commands_panel(self, parent):
        """Commands panel"""
        # Header
        header = tk.Frame(parent, bg='#3d3d3d', height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚡ Quick Commands", bg='#3d3d3d', fg='#ffffff',
                font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Commands area
        cmd_area = tk.Frame(parent, bg='#2d2d2d')
        cmd_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command categories
        categories = [
            ("📸 Camera", ["camera_photo", "camera_list"]),
            ("🔊 Audio", ["audio_record 10", "mic_record 5"]),
            ("📍 Location", ["location_gps", "location_info"]),
            ("📱 System", ["sysinfo", "screenshot"])
        ]
        
        for i, (cat_name, commands) in enumerate(categories):
            cat_frame = tk.LabelFrame(cmd_area, text=cat_name, bg='#2d2d2d', fg='#00ff00',
                                     font=('Consolas', 10, 'bold'))
            cat_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
            
            for cmd in commands:
                tk.Button(cat_frame, text=cmd, command=lambda c=cmd: self.send_quick_command(c),
                         bg='#404040', fg='#ffffff', font=('Consolas', 9),
                         relief=tk.FLAT, padx=8, pady=4).pack(fill=tk.X, padx=3, pady=2)
        
        cmd_area.grid_columnconfigure(0, weight=1)
        cmd_area.grid_columnconfigure(1, weight=1)
        
        # Custom command
        custom_frame = tk.Frame(cmd_area, bg='#2d2d2d')
        custom_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        tk.Label(custom_frame, text="Custom:", bg='#2d2d2d', fg='#ffffff',
                font=('Consolas', 9)).pack(side=tk.LEFT, padx=5)
        
        self.custom_cmd_entry = tk.Entry(custom_frame, bg='#404040', fg='#ffffff',
                                         font=('Consolas', 10), insertbackground='white')
        self.custom_cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.custom_cmd_entry.bind('<Return>', lambda e: self.send_custom_command())
        
        tk.Button(custom_frame, text="Send", command=self.send_custom_command,
                 bg='#00aa00', fg='#ffffff', font=('Consolas', 9),
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        
    def create_console_panel(self, parent):
        """Console panel"""
        console_frame = tk.Frame(parent, bg='#2d2d2d')
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Header
        header = tk.Frame(console_frame, bg='#3d3d3d', height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📝 Console", bg='#3d3d3d', fg='#ffffff',
                font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Button(header, text="Clear", command=self.clear_console,
                 bg='#404040', fg='#ffffff', font=('Consolas', 8),
                 relief=tk.FLAT, padx=8, pady=2).pack(side=tk.RIGHT, padx=5)
        
        # Console text
        self.console = scrolledtext.ScrolledText(console_frame, bg='#1a1a1a', fg='#00ff00',
                                                 font=('Consolas', 9), height=8,
                                                 insertbackground='white')
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log("GUI started - Monitoring server at {}:{}".format(
            self.server_host, self.server_port))
        
    def log(self, message):
        """Console'ga log yozish"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        
    def clear_console(self):
        """Console'ni tozalash"""
        self.console.delete(1.0, tk.END)
        
    def start_refresh_thread(self):
        """Auto-refresh thread"""
        def refresh_loop():
            while True:
                self.refresh_agents_data()
                time.sleep(5)
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
        
    def refresh_agents_data(self):
        """Server'dan agent ma'lumotlarini olish"""
        # Bu yerda server API orqali agent ma'lumotlarini olish kerak
        # Hozircha mock data
        pass
        
    def manual_refresh(self):
        """Manual refresh"""
        self.log("Refreshing agents...")
        self.refresh_agents_data()
        
    def on_agent_select(self, event):
        """Agent tanlanganda"""
        selection = self.agents_tree.selection()
        if selection:
            agent_id = self.agents_tree.item(selection[0])['text']
            self.log(f"Selected agent: {agent_id}")
            
    def send_quick_command(self, command):
        """Quick command yuborish"""
        selection = self.agents_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Iltimos agent tanlang!")
            return
        
        agent_id = self.agents_tree.item(selection[0])['text']
        self.log(f"Sending command to {agent_id}: {command}")
        # Bu yerda server'ga komanda yuborish kerak
        
    def send_custom_command(self):
        """Custom command yuborish"""
        command = self.custom_cmd_entry.get().strip()
        if not command:
            return
        
        selection = self.agents_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Iltimos agent tanlang!")
            return
        
        agent_id = self.agents_tree.item(selection[0])['text']
        self.log(f"Sending to {agent_id}: {command}")
        self.custom_cmd_entry.delete(0, tk.END)
        # Bu yerda server'ga komanda yuborish kerak
        
    def remove_agent(self):
        """Agent'ni remove qilish"""
        selection = self.agents_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Iltimos agent tanlang!")
            return
        
        agent_id = self.agents_tree.item(selection[0])['text']
        if messagebox.askyesno("Confirm", f"Remove agent {agent_id}?"):
            self.log(f"Removing agent: {agent_id}")
            # Bu yerda server'ga remove command yuborish
            
    def kill_agent(self):
        """Agent'ni kill qilish"""
        selection = self.agents_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Iltimos agent tanlang!")
            return
        
        agent_id = self.agents_tree.item(selection[0])['text']
        if messagebox.askyesno("Confirm", f"Kill agent {agent_id}? (qayta ulanmaydi)"):
            self.log(f"Killing agent: {agent_id}")
            # Bu yerda server'ga kill command yuborish
            
    def show_agent_context_menu(self, event):
        """Agent context menu"""
        # Context menu implementatsiyasi
        pass
        
    def show_commands(self):
        """Barcha commandlarni ko'rsatish"""
        messagebox.showinfo("Commands", 
            "Available Commands:\n\n"
            "System: sysinfo, screenshot\n"
            "Camera: camera_photo, camera_list\n"
            "Audio: audio_record <sec>, mic_record <sec>\n"
            "Location: location_gps, location_info\n"
            "SMS: sms_list, sms_send <number> <text>\n"
            "Files: file_list <path>, file_download <path>"
        )
        
    def run(self):
        """GUI'ni ishga tushirish"""
        self.root.mainloop()


def main():
    """Main funksiya"""
    print("🎯 C2 TCP Server GUI")
    print("=" * 50)
    print("⚠️  Server'ni alohida terminalda ishga tushiring:")
    print("   python server/tcp_server.py --no-cli")
    print("=" * 50)
    
    app = TCPServerGUI()
    app.run()


if __name__ == '__main__':
    main()
