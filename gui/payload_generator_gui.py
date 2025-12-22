"""
C2 Platform - Payload Generator GUI
Grafik interfeys orqali payload yaratish
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime

# Common modullarni import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.payload_generator import PayloadGenerator


class PayloadGeneratorGUI:
    """Payload Generator GUI klassi"""
    
    def __init__(self, parent=None):
        # Window yaratish
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("🛠️ Payload Generator")
        self.window.geometry("700x600")
        self.window.configure(bg='#1e1e1e')
        
        # Generator
        self.generator = None
        
        # UI yaratish
        self._create_ui()
        
    def _create_ui(self):
        """UI yaratish"""
        # Main container
        main_frame = tk.Frame(self.window, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="🛠️ Payload Generator",
            font=('Consolas', 18, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        title.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = tk.LabelFrame(
            main_frame,
            text="Configuration",
            font=('Consolas', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.GROOVE,
            bd=2
        )
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server settings
        server_frame = tk.Frame(config_frame, bg='#2d2d2d')
        server_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            server_frame,
            text="Server Host:",
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff'
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.host_entry = tk.Entry(
            server_frame,
            font=('Consolas', 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        self.host_entry.bind('<KeyRelease>', lambda e: self._update_connection_info())
        
        tk.Label(
            server_frame,
            text="Port:",
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff'
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.port_entry = tk.Entry(
            server_frame,
            font=('Consolas', 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.port_entry.insert(0, "8080")
        self.port_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        self.port_entry.bind('<KeyRelease>', lambda e: self._update_connection_info())
        
        server_frame.columnconfigure(1, weight=1)
        
        # Payload options frame
        options_frame = tk.LabelFrame(
            main_frame,
            text="Payload Options",
            font=('Consolas', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.GROOVE,
            bd=2
        )
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        options_inner = tk.Frame(options_frame, bg='#2d2d2d')
        options_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Payload type
        tk.Label(
            options_inner,
            text="Payload Type:",
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff'
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.type_var = tk.StringVar(value='python')
        type_combo = ttk.Combobox(
            options_inner,
            textvariable=self.type_var,
            values=['python', 'powershell', 'bash', 'batch', 'vbs', 
                   'hta', 'js', 'vbe', 'exe', 'scr', 'elf', 'dll',
                   'jpg', 'png', 'pdf'],
            state='readonly',
            font=('Consolas', 10)
        )
        type_combo.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        type_combo.bind('<<ComboboxSelected>>', self._on_type_change)
        
        # Listener type
        tk.Label(
            options_inner,
            text="Listener Type:",
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff'
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        listener_frame = tk.Frame(options_inner, bg='#2d2d2d')
        listener_frame.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        self.listener_var = tk.StringVar(value='http')
        listener_combo = ttk.Combobox(
            listener_frame,
            textvariable=self.listener_var,
            values=['http', 'tcp'],
            state='readonly',
            font=('Consolas', 10),
            width=15
        )
        listener_combo.pack(side=tk.LEFT)
        listener_combo.bind('<<ComboboxSelected>>', self._on_listener_change)
        
        # Protocol info label
        self.protocol_info = tk.Label(
            listener_frame,
            text="📡 HTTP (Web-based)",
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#00aaff',
            anchor=tk.W
        )
        self.protocol_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # Obfuscation
        self.obfuscate_var = tk.BooleanVar(value=False)
        obfuscate_check = tk.Checkbutton(
            options_inner,
            text="Enable Obfuscation",
            variable=self.obfuscate_var,
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff',
            selectcolor='#3c3c3c',
            activebackground='#2d2d2d',
            activeforeground='#00ff00'
        )
        obfuscate_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        options_inner.columnconfigure(1, weight=1)
        
        # Output frame
        output_frame = tk.LabelFrame(
            main_frame,
            text="Output",
            font=('Consolas', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.GROOVE,
            bd=2
        )
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_inner = tk.Frame(output_frame, bg='#2d2d2d')
        output_inner.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            output_inner,
            text="Output File:",
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff'
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.output_entry = tk.Entry(
            output_inner,
            font=('Consolas', 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.output_entry.insert(0, "payload.py")
        self.output_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 5), pady=5)
        
        browse_btn = tk.Button(
            output_inner,
            text="Browse",
            command=self._browse_output,
            font=('Consolas', 9),
            bg='#3c3c3c',
            fg='#ffffff',
            relief=tk.FLAT
        )
        browse_btn.grid(row=0, column=2, pady=5)
        
        output_inner.columnconfigure(1, weight=1)
        
        # Connection info frame
        info_frame = tk.LabelFrame(
            main_frame,
            text="Connection Info",
            font=('Consolas', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.GROOVE,
            bd=2
        )
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_inner = tk.Frame(info_frame, bg='#2d2d2d')
        info_inner.pack(fill=tk.X, padx=10, pady=10)
        
        self.connection_label = tk.Label(
            info_inner,
            text="📍 Agent will connect to: http://127.0.0.1:8080",
            font=('Consolas', 10, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00',
            anchor=tk.W
        )
        self.connection_label.pack(fill=tk.X)
        
        # Update connection info
        self._update_connection_info()
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#1e1e1e')
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        generate_btn = tk.Button(
            buttons_frame,
            text="🚀 Generate Payload",
            command=self._generate_payload,
            font=('Consolas', 12, 'bold'),
            bg='#00ff00',
            fg='#000000',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        generate_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        preview_btn = tk.Button(
            buttons_frame,
            text="👁️ Preview",
            command=self._preview_payload,
            font=('Consolas', 12, 'bold'),
            bg='#3c3c3c',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        preview_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Status frame
        status_frame = tk.LabelFrame(
            main_frame,
            text="Status",
            font=('Consolas', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.GROOVE,
            bd=2
        )
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(
            status_frame,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#00ff00',
            wrap=tk.WORD,
            height=10
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        self._log("✅ Payload Generator tayyor\n")
    
    def _on_type_change(self, event=None):
        """Payload type o'zgarganda fayl kengaytmasini yangilash"""
        payload_type = self.type_var.get()
        extensions = {
            'python': '.py',
            'powershell': '.ps1',
            'bash': '.sh',
            'batch': '.bat',
            'vbs': '.vbs',
            'hta': '.hta',
            'js': '.js',
            'vbe': '.vbe',
            'exe': '.exe',
            'scr': '.scr',
            'elf': '',
            'dll': '.dll',
            'jpg': '.jpg',
            'png': '.png',
            'pdf': '.pdf'
        }
        
        current = self.output_entry.get()
        base = os.path.splitext(current)[0]
        new_name = base + extensions.get(payload_type, '.txt')
        
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, new_name)
        
        # Connection info update
        self._update_connection_info()
    
    def _on_listener_change(self, event=None):
        """Listener type o'zgarganda"""
        listener_type = self.listener_var.get()
        
        # Protocol info update
        protocol_info = {
            'http': ('📡 HTTP (Web-based)', '#00aaff'),
            'tcp': ('🔌 TCP (Raw socket)', '#ff9900')
        }
        
        info_text, info_color = protocol_info.get(listener_type, ('', '#ffffff'))
        self.protocol_info.config(text=info_text, fg=info_color)
        
        # Port default o'zgartirish
        if listener_type == 'http' and self.port_entry.get() == '4444':
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, '8080')
        elif listener_type == 'tcp' and self.port_entry.get() == '8080':
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, '4444')
        
        # Connection info update
        self._update_connection_info()
    
    def _update_connection_info(self):
        """Connection info yangilash"""
        try:
            host = self.host_entry.get() or '127.0.0.1'
            port = self.port_entry.get() or '8080'
            listener = self.listener_var.get() or 'http'
            
            if listener == 'http':
                conn_str = f"📍 Agent will connect to: http://{host}:{port}"
                color = '#00ff00'
            else:
                conn_str = f"📍 Agent will connect to: tcp://{host}:{port}"
                color = '#ff9900'
            
            self.connection_label.config(text=conn_str, fg=color)
        except:
            pass
    
    def _browse_output(self):
        """Output fayl tanlash"""
        filetypes = [
            ("Python Files", "*.py"),
            ("PowerShell Files", "*.ps1"),
            ("Bash Files", "*.sh"),
            ("Batch Files", "*.bat"),
            ("VBS Files", "*.vbs"),
            ("HTA Files", "*.hta"),
            ("JavaScript Files", "*.js"),
            ("VBE Files", "*.vbe"),
            ("Executable Files", "*.exe"),
            ("Screensaver Files", "*.scr"),
            ("DLL Files", "*.dll"),
            ("ELF Files", "*"),
            ("Image Files", "*.jpg;*.png"),
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Save Payload",
            defaultextension=".py",
            filetypes=filetypes
        )
        
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)
    
    def _generate_payload(self):
        """Payload yaratish"""
        try:
            # Input validation
            host = self.host_entry.get().strip()
            port = self.port_entry.get().strip()
            output = self.output_entry.get().strip()
            
            if not host or not port or not output:
                messagebox.showerror("Error", "Barcha maydonlarni to'ldiring!")
                return
            
            try:
                port = int(port)
            except ValueError:
                messagebox.showerror("Error", "Port raqam bo'lishi kerak!")
                return
            
            # Generator yaratish
            self.generator = PayloadGenerator(host, port)
            
            # Payload yaratish
            self._log(f"\n{'='*50}")
            self._log(f"🚀 Payload yaratilmoqda...")
            self._log(f"   Type: {self.type_var.get()}")
            self._log(f"   Listener: {self.listener_var.get()}")
            self._log(f"   Server: {host}:{port}")
            self._log(f"   Output: {output}")
            self._log(f"   Obfuscate: {'Yes' if self.obfuscate_var.get() else 'No'}")
            self._log(f"{'='*50}\n")
            
            result = self.generator.generate(
                payload_type=self.type_var.get(),
                listener_type=self.listener_var.get(),
                output_file=output,
                obfuscate=self.obfuscate_var.get()
            )
            
            if result.get('success'):
                listener_type = self.listener_var.get()
                protocol_emoji = '📡' if listener_type == 'http' else '🔌'
                
                self._log(f"✅ Payload muvaffaqiyatli yaratildi!")
                self._log(f"   Size: {result['size']:,} bytes")
                self._log(f"   Protocol: {protocol_emoji} {listener_type.upper()}")
                self._log(f"   Time: {datetime.now().strftime('%H:%M:%S')}\n")
                
                messagebox.showinfo(
                    "Success",
                    f"Payload yaratildi!\n\n"
                    f"File: {output}\n"
                    f"Size: {result['size']:,} bytes\n"
                    f"Protocol: {protocol_emoji} {listener_type.upper()}\n"
                    f"Target: {host}:{port}"
                )
            else:
                error = result.get('error', 'Unknown error')
                self._log(f"❌ Xato: {error}\n")
                messagebox.showerror("Error", f"Payload yaratishda xato:\n{error}")
                
        except Exception as e:
            self._log(f"❌ Xatolik: {str(e)}\n")
            messagebox.showerror("Error", f"Xatolik:\n{str(e)}")
    
    def _preview_payload(self):
        """Payload preview"""
        try:
            host = self.host_entry.get().strip()
            port = self.port_entry.get().strip()
            
            if not host or not port:
                messagebox.showerror("Error", "Host va Port kiriting!")
                return
            
            port = int(port)
            
            # Vaqtinchalik generator
            temp_gen = PayloadGenerator(host, port)
            result = temp_gen.generate(
                payload_type=self.type_var.get(),
                listener_type=self.listener_var.get(),
                obfuscate=self.obfuscate_var.get()
            )
            
            if result.get('success'):
                # Preview window
                preview_window = tk.Toplevel(self.window)
                preview_window.title("Payload Preview")
                preview_window.geometry("800x600")
                preview_window.configure(bg='#1e1e1e')
                
                text = tk.Text(
                    preview_window,
                    font=('Consolas', 9),
                    bg='#1e1e1e',
                    fg='#00ff00',
                    wrap=tk.NONE
                )
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Scrollbars
                vsb = tk.Scrollbar(text, orient=tk.VERTICAL, command=text.yview)
                vsb.pack(side=tk.RIGHT, fill=tk.Y)
                text.config(yscrollcommand=vsb.set)
                
                hsb = tk.Scrollbar(text, orient=tk.HORIZONTAL, command=text.xview)
                hsb.pack(side=tk.BOTTOM, fill=tk.X)
                text.config(xscrollcommand=hsb.set)
                
                # Content
                text.insert('1.0', result['content'])
                text.config(state=tk.DISABLED)
                
            else:
                messagebox.showerror("Error", result.get('error', 'Unknown error'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Preview xatosi:\n{str(e)}")
    
    def _log(self, message: str):
        """Status log"""
        self.status_text.insert(tk.END, message + '\n')
        self.status_text.see(tk.END)
        self.window.update()
    
    def run(self):
        """GUI ishga tushirish"""
        self.window.mainloop()


if __name__ == "__main__":
    app = PayloadGeneratorGUI()
    app.run()
