"""
Audio Module - Ovoz yozish va mikrofon boshqaruvi
Mikrofondan ovoz yozib saqlash
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import wave
import time
from datetime import datetime
import os


class AudioRecorder:
    """Audio recording va playback"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.recording = False
        self.frames = []
        self.stream = None
        self.audio = None
        
    def show_recorder(self):
        """Audio recorder oynasini ochish"""
        try:
            # Window yaratish
            window = tk.Toplevel(self.parent)
            window.title("🎤 Audio Recorder")
            window.geometry("700x500")
            window.configure(bg='#1e1e1e')
            
            # Title
            tk.Label(
                window,
                text="🎤 Audio Recorder",
                bg='#1e1e1e',
                fg='#00ff00',
                font=('Consolas', 16, 'bold')
            ).pack(pady=15)
            
            # Controls
            self._create_controls(window)
            
            # Status display
            self._create_status_display(window)
            
            # Recording list
            self._create_recording_list(window)
            
            self.log("🎤 Audio recorder ochildi")
            
        except Exception as e:
            self.log(f"❌ Audio recorder xatosi: {e}")
            messagebox.showerror("Xato", f"Audio recorder xatosi:\n{e}")
            
    def _create_controls(self, window):
        """Boshqaruv tugmalari"""
        control_frame = tk.Frame(window, bg='#2d2d2d')
        control_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Record button
        self.record_btn = tk.Button(
            control_frame,
            text="🔴 Yozishni Boshlash",
            command=self.start_recording,
            bg='#ff0000',
            fg='#ffffff',
            font=('Consolas', 12, 'bold'),
            width=20,
            height=2
        )
        self.record_btn.pack(side=tk.LEFT, padx=10)
        
        # Stop button
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️ To'xtatish",
            command=self.stop_recording,
            bg='#555555',
            fg='#ffffff',
            font=('Consolas', 12, 'bold'),
            width=15,
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Save button
        tk.Button(
            control_frame,
            text="💾 Saqlash",
            command=self.save_recording,
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 11, 'bold'),
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
    def _create_status_display(self, window):
        """Status ko'rsatish"""
        status_frame = tk.Frame(window, bg='#2d2d2d', relief=tk.SUNKEN, bd=2)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="⚪ Tayyor - Yozishni boshlash uchun tugmani bosing",
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 11, 'bold')
        )
        self.status_label.pack(pady=15)
        
        # Timer
        self.timer_label = tk.Label(
            status_frame,
            text="⏱️ 00:00:00",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 18, 'bold')
        )
        self.timer_label.pack(pady=10)
        
        # Audio level indicator
        self.level_canvas = tk.Canvas(
            status_frame,
            bg='#1e1e1e',
            height=30,
            highlightthickness=0
        )
        self.level_canvas.pack(fill=tk.X, padx=20, pady=10)
        
    def _create_recording_list(self, window):
        """Yozilgan ovozlar ro'yxati"""
        list_frame = tk.Frame(window, bg='#1e1e1e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            list_frame,
            text="📼 Yozilgan Ovozlar",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 12, 'bold')
        ).pack(pady=5)
        
        # Listbox
        self.recording_list = tk.Listbox(
            list_frame,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10),
            selectbackground='#00ff00',
            selectforeground='#000000'
        )
        self.recording_list.pack(fill=tk.BOTH, expand=True)
        
    def start_recording(self):
        """Ovoz yozishni boshlash"""
        def record_thread():
            try:
                self.log("🎤 Ovoz yozish boshlanmoqda...")
                
                # PyAudio import
                try:
                    import pyaudio
                    
                    # Audio settings
                    CHUNK = 1024
                    FORMAT = pyaudio.paInt16
                    CHANNELS = 2
                    RATE = 44100
                    
                    self.audio = pyaudio.PyAudio()
                    
                    # Open stream
                    self.stream = self.audio.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK
                    )
                    
                    self.recording = True
                    self.frames = []
                    
                    # Update UI
                    self.record_btn.config(state=tk.DISABLED)
                    self.stop_btn.config(state=tk.NORMAL)
                    self.status_label.config(
                        text="🔴 YOZILMOQDA...",
                        fg='#ff0000'
                    )
                    
                    self.log("✅ Ovoz yozish boshlandi!")
                    
                    # Record
                    start_time = time.time()
                    while self.recording:
                        data = self.stream.read(CHUNK)
                        self.frames.append(data)
                        
                        # Update timer
                        elapsed = int(time.time() - start_time)
                        hours = elapsed // 3600
                        minutes = (elapsed % 3600) // 60
                        seconds = elapsed % 60
                        self.timer_label.config(
                            text=f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"
                        )
                        
                        # Update level indicator
                        self._update_audio_level(data)
                        
                    # Stop and close stream
                    self.stream.stop_stream()
                    self.stream.close()
                    self.audio.terminate()
                    
                    self.log(f"✅ Yozish to'xtatildi - {len(self.frames)} frames")
                    
                except ImportError:
                    self.log("❌ PyAudio o'rnatilmagan!")
                    messagebox.showerror(
                        "Xato",
                        "PyAudio kutubxonasi kerak!\n\nO'rnatish:\npip install pyaudio"
                    )
                    self.recording = False
                    self.record_btn.config(state=tk.NORMAL)
                    
                except Exception as e:
                    self.log(f"❌ Recording xatosi: {e}")
                    messagebox.showerror("Xato", f"Recording xatosi:\n{e}")
                    self.recording = False
                    self.record_btn.config(state=tk.NORMAL)
                    
            except Exception as e:
                self.log(f"❌ Record thread xatosi: {e}")
        
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
        
    def stop_recording(self):
        """Yozishni to'xtatish"""
        if not self.recording:
            return
            
        self.recording = False
        self.stop_btn.config(state=tk.DISABLED)
        self.record_btn.config(state=tk.NORMAL)
        self.status_label.config(
            text="⏹️ To'xtatildi - Saqlash uchun '💾 Saqlash' bosing",
            fg='#ffaa00'
        )
        self.log("⏹️ Ovoz yozish to'xtatildi")
        
    def save_recording(self):
        """Yozilgan ovozni saqlash"""
        if not self.frames:
            messagebox.showwarning("Ogohlantirish", "Avval ovoz yozing!")
            return
            
        def save_thread():
            try:
                # Save dialog
                filename = filedialog.asksaveasfilename(
                    defaultextension=".wav",
                    filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                    initialfile=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                )
                
                if filename:
                    import pyaudio
                    
                    # Save WAV file
                    wf = wave.open(filename, 'wb')
                    wf.setnchannels(2)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(44100)
                    wf.writeframes(b''.join(self.frames))
                    wf.close()
                    
                    self.log(f"💾 Ovoz saqlandi: {filename}")
                    
                    # Add to list
                    self.recording_list.insert(
                        tk.END,
                        f"📼 {os.path.basename(filename)} - {datetime.now().strftime('%H:%M:%S')}"
                    )
                    
                    messagebox.showinfo("Saqlandi", f"Ovoz saqlandi:\n{filename}")
                    
                    # Reset
                    self.frames = []
                    self.timer_label.config(text="⏱️ 00:00:00")
                    self.status_label.config(
                        text="⚪ Tayyor - Yozishni boshlash uchun tugmani bosing",
                        fg='#888888'
                    )
                    
            except Exception as e:
                self.log(f"❌ Saqlash xatosi: {e}")
                messagebox.showerror("Xato", f"Saqlash xatosi:\n{e}")
        
        thread = threading.Thread(target=save_thread, daemon=True)
        thread.start()
        
    def _update_audio_level(self, data):
        """Audio level indicator yangilash"""
        try:
            import struct
            
            # Calculate average amplitude
            count = len(data) // 2
            format_str = "%dh" % count
            shorts = struct.unpack(format_str, data)
            
            # Calculate level
            sum_squares = sum(abs(sample) for sample in shorts)
            amplitude = sum_squares / count if count > 0 else 0
            level = min(100, int(amplitude / 100))
            
            # Draw level bar
            self.level_canvas.delete("all")
            width = self.level_canvas.winfo_width()
            height = 30
            
            # Background
            self.level_canvas.create_rectangle(
                0, 0, width, height,
                fill='#1e1e1e',
                outline=''
            )
            
            # Level bar
            bar_width = int(width * level / 100)
            color = '#00ff00' if level < 70 else '#ffaa00' if level < 90 else '#ff0000'
            
            self.level_canvas.create_rectangle(
                0, 0, bar_width, height,
                fill=color,
                outline=''
            )
            
            # Text
            self.level_canvas.create_text(
                width // 2, height // 2,
                text=f"📊 Level: {level}%",
                fill='#ffffff',
                font=('Consolas', 10, 'bold')
            )
            
        except:
            pass
