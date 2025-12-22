"""
Camera Module - Webcam boshqaruvi
Kameradan rasm va video olish
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import os


class CameraViewer:
    """Webcam viewer va recorder"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.camera = None
        self.recording = False
        self.camera_active = False
        
    def show_viewer(self):
        """Kamera viewer oynasini ochish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("📷 Camera Viewer")
            window.geometry("900x700")
            window.configure(bg='#1e1e1e')
            
            # Top controls
            self._create_controls(window)
            
            # Camera display
            self.canvas = self._create_display(window)
            
            # Status
            self.status_label = tk.Label(
                window,
                text="📷 Kamera faol emas",
                bg='#1e1e1e',
                fg='#ff0000',
                font=('Consolas', 10, 'bold')
            )
            self.status_label.pack(pady=5)
            
            self.log("📷 Camera viewer ochildi")
            
        except Exception as e:
            self.log(f"❌ Camera viewer xatosi: {e}")
            messagebox.showerror("Xato", f"Camera viewer xatosi:\n{e}")
            
    def _create_controls(self, window):
        """Boshqaruv paneli"""
        control_frame = tk.Frame(window, bg='#2d2d2d')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            control_frame,
            text="📷 Camera Control",
            font=('Consolas', 14, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00'
        ).pack(side=tk.LEFT, padx=10)
        
        # Camera control buttons
        tk.Button(
            control_frame,
            text="▶️ Kamerani Yoqish",
            command=self.start_camera,
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="⏸️ To'xtatish",
            command=self.stop_camera,
            bg='#ff9900',
            fg='#000000',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="📸 Rasm Olish",
            command=self.capture_photo,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🎥 Video Yozish",
            command=self.start_recording,
            bg='#ff0000',
            fg='#ffffff',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="⏹️ Yozishni To'xtatish",
            command=self.stop_recording,
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
    def _create_display(self, window):
        """Display area yaratish"""
        display_frame = tk.Frame(window, bg='#2d2d2d', relief=tk.SUNKEN, bd=2)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(
            display_frame,
            bg='#2d2d2d',
            highlightthickness=0,
            width=640,
            height=480
        )
        canvas.pack(expand=True)
        
        # Info text
        canvas.create_text(
            320, 240,
            text="📷 Kamerani yoqish uchun '▶️ Kamerani Yoqish' bosing",
            fill='#888888',
            font=('Consolas', 12)
        )
        
        return canvas
        
    def start_camera(self):
        """Kamerani yoqish"""
        def camera_thread():
            try:
                self.log("📷 Kamera yoqilmoqda...")
                
                # OpenCV import
                try:
                    import cv2
                    from PIL import Image, ImageTk
                    
                    # Camera ochish
                    self.camera = cv2.VideoCapture(0)
                    
                    if not self.camera.isOpened():
                        raise Exception("Kamera ochilmadi! Webcam tekshiring.")
                    
                    self.camera_active = True
                    self.log("✅ Kamera yoqildi!")
                    self.status_label.config(
                        text="📷 Kamera faol - Stream boshlanmoqda...",
                        fg='#00ff00'
                    )
                    
                    # Camera stream
                    while self.camera_active:
                        ret, frame = self.camera.read()
                        
                        if ret:
                            # Convert BGR to RGB
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            
                            # Resize to fit canvas
                            frame_resized = cv2.resize(frame_rgb, (640, 480))
                            
                            # Convert to PIL Image
                            img = Image.fromarray(frame_resized)
                            photo = ImageTk.PhotoImage(img)
                            
                            # Update canvas
                            self.canvas.delete("all")
                            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                            self.canvas.image = photo  # Keep reference
                            
                        time.sleep(0.03)  # ~30 FPS
                        
                    # Release camera
                    self.camera.release()
                    self.log("📷 Kamera to'xtatildi")
                    
                except ImportError:
                    self.log("❌ OpenCV o'rnatilmagan!")
                    messagebox.showerror(
                        "Xato",
                        "OpenCV kutubxonasi kerak!\n\nO'rnatish:\npip install opencv-python"
                    )
                except Exception as e:
                    self.log(f"❌ Kamera xatosi: {e}")
                    messagebox.showerror("Kamera Xatosi", str(e))
                    
            except Exception as e:
                self.log(f"❌ Camera thread xatosi: {e}")
        
        thread = threading.Thread(target=camera_thread, daemon=True)
        thread.start()
        
    def stop_camera(self):
        """Kamerani to'xtatish"""
        self.camera_active = False
        self.status_label.config(
            text="📷 Kamera faol emas",
            fg='#ff0000'
        )
        self.log("⏸️ Kamera to'xtatildi")
        
    def capture_photo(self):
        """Rasm olish"""
        if not self.camera_active:
            messagebox.showwarning("Ogohlantirish", "Avval kamerani yoqing!")
            return
            
        def capture_thread():
            try:
                import cv2
                
                ret, frame = self.camera.read()
                
                if ret:
                    # Save dialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".jpg",
                        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
                        initialfile=f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    
                    if filename:
                        cv2.imwrite(filename, frame)
                        self.log(f"📸 Rasm saqlandi: {filename}")
                        messagebox.showinfo("Saqlandi", f"Rasm saqlandi:\n{filename}")
                else:
                    self.log("❌ Frame olinmadi")
                    
            except Exception as e:
                self.log(f"❌ Capture xatosi: {e}")
                messagebox.showerror("Xato", str(e))
        
        thread = threading.Thread(target=capture_thread, daemon=True)
        thread.start()
        
    def start_recording(self):
        """Video yozishni boshlash"""
        if not self.camera_active:
            messagebox.showwarning("Ogohlantirish", "Avval kamerani yoqing!")
            return
            
        if self.recording:
            messagebox.showwarning("Ogohlantirish", "Video allaqachon yozilmoqda!")
            return
            
        def record_thread():
            try:
                import cv2
                
                # Video fayl nomi
                filename = filedialog.asksaveasfilename(
                    defaultextension=".avi",
                    filetypes=[("AVI files", "*.avi"), ("MP4 files", "*.mp4"), ("All files", "*.*")],
                    initialfile=f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                )
                
                if not filename:
                    return
                    
                # Video writer
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
                
                self.recording = True
                self.status_label.config(
                    text="🎥 Video yozilmoqda...",
                    fg='#ff0000'
                )
                self.log(f"🎥 Video yozish boshlandi: {filename}")
                
                while self.recording and self.camera_active:
                    ret, frame = self.camera.read()
                    
                    if ret:
                        frame_resized = cv2.resize(frame, (640, 480))
                        out.write(frame_resized)
                        
                    time.sleep(0.05)  # 20 FPS
                    
                # Release writer
                out.release()
                self.log(f"✅ Video saqlandi: {filename}")
                messagebox.showinfo("Saqlandi", f"Video saqlandi:\n{filename}")
                
                self.status_label.config(
                    text="📷 Kamera faol",
                    fg='#00ff00'
                )
                
            except Exception as e:
                self.log(f"❌ Recording xatosi: {e}")
                messagebox.showerror("Xato", str(e))
                self.recording = False
        
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
        
    def stop_recording(self):
        """Video yozishni to'xtatish"""
        if not self.recording:
            messagebox.showwarning("Ogohlantirish", "Video yozilmayapti!")
            return
            
        self.recording = False
        self.log("⏹️ Video yozish to'xtatildi")
