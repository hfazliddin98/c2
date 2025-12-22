"""
Master Server Launcher
Barcha C2 serverlarni bir vaqtda ishga tushirish
"""

import subprocess
import time
import os
import sys
from datetime import datetime


class ServerManager:
    """Barcha serverlarni boshqarish"""
    
    def __init__(self):
        self.processes = []
        self.servers = [
            {
                'name': 'TCP Server',
                'script': 'server/tcp_server.py',
                'port': 9999,
                'icon': '🔵'
            },
            {
                'name': 'HTTP Server',
                'script': 'server/http_server.py',
                'port': 8080,
                'icon': '🌐'
            },
            {
                'name': 'HTTPS Server',
                'script': 'server/https_server.py',
                'port': 8443,
                'icon': '🔒'
            },
            {
                'name': 'WebSocket Server',
                'script': 'server/websocket_server.py',
                'port': 8765,
                'icon': '🔌'
            },
            {
                'name': 'UDP Server',
                'script': 'server/udp_server.py',
                'port': 5353,
                'icon': '📡'
            },
            {
                'name': 'DNS Server',
                'script': 'server/dns_server.py',
                'port': 5353,
                'icon': '🌍'
            },
            {
                'name': 'ICMP Server',
                'script': 'server/icmp_server.py',
                'port': 'raw',
                'icon': '📶',
                'requires_admin': True
            },
            {
                'name': 'RTSP Server',
                'script': 'server/rtsp_server.py',
                'port': 8554,
                'icon': '📹'
            }
        ]
    
    def check_server_exists(self, script_path):
        """Server script mavjudligini tekshirish"""
        return os.path.exists(script_path)
    
    def start_all_servers(self):
        """Barcha serverlarni ishga tushirish"""
        print("\n" + "="*70)
        print("🚀 C2 Platform - Master Server Launcher")
        print("="*70)
        print(f"\n📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Working Directory: {os.getcwd()}\n")
        
        print("Serverlar ishga tushirilmoqda...\n")
        
        started_count = 0
        failed_count = 0
        
        for server in self.servers:
            try:
                # Check if script exists
                if not self.check_server_exists(server['script']):
                    print(f"{server['icon']} {server['name']:20} ❌ SCRIPT TOPILMADI: {server['script']}")
                    failed_count += 1
                    continue
                
                # Check admin requirement
                if server.get('requires_admin', False) and os.name == 'nt':
                    import ctypes
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        print(f"{server['icon']} {server['name']:20} ⚠️  ADMIN KERAK (o'tkazib yuborildi)")
                        continue
                
                # Start server
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(
                        [sys.executable, server['script']],
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                else:  # Linux/Mac
                    process = subprocess.Popen(
                        [sys.executable, server['script']],
                        start_new_session=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                
                self.processes.append({
                    'name': server['name'],
                    'process': process,
                    'script': server['script']
                })
                
                port_info = f":{server['port']}" if server['port'] != 'raw' else ''
                print(f"{server['icon']} {server['name']:20} ✅ ISHGA TUSHDI (PID: {process.pid}{port_info})")
                started_count += 1
                
                # Small delay between starts
                time.sleep(0.5)
                
            except Exception as e:
                print(f"{server['icon']} {server['name']:20} ❌ XATO: {e}")
                failed_count += 1
        
        print("\n" + "="*70)
        print(f"✅ Ishga tushgan: {started_count}")
        print(f"❌ Xato: {failed_count}")
        print("="*70)
        
        if started_count > 0:
            print("\n💡 Serverlar ishga tushdi!")
            print("📌 GUI'ni ishga tushirish: python gui/modular_gui.py")
            print("📌 To'xtatish: Ctrl+C\n")
            
            return True
        else:
            print("\n❌ Hech qanday server ishga tushmadi!")
            return False
    
    def monitor_servers(self):
        """Serverlarni monitoring qilish"""
        try:
            print("🔍 Monitoring boshlanmoqda...\n")
            print("Serverlar ishlashini kuzatish (Ctrl+C - to'xtatish)\n")
            
            while True:
                time.sleep(5)
                
                # Check if any process died
                for item in self.processes:
                    if item['process'].poll() is not None:
                        print(f"\n⚠️  {item['name']} to'xtadi! (Exit code: {item['process'].poll()})")
                        
                        # Restart
                        print(f"🔄 {item['name']} qayta ishga tushirilmoqda...")
                        
                        try:
                            if os.name == 'nt':
                                new_process = subprocess.Popen(
                                    [sys.executable, item['script']],
                                    creationflags=subprocess.CREATE_NEW_CONSOLE
                                )
                            else:
                                new_process = subprocess.Popen(
                                    [sys.executable, item['script']],
                                    start_new_session=True
                                )
                            
                            item['process'] = new_process
                            print(f"✅ {item['name']} qayta ishga tushdi (PID: {new_process.pid})\n")
                            
                        except Exception as e:
                            print(f"❌ Qayta ishga tushirishda xato: {e}\n")
                
        except KeyboardInterrupt:
            print("\n\n🛑 To'xtatish signali qabul qilindi...")
            self.stop_all_servers()
    
    def stop_all_servers(self):
        """Barcha serverlarni to'xtatish"""
        print("\n" + "="*70)
        print("🛑 Barcha serverlar to'xtatilmoqda...")
        print("="*70 + "\n")
        
        for item in self.processes:
            try:
                if item['process'].poll() is None:
                    item['process'].terminate()
                    item['process'].wait(timeout=5)
                    print(f"✅ {item['name']} to'xtatildi")
            except Exception as e:
                print(f"❌ {item['name']} to'xtatishda xato: {e}")
                try:
                    item['process'].kill()
                except:
                    pass
        
        print("\n✅ Barcha serverlar to'xtatildi\n")
    
    def start_with_monitoring(self):
        """Serverlarni ishga tushirish va monitoring"""
        if self.start_all_servers():
            self.monitor_servers()


def main():
    """Main entry point"""
    
    # Banner
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        🎯 C2 Platform - Master Server Launcher 🎯            ║
    ║                                                               ║
    ║  Barcha serverlarni bir vaqtda ishga tushirish va boshqarish ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    manager = ServerManager()
    
    print("Tanlang:")
    print("1. Barcha serverlarni ishga tushirish + Monitoring")
    print("2. Barcha serverlarni ishga tushirish (background)")
    print("3. Chiqish")
    
    choice = input("\nTanlov (1-3): ").strip()
    
    if choice == '1':
        manager.start_with_monitoring()
    elif choice == '2':
        manager.start_all_servers()
        print("\n✅ Serverlar background'da ishlamoqda")
    elif choice == '3':
        print("❌ Bekor qilindi")
    else:
        print("❌ Noto'g'ri tanlov!")


if __name__ == "__main__":
    main()
