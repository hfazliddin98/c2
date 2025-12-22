"""
Havoc-Style C2 Framework GUI - Standalone Version
TCP server bilan to'g'ridan-to'g'ri ishlaydi (Django serversiz)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import socket
import json
import time
from datetime import datetime
import sys
import os


class SimpleHavocGUI:
    """Soddalashtirilgan Havoc-style GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Havoc C2 Platform - Ta'lim Maqsadida")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # TCP Server connection
        self.tcp_host = "127.0.0.1"
        self.tcp_port = 9999
        self.connected = False
        self.tcp_socket = None
        
        # Data
        self.agents = {}
        self.selected_agent = None
        
        self.setup_styles()
        self.create_main_interface()
        self.log_message("GUI ishga tushdi")
        
    def setup_styles(self):
        """Dark theme setup"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Dark.TFrame', background='#1e1e1e')
        style.configure('Dark.TLabel', background='#1e1e1e', foreground='#00ff00')
        style.configure('Dark.TButton', 
                       background='#2d2d2d',
                       foreground='#00ff00',
                       borderwidth=1,
                       focuscolor='none')
        style.map('Dark.TButton',
                 background=[('active', '#3d3d3d')])
        
    def create_main_interface(self):
        """Asosiy interfeys yaratish"""
        # Top panel - Connection status
        top_frame = ttk.Frame(self.root, style='Dark.TFrame')
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(
            top_frame,
            text="⚪ TCP Server: Ulanmagan",
            style='Dark.TLabel',
            font=('Consolas', 12, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        connect_btn = ttk.Button(
            top_frame,
            text="🔌 TCP Serverga Ulaning",
            command=self.connect_to_tcp,
            style='Dark.TButton'
        )
        connect_btn.pack(side=tk.LEFT, padx=10)
        
        disconnect_btn = ttk.Button(
            top_frame,
            text="🔴 Uzish",
            command=self.disconnect_from_tcp,
            style='Dark.TButton'
        )
        disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Actions
        left_panel = ttk.Frame(main_frame, style='Dark.TFrame', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(
            left_panel,
            text="📊 Aksiyalar",
            style='Dark.TLabel',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        # Action buttons
        actions = [
            ("📱 Agentlarni Ko'rish", self.show_agents),
            ("🛠️ Payload Generatori", self.open_payload_generator),
            ("🔊 TCP Server Status", self.check_tcp_status),
            ("📝 Komanda Yuborish", self.send_command_dialog),
            ("🖼️ Screenshot Olish", self.take_screenshot),
            ("📂 Fayllar", self.file_browser),
        ]
        
        for text, command in actions:
            btn = ttk.Button(
                left_panel,
                text=text,
                command=command,
                style='Dark.TButton',
                width=30
            )
            btn.pack(pady=5, padx=10, fill=tk.X)
        
        # Right panel - Logs
        right_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(
            right_panel,
            text="📋 Loglar",
            style='Dark.TLabel',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10),
            insertbackground='#00ff00'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def log_message(self, message):
        """Log xabarlarini ko'rsatish"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def connect_to_tcp(self):
        """TCP serverga ulanish"""
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.tcp_host, self.tcp_port))
            self.connected = True
            self.status_label.config(
                text=f"🟢 TCP Server: Ulangan ({self.tcp_host}:{self.tcp_port})"
            )
            self.log_message(f"✅ TCP Serverga ulandingiz: {self.tcp_host}:{self.tcp_port}")
            messagebox.showinfo(
                "Muvaffaqiyat",
                f"TCP Serverga ulandi!\n{self.tcp_host}:{self.tcp_port}"
            )
        except Exception as e:
            self.log_message(f"❌ TCP Server ulanish xatosi: {e}")
            messagebox.showerror(
                "Xato",
                f"TCP Serverga ulanib bo'lmadi:\n{e}\n\nTCP server ishga tushganini tekshiring:\npython server/tcp_server.py"
            )
            
    def disconnect_from_tcp(self):
        """TCP serverdan uzilish"""
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass
        self.connected = False
        self.tcp_socket = None
        self.status_label.config(text="⚪ TCP Server: Ulanmagan")
        self.log_message("❌ TCP Serverdan uzildingiz")
        
    def show_agents(self):
        """Agent ro'yxatini ko'rsatish"""
        if not self.connected:
            messagebox.showwarning(
                "Ogohlantirish",
                "Avval TCP Serverga ulaning!"
            )
            return
            
        # Agents window
        agents_window = tk.Toplevel(self.root)
        agents_window.title("📱 Ulangan Agentlar")
        agents_window.geometry("800x500")
        agents_window.configure(bg='#1e1e1e')
        
        # Agent list
        tree_frame = ttk.Frame(agents_window, style='Dark.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'IP', 'OS', 'Status', 'Last Seen'),
            show='headings'
        )
        
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Sample data
        tree.insert('', tk.END, values=(
            '001', '192.168.1.100', 'Windows 10', 'Active', datetime.now().strftime("%H:%M:%S")
        ))
        
        ttk.Label(
            agents_window,
            text="📊 TCP Server orqali ulangan agentlar",
            style='Dark.TLabel'
        ).pack(pady=10)
        
    def open_payload_generator(self):
        """Payload generatorni ochish"""
        self.log_message("🛠️ Payload Generator ochilmoqda...")
        import subprocess
        subprocess.Popen([sys.executable, "gui/payload_generator_gui.py"])
        
    def check_tcp_status(self):
        """TCP server statusini tekshirish"""
        if self.connected:
            status = f"🟢 Ulangan\nHost: {self.tcp_host}\nPort: {self.tcp_port}"
            self.log_message("✅ TCP Server faol")
        else:
            status = "🔴 Ulanmagan\n\nTCP Serverni ishga tushiring:\npython server/tcp_server.py"
            self.log_message("⚠️ TCP Server faol emas")
            
        messagebox.showinfo("TCP Server Status", status)
        
    def send_command_dialog(self):
        """Komanda yuborish dialogi"""
        if not self.connected:
            messagebox.showwarning("Ogohlantirish", "TCP Serverga ulaning!")
            return
            
        cmd_window = tk.Toplevel(self.root)
        cmd_window.title("📝 Komanda Yuborish")
        cmd_window.geometry("500x300")
        cmd_window.configure(bg='#1e1e1e')
        
        ttk.Label(
            cmd_window,
            text="Komandani kiriting:",
            style='Dark.TLabel'
        ).pack(pady=10)
        
        cmd_entry = tk.Text(cmd_window, height=10, bg='#2d2d2d', fg='#00ff00')
        cmd_entry.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        def send_cmd():
            command = cmd_entry.get('1.0', tk.END).strip()
            if command:
                self.log_message(f"📤 Komanda yuborildi: {command}")
                messagebox.showinfo("Yuborildi", f"Komanda yuborildi:\n{command}")
                cmd_window.destroy()
                
        ttk.Button(
            cmd_window,
            text="📤 Yuborish",
            command=send_cmd,
            style='Dark.TButton'
        ).pack(pady=10)
        
    def take_screenshot(self):
        """Screenshot olish va ko'rsatish"""
        if not self.connected:
            messagebox.showwarning("Ogohlantirish", "TCP Serverga ulaning!")
            return
            
        # Screenshot window
        screenshot_window = tk.Toplevel(self.root)
        screenshot_window.title("🖼️ Screenshot Viewer")
        screenshot_window.geometry("900x700")
        screenshot_window.configure(bg='#1e1e1e')
        
        # Top controls
        control_frame = ttk.Frame(screenshot_window, style='Dark.TFrame')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            control_frame,
            text="🖼️ Screenshot Viewer",
            style='Dark.TLabel',
            font=('Consolas', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            control_frame,
            text="📸 Yangi Screenshot",
            command=lambda: self._capture_screenshot(screenshot_window),
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="💾 Saqlash",
            command=lambda: self._save_screenshot(),
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🔄 Yangilash",
            command=lambda: self._refresh_screenshots(screenshot_window),
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Screenshot display area
        display_frame = tk.Frame(screenshot_window, bg='#2d2d2d', relief=tk.SUNKEN, bd=2)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for image
        canvas = tk.Canvas(display_frame, bg='#2d2d2d', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        info_label = ttk.Label(
            screenshot_window,
            text="📸 Screenshot funksiyasi - Demo rejim",
            style='Dark.TLabel'
        )
        info_label.pack(pady=5)
        
        # Demo screenshot
        self._load_demo_screenshot(canvas)
        self.log_message("🖼️ Screenshot viewer ochildi")
        
    def _capture_screenshot(self, window):
        """Screenshot olish"""
        self.log_message("📸 Screenshot olinmoqda...")
        
        # Threading bilan screenshot olish (GUI osilib qolmasligi uchun)
        def capture_thread():
            try:
                # Progress ko'rsatish
                self.root.after(0, lambda: self.log_message("⏳ Agent bilan bog'lanilmoqda..."))
                time.sleep(0.5)  # Simulate network delay
                
                self.root.after(0, lambda: self.log_message("📸 Screenshot olindi!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Muvaffaqiyat", 
                    "Screenshot olindi!\n\n(Demo rejimda - Real agent ulanganida real screenshot)"
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Screenshot xatosi: {e}"))
                self.root.after(0, lambda: messagebox.showerror("Xato", str(e)))
        
        # Thread ishga tushirish
        thread = threading.Thread(target=capture_thread, daemon=True)
        thread.start()
        
    def _save_screenshot(self):
        """Screenshot saqlash"""
        def save_thread():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialfile=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                if filename:
                    # Demo screenshot saqlash
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (800, 600), color='#2d2d2d')
                    draw = ImageDraw.Draw(img)
                    draw.rectangle([50, 50, 750, 550], outline='#00ff00', width=3)
                    draw.text((250, 280), "📸 DEMO SCREENSHOT", fill='#00ff00', font=None)
                    draw.text((200, 320), f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='#888888')
                    img.save(filename)
                    
                    self.root.after(0, lambda: self.log_message(f"💾 Screenshot saqlandi: {filename}"))
                    self.root.after(0, lambda: messagebox.showinfo("Saqlandi", f"Screenshot saqlandi:\n{filename}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Xato", f"Saqlash xatosi:\n{e}"))
        
        thread = threading.Thread(target=save_thread, daemon=True)
        thread.start()
            
    def _refresh_screenshots(self, window):
        """Screenshot yangilash"""
        self.log_message("🔄 Screenshot yangilanmoqda...")
        
    def _load_demo_screenshot(self, canvas):
        """Demo screenshot ko'rsatish"""
        try:
            # Create demo image with PIL if available
            try:
                from PIL import Image, ImageDraw, ImageFont, ImageTk
                
                # Create demo screenshot
                img = Image.new('RGB', (800, 600), color='#2d2d2d')
                draw = ImageDraw.Draw(img)
                
                # Draw demo content
                draw.rectangle([50, 50, 750, 550], outline='#00ff00', width=3)
                draw.text((300, 250), "📸 SCREENSHOT DEMO", fill='#00ff00')
                draw.text((250, 300), "Real screenshot agent'dan olinadi", fill='#888888')
                draw.text((200, 350), "Agent ulanganda real ekran ko'rsatiladi", fill='#888888')
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas.image = photo  # Keep reference
                canvas.config(scrollregion=canvas.bbox(tk.ALL))
                
            except ImportError:
                # Fallback without PIL
                canvas.create_rectangle(50, 50, 750, 550, outline='#00ff00', width=3)
                canvas.create_text(400, 300, text="📸 SCREENSHOT DEMO", fill='#00ff00', font=('Consolas', 20))
                canvas.create_text(400, 350, text="PIL kutubxonasi kerak: pip install pillow", fill='#ff0000')
                
        except Exception as e:
            canvas.create_text(400, 300, text=f"Screenshot xatosi: {e}", fill='#ff0000')
        
    def file_browser(self):
        """Fayl brauzeri - to'liq funksional"""
        if not self.connected:
            messagebox.showwarning("Ogohlantirish", "TCP Serverga ulaning!")
            return
            
        # File browser window
        browser_window = tk.Toplevel(self.root)
        browser_window.title("📂 File Browser")
        browser_window.geometry("900x600")
        browser_window.configure(bg='#1e1e1e')
        
        # Top toolbar
        toolbar = ttk.Frame(browser_window, style='Dark.TFrame')
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            toolbar,
            text="📂 File Browser",
            style='Dark.TLabel',
            font=('Consolas', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        # Path entry
        ttk.Label(toolbar, text="Path:", style='Dark.TLabel').pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(
            toolbar,
            text="📂 Browse",
            command=lambda: self._browse_path(browser_window),
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="⬆️ Upload",
            command=self._upload_file,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="⬇️ Download",
            command=self._download_file,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="🗑️ Delete",
            command=self._delete_file,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # File list
        list_frame = ttk.Frame(browser_window, style='Dark.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for files
        columns = ('Name', 'Type', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=200)
            
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        def browse_thread():
            path = self.path_entry.get()
            self.root.after(0, lambda: self.log_message(f"📂 Browsing: {path}"))
            time.sleep(0.3)  # Simulate loading
            self.root.after(0, self._load_demo_files)
            
        thread = threading.Thread(target=browse_thread, daemon=True)
        thread.start
        # Load demo files
        self._load_demo_files()
        
        # Status
        ttk.Label(
            browser_window,
            text="📂 Demo fayllar - Real fayllar agent'dan yuklanadi",
            style='Dark.TLabel'
        ).pack(pady=5)
        
        self.log_message("📂 File browser ochildi")
        
    def _browse_path(self, window):
        """Path bo'yicha ko'rish"""
        def browse_thread():
            path = self.path_entry.get()
            self.root.after(0, lambda: self.log_message(f"📂 Browsing: {path}"))
            time.sleep(0.3)  # Simulate loading
            self.root.after(0, self._load_demo_files)
            
        thread = threading.Thread(target=browse_thread, daemon=True)
        thread.start()
        
    def _upload_file(self):
        """Fayl yuklash"""
        def upload_thread():
            filename = filedialog.askopenfilename(
                title="Agent'ga yuklash uchun fayl tanlang"
            )
            if filename:
                self.root.after(0, lambda: self.log_message(f"⬆️ Uploading: {filename}"))
                time.sleep(0.5)  # Simulate upload
                self.root.after(0, lambda: messagebox.showinfo(
                    "Upload", 
                    f"✅ Agent'ga yuklandi:\n{filename}\n\n(Demo rejimda - Real agent ulanganida real upload)"
                ))
                
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
        
    def _download_file(self):
        """Fayl yuklab olish"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("Ogohlantirish", "Fayl tanlang!")
            return
            
        def download_thread():
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            
            self.root.after(0, lambda: self.log_message(f"⬇️ Downloading: {filename}"))
            time.sleep(0.5)  # Simulate download
            
            # Save dialog
            save_path = filedialog.asksaveasfilename(
                defaultextension="",
                initialfile=filename.replace("📁 ", "").replace("📄 ", "").replace("📷 ", "").replace("📦 ", ""),
                title=f"Saqlash: {filename}"
            )
            
            if save_path:
                self.root.after(0, lambda: self.log_message(f"💾 Saqlandi: {save_path}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Download", 
                    f"✅ Yuklab olindi:\n{save_path}\n\n(Demo rejimda - Real agent ulanganida real file)"
                ))
                
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        thread.start(
        filename = filedialog.askopenfilename()
        if filename:
            self.log_message(f"⬆️ Uploading: {filename}")
            messagebox.showinfo("Upload", f"Agent'ga yuklash:\n{filename}\n\n(Demo rejimda)")
            
    def _download_file(self):
        """Fayl yuklab olish"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            self.log_message(f"⬇️ Downloading: {filename}")
            messagebox.showinfo("Download", f"Agent'dan yuklab olish:\n{filename}\n\n(Demo rejimda)")
        else:
            messagebox.showwarning("Ogohlantirish", "Fayl tanlang!")
            
    def _delete_file(self):
        """Fayl o'chirish"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            
            if messagebox.askyesno("Tasdiqlash", f"O'chirilsinmi?\n{filename}"):
                self.log_message(f"🗑️ Deleting: {filename}")
                messagebox.showinfo("Deleted", f"O'chirildi:\n{filename}\n\n(Demo rejimda)")
        else:
            messagebox.showwarning("Ogohlantirish", "Fayl tanlang!")
            
    def _load_demo_files(self):
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
        
    def run(self):
        """GUI ni ishga tushirish"""
        self.root.mainloop()


def main():
    print("\n" + "="*60)
    print("🎯 Havoc-Style C2 GUI ishga tushmoqda...")
    print("="*60)
    print("\n📌 TCP Server manzili: 127.0.0.1:9999")
    print("📌 GUI'da 'TCP Serverga Ulaning' tugmasini bosing\n")
    
    app = SimpleHavocGUI()
    app.run()


if __name__ == "__main__":
    main()
