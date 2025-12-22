"""
Screenshot Module - Alohida screenshot funksiyalari
Xatolarni osongina topish uchun
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import threading
import time
from datetime import datetime


class ScreenshotViewer:
    """Screenshot ko'rish va saqlash"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.current_image = None
        
    def show_viewer(self):
        """Screenshot viewer oynasini ochish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("🖼️ Screenshot Viewer")
            window.geometry("900x700")
            window.configure(bg='#1e1e1e')
            
            # Top controls
            self._create_controls(window)
            
            # Display area
            self.canvas = self._create_display(window)
            
            # Load demo
            self._load_demo_screenshot()
            
            self.log("🖼️ Screenshot viewer ochildi")
            
        except Exception as e:
            self.log(f"❌ Viewer xatosi: {e}")
            messagebox.showerror("Xato", f"Screenshot viewer xatosi:\n{e}")
            
    def _create_controls(self, window):
        """Boshqaruv paneli"""
        control_frame = ttk.Frame(window)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            control_frame,
            text="🖼️ Screenshot Viewer",
            font=('Consolas', 14, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            control_frame,
            text="📸 Yangi Screenshot",
            command=self.capture_screenshot,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="💾 Saqlash",
            command=self.save_screenshot,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🔄 Yangilash",
            command=self._load_demo_screenshot,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
    def _create_display(self, window):
        """Display area yaratish"""
        display_frame = tk.Frame(window, bg='#2d2d2d', relief=tk.SUNKEN, bd=2)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(display_frame, bg='#2d2d2d', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        return canvas
        
    def capture_screenshot(self):
        """Screenshot olish (thread bilan)"""
        def capture_thread():
            try:
                self.log("📸 Screenshot olinmoqda...")
                time.sleep(0.5)  # Simulate network delay
                
                # Demo screenshot yaratish
                self._load_demo_screenshot()
                
                self.log("✅ Screenshot olindi!")
                messagebox.showinfo(
                    "Muvaffaqiyat",
                    "Screenshot olindi!\n\n(Demo rejimda)"
                )
                
            except Exception as e:
                self.log(f"❌ Screenshot xatosi: {e}")
                messagebox.showerror("Xato", str(e))
        
        thread = threading.Thread(target=capture_thread, daemon=True)
        thread.start()
        
    def save_screenshot(self):
        """Screenshot saqlash (thread bilan)"""
        def save_thread():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialfile=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                
                if filename:
                    # Create demo screenshot
                    img = Image.new('RGB', (800, 600), color='#2d2d2d')
                    draw = ImageDraw.Draw(img)
                    draw.rectangle([50, 50, 750, 550], outline='#00ff00', width=3)
                    draw.text((250, 280), "DEMO SCREENSHOT", fill='#00ff00')
                    draw.text((200, 320), f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='#888888')
                    img.save(filename)
                    
                    self.log(f"💾 Screenshot saqlandi: {filename}")
                    messagebox.showinfo("Saqlandi", f"Screenshot saqlandi:\n{filename}")
                    
            except Exception as e:
                self.log(f"❌ Saqlash xatosi: {e}")
                messagebox.showerror("Xato", f"Saqlash xatosi:\n{e}")
        
        thread = threading.Thread(target=save_thread, daemon=True)
        thread.start()
        
    def _load_demo_screenshot(self):
        """Demo screenshot yuklash"""
        try:
            # Create demo image
            img = Image.new('RGB', (800, 600), color='#2d2d2d')
            draw = ImageDraw.Draw(img)
            
            # Draw demo content
            draw.rectangle([50, 50, 750, 550], outline='#00ff00', width=3)
            draw.text((280, 250), "SCREENSHOT DEMO", fill='#00ff00', font=None)
            draw.text((220, 300), "Real screenshot agent'dan olinadi", fill='#888888')
            draw.text((180, 350), "Agent ulanganda real ekran ko'rsatiladi", fill='#888888')
            
            # Convert to PhotoImage
            self.current_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            
            self.log("🖼️ Demo screenshot yuklandi")
            
        except Exception as e:
            self.log(f"❌ Screenshot yuklash xatosi: {e}")
