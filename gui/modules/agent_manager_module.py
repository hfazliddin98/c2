"""
Agent Manager Module - Agent boshqaruvi
Xatolarni osongina topish uchun
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class AgentManager:
    """Agent ro'yxati va boshqaruvi"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.agents = {}
        
    def show_agents(self):
        """Agent ro'yxatini ko'rsatish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("📱 Ulangan Agentlar")
            window.geometry("900x500")
            window.configure(bg='#1e1e1e')
            
            # Title
            tk.Label(
                window,
                text="📱 Ulangan Agentlar",
                bg='#1e1e1e',
                fg='#00ff00',
                font=('Consolas', 16, 'bold')
            ).pack(pady=10)
            
            # Agent list
            self._create_agent_list(window)
            
            # Buttons
            self._create_buttons(window)
            
            # Status
            tk.Label(
                window,
                text="📊 TCP Server orqali ulangan agentlar",
                bg='#1e1e1e',
                fg='#888888',
                font=('Consolas', 9)
            ).pack(pady=10)
            
            self.log("📱 Agent ro'yxati ochildi")
            
        except Exception as e:
            self.log(f"❌ Agent manager xatosi: {e}")
            messagebox.showerror("Xato", f"Agent manager xatosi:\n{e}")
            
    def _create_agent_list(self, window):
        """Agent ro'yxati yaratish"""
        tree_frame = tk.Frame(window, bg='#1e1e1e')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('ID', 'IP', 'OS', 'Status', 'Last Seen')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Demo data
        tree.insert('', tk.END, values=(
            '001',
            '192.168.1.100',
            'Windows 10',
            '🟢 Active',
            datetime.now().strftime("%H:%M:%S")
        ))
        
        tree.insert('', tk.END, values=(
            '002',
            '192.168.1.101',
            'Ubuntu 22.04',
            '🟢 Active',
            datetime.now().strftime("%H:%M:%S")
        ))
        
        self.tree = tree
        
    def _create_buttons(self, window):
        """Tugmalar yaratish"""
        button_frame = tk.Frame(window, bg='#1e1e1e')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="🔄 Yangilash",
            command=self._refresh_agents,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📝 Komanda Yuborish",
            command=self._send_command,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ Agent O'chirish",
            command=self._delete_agent,
            bg='#2d2d2d',
            fg='#ff0000',
            font=('Consolas', 10),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
    def _refresh_agents(self):
        """Agentlarni yangilash"""
        self.log("🔄 Agent ro'yxati yangilanmoqda...")
        messagebox.showinfo("Yangilash", "Agent ro'yxati yangilandi!")
        
    def _send_command(self):
        """Tanlangan agentga komanda yuborish"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Agent tanlang!")
            return
            
        item = self.tree.item(selection[0])
        agent_id = item['values'][0]
        
        self.log(f"📝 Agent {agent_id}ga komanda yuborilmoqda...")
        messagebox.showinfo("Komanda", f"Agent {agent_id}ga komanda yuborish oynasi")
        
    def _delete_agent(self):
        """Agentni o'chirish"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Agent tanlang!")
            return
            
        item = self.tree.item(selection[0])
        agent_id = item['values'][0]
        
        if messagebox.askyesno("Tasdiqlash", f"Agent {agent_id} o'chirilsinmi?"):
            self.tree.delete(selection[0])
            self.log(f"🗑️ Agent {agent_id} o'chirildi")
