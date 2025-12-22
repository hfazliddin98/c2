"""
File Browser Module - Alohida fayl boshqaruvi
Xatolarni osongina topish uchun
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime


class FileBrowser:
    """Fayl brauzeri - upload, download, delete"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.file_tree = None
        self.path_entry = None
        
    def show_browser(self):
        """File browser oynasini ochish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("📂 File Browser")
            window.geometry("900x600")
            window.configure(bg='#1e1e1e')
            
            # Toolbar
            self._create_toolbar(window)
            
            # File list
            self._create_file_list(window)
            
            # Status
            tk.Label(
                window,
                text="📂 Demo fayllar - Real fayllar agent'dan yuklanadi",
                bg='#1e1e1e',
                fg='#888888',
                font=('Consolas', 9)
            ).pack(pady=5)
            
            # Load demo files
            self.load_demo_files()
            
            self.log("📂 File browser ochildi")
            
        except Exception as e:
            self.log(f"❌ Browser xatosi: {e}")
            messagebox.showerror("Xato", f"File browser xatosi:\n{e}")
            
    def _create_toolbar(self, window):
        """Toolbar yaratish"""
        toolbar = tk.Frame(window, bg='#2d2d2d')
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            toolbar,
            text="📂 File Browser",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        # Path entry
        tk.Label(toolbar, text="Path:", bg='#2d2d2d', fg='#ffffff').pack(side=tk.LEFT, padx=5)
        
        self.path_entry = tk.Entry(
            toolbar,
            font=('Consolas', 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            width=40
        )
        self.path_entry.insert(0, "C:\\")
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        tk.Button(
            toolbar,
            text="📂 Browse",
            command=self.browse_path,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="⬆️ Upload",
            command=self.upload_file,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="⬇️ Download",
            command=self.download_file,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🗑️ Delete",
            command=self.delete_file,
            bg='#2d2d2d',
            fg='#ff0000',
            font=('Consolas', 9)
        ).pack(side=tk.LEFT, padx=5)
        
    def _create_file_list(self, window):
        """Fayl ro'yxati yaratish"""
        list_frame = tk.Frame(window, bg='#1e1e1e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('Name', 'Type', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=200)
            
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
    def browse_path(self):
        """Path bo'yicha ko'rish (thread bilan)"""
        def browse_thread():
            path = self.path_entry.get()
            self.log(f"📂 Browsing: {path}")
            time.sleep(0.3)  # Simulate loading
            self.load_demo_files()
            
        thread = threading.Thread(target=browse_thread, daemon=True)
        thread.start()
        
    def upload_file(self):
        """Fayl yuklash (thread bilan)"""
        def upload_thread():
            filename = filedialog.askopenfilename(
                title="Agent'ga yuklash uchun fayl tanlang"
            )
            if filename:
                self.log(f"⬆️ Uploading: {filename}")
                time.sleep(0.5)  # Simulate upload
                messagebox.showinfo(
                    "Upload",
                    f"✅ Agent'ga yuklandi:\n{filename}\n\n(Demo rejimda)"
                )
                
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
        
    def download_file(self):
        """Fayl yuklab olish (thread bilan)"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Fayl tanlang!")
            return
            
        def download_thread():
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            
            self.log(f"⬇️ Downloading: {filename}")
            time.sleep(0.5)  # Simulate download
            
            # Save dialog
            save_path = filedialog.asksaveasfilename(
                defaultextension="",
                initialfile=filename.replace("📁 ", "").replace("📄 ", "").replace("📷 ", "").replace("📦 ", ""),
                title=f"Saqlash: {filename}"
            )
            
            if save_path:
                self.log(f"💾 Saqlandi: {save_path}")
                messagebox.showinfo(
                    "Download",
                    f"✅ Yuklab olindi:\n{save_path}\n\n(Demo rejimda)"
                )
                
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
    def delete_file(self):
        """Fayl o'chirish"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Fayl tanlang!")
            return
            
        item = self.file_tree.item(selection[0])
        filename = item['values'][0]
        
        if messagebox.askyesno("Tasdiqlash", f"O'chirilsinmi?\n{filename}"):
            self.log(f"🗑️ Deleting: {filename}")
            self.file_tree.delete(selection[0])
            messagebox.showinfo("Deleted", f"O'chirildi:\n{filename}")
            
    def load_demo_files(self):
        """Demo fayllarni yuklash"""
        # Clear existing
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Add demo files
        demo_files = [
            ("📁 Desktop", "Folder", "-", "2025-12-22"),
            ("📁 Documents", "Folder", "-", "2025-12-22"),
            ("📁 Downloads", "Folder", "-", "2025-12-22"),
            ("📄 config.txt", "Text", "2.5 KB", "2025-12-22 10:30"),
            ("📄 passwords.txt", "Text", "1.2 KB", "2025-12-22 11:15"),
            ("📷 screenshot.png", "Image", "156 KB", "2025-12-22 12:00"),
            ("📦 payload.exe", "Executable", "45 KB", "2025-12-22 13:45"),
            ("📄 log.txt", "Text", "8.9 KB", "2025-12-22 14:20"),
        ]
        
        for file_data in demo_files:
            self.file_tree.insert('', tk.END, values=file_data)
            
        self.log("📂 Demo fayllar yuklandi")
