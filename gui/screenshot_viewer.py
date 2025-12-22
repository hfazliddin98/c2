"""
Screenshot Viewer - GUI'da screenshot ko'rsatish
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import base64
import io
import requests
from datetime import datetime


class ScreenshotViewer:
    """Screenshot ko'rsatish oynasi"""
    
    def __init__(self, parent, agent_id, server_url):
        self.parent = parent
        self.agent_id = agent_id
        self.server_url = server_url
        self.window = None
        self.screenshot_label = None
        self.last_screenshot = None
        
    def show(self):
        """Screenshot oynasini ko'rsatish"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Screenshot - {self.agent_id[:8]}")
        self.window.geometry("1024x768")
        self.window.configure(bg='#1e1e1e')
        
        # Toolbar
        toolbar = ttk.Frame(self.window, style='Dark.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="📸 Screenshot Olish", 
                  command=self.capture_screenshot, 
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="💾 Saqlash", 
                  command=self.save_screenshot, 
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="🔄 Yangilash", 
                  command=self.refresh_screenshot, 
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        # Quality control
        ttk.Label(toolbar, text="Sifat:", 
                 style='Dark.TLabel').pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.StringVar(value="85")
        quality_combo = ttk.Combobox(toolbar, textvariable=self.quality_var, 
                                     width=10, values=['50', '70', '85', '95', '100'])
        quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = ttk.Label(toolbar, text="Screenshot yo'q", 
                                   style='Dark.TLabel')
        self.info_label.pack(side=tk.RIGHT, padx=5)
        
        # Screenshot display area (scrollable)
        canvas_frame = ttk.Frame(self.window, style='Dark.TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='#2d2d2d', highlightthickness=0)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, 
                                   command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                   command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, 
                            yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Screenshot label on canvas
        self.screenshot_label = ttk.Label(self.canvas, style='Dark.TLabel')
        self.canvas_window = self.canvas.create_window(0, 0, anchor=tk.NW, 
                                                       window=self.screenshot_label)
        
        # Auto capture on open
        self.window.after(500, self.capture_screenshot)
    
    def capture_screenshot(self):
        """Screenshot olish"""
        try:
            self.info_label.config(text="📸 Screenshot olinmoqda...")
            self.window.update()
            
            quality = self.quality_var.get()
            response = requests.get(
                f"{self.server_url}/api/screenshot/{self.agent_id}?quality={quality}",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.info_label.config(text="⏳ Screenshot kutilmoqda...")
                    # Javobni kutish (polling yoki WebSocket)
                    self.window.after(2000, self.check_screenshot_result)
                else:
                    messagebox.showerror("Xato", result.get('message', 'Noma\'lum xato'))
                    self.info_label.config(text="❌ Xato")
            else:
                messagebox.showerror("Xato", f"Server xatosi: {response.status_code}")
                self.info_label.config(text="❌ Server xatosi")
                
        except Exception as e:
            messagebox.showerror("Xato", f"Screenshot olishda xato: {str(e)}")
            self.info_label.config(text="❌ Xato")
    
    def check_screenshot_result(self):
        """Screenshot natijasini tekshirish"""
        # Bu yerda agent'dan kelgan screenshot'ni olish kerak
        # Hozircha demo uchun placeholder
        self.info_label.config(text="⚠️ Screenshot agent'dan kelishi kutilmoqda")
        messagebox.showinfo("Info", 
                          "Screenshot so'rovi yuborildi. Agent javob berishi kerak.")
    
    def display_screenshot(self, screenshot_data):
        """Screenshot'ni ko'rsatish"""
        try:
            # Base64'dan image'ga
            image_data = base64.b64decode(screenshot_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Save original
            self.last_screenshot = image.copy()
            
            # Fit to window
            window_width = self.canvas.winfo_width()
            window_height = self.canvas.winfo_height()
            
            if window_width > 1 and window_height > 1:
                # Scale to fit
                image.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
            
            # Display
            photo = ImageTk.PhotoImage(image)
            self.screenshot_label.config(image=photo)
            self.screenshot_label.image = photo  # Keep reference
            
            # Update canvas scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Update info
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.info_label.config(
                text=f"✅ {image.width}x{image.height} - {timestamp}"
            )
            
        except Exception as e:
            messagebox.showerror("Xato", f"Screenshot ko'rsatishda xato: {str(e)}")
            self.info_label.config(text="❌ Ko'rsatish xatosi")
    
    def save_screenshot(self):
        """Screenshot'ni saqlash"""
        if not self.last_screenshot:
            messagebox.showwarning("Ogohlantirish", "Screenshot yo'q")
            return
        
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG fayl", "*.png"), ("JPEG fayl", "*.jpg"), 
                          ("Barcha fayllar", "*.*")]
            )
            
            if filename:
                self.last_screenshot.save(filename)
                messagebox.showinfo("Muvaffaqiyat", f"Screenshot saqlandi: {filename}")
                
        except Exception as e:
            messagebox.showerror("Xato", f"Saqlashda xato: {str(e)}")
    
    def refresh_screenshot(self):
        """Screenshot'ni yangilash"""
        self.capture_screenshot()
