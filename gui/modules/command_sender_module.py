"""
Command Sender Module - Komanda yuborish
Xatolarni osongina topish uchun
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime


class CommandSender:
    """Komanda yuborish moduli"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        
    def show_dialog(self):
        """Komanda yuborish dialogini ochish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("📝 Komanda Yuborish")
            window.geometry("600x400")
            window.configure(bg='#1e1e1e')
            
            # Title
            tk.Label(
                window,
                text="📝 Agent'ga Komanda Yuborish",
                bg='#1e1e1e',
                fg='#00ff00',
                font=('Consolas', 14, 'bold')
            ).pack(pady=10)
            
            # Command input
            tk.Label(
                window,
                text="Komandani kiriting:",
                bg='#1e1e1e',
                fg='#ffffff',
                font=('Consolas', 10)
            ).pack(pady=5)
            
            cmd_text = scrolledtext.ScrolledText(
                window,
                height=10,
                bg='#2d2d2d',
                fg='#00ff00',
                font=('Consolas', 10),
                insertbackground='#00ff00'
            )
            cmd_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            
            # Pre-fill with example
            cmd_text.insert('1.0', "# Misol komandalar:\nsysinfo\ndir C:\\\nping google.com")
            
            # Buttons
            button_frame = tk.Frame(window, bg='#1e1e1e')
            button_frame.pack(pady=10)
            
            tk.Button(
                button_frame,
                text="📤 Yuborish",
                command=lambda: self._send_command(cmd_text.get('1.0', tk.END).strip(), window),
                bg='#2d2d2d',
                fg='#00ff00',
                font=('Consolas', 11, 'bold'),
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame,
                text="❌ Bekor qilish",
                command=window.destroy,
                bg='#2d2d2d',
                fg='#ff0000',
                font=('Consolas', 11),
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            self.log("📝 Komanda yuborish dialogi ochildi")
            
        except Exception as e:
            self.log(f"❌ Command sender xatosi: {e}")
            messagebox.showerror("Xato", f"Command sender xatosi:\n{e}")
            
    def _send_command(self, command, window):
        """Komandani yuborish (thread bilan)"""
        if not command.strip():
            messagebox.showwarning("Ogohlantirish", "Komanda kiriting!")
            return
            
        def send_thread():
            try:
                self.log(f"📤 Komanda yuborilmoqda: {command[:50]}...")
                time.sleep(0.5)  # Simulate sending
                
                self.log(f"✅ Komanda yuborildi!")
                messagebox.showinfo(
                    "Yuborildi",
                    f"✅ Komanda agent'ga yuborildi:\n\n{command[:100]}...\n\n(Demo rejimda)"
                )
                window.destroy()
                
            except Exception as e:
                self.log(f"❌ Yuborish xatosi: {e}")
                messagebox.showerror("Xato", str(e))
        
        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()
