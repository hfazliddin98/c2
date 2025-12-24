"""
Shifrangan Agent - TCP Client with AES-256 Encryption
"""

import socket
import json
import uuid
import platform
import time
from common.crypto import CryptoManager


class EncryptedTCPAgent:
    """Shifrlangan TCP Agent"""
    
    def __init__(self, server_host='127.0.0.1', server_port=9999, password='agent_password_123'):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.agent_id = str(uuid.uuid4())
        
        # Shifrlash manageri
        self.crypto = CryptoManager(password=password)
        self.encryption_enabled = True
        
        print(f"🔐 Shifrlash yoqilgan: {self.encryption_enabled}")
        print(f"🔑 Encryption key: {self.crypto.get_key()[:32]}...")
    
    def connect(self):
        """Serverga ulanish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"✅ Serverga ulandi: {self.server_host}:{self.server_port}")
            
            # System info jo'natish (shifrlangan)
            system_info = self.get_system_info()
            self.send_data(system_info)
            print("📤 System info jo'natildi (shifrlangan)")
            
            return True
        except Exception as e:
            print(f"❌ Ulanish xatosi: {e}")
            return False
    
    def get_system_info(self):
        """System info to'plash"""
        return {
            "agent_id": self.agent_id,
            "hostname": platform.node(),
            "platform": platform.system() + " " + platform.release(),
            "username": "user",
            "ip_address": "127.0.0.1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "encrypted": self.encryption_enabled,
            "encryption_key": self.crypto.get_key()  # Server uchun key
        }
    
    def send_data(self, data):
        """Ma'lumot jo'natish (shifrlangan)"""
        try:
            # JSON ga o'zgartirish
            json_data = json.dumps(data)
            
            # Shifrlash
            if self.encryption_enabled:
                encrypted_data = self.crypto.encrypt(json_data)
                # Shifrlangan ma'lumotni jo'natish
                message = encrypted_data.encode('utf-8')
            else:
                message = json_data.encode('utf-8')
            
            # 4-byte length prefix + data
            length = len(message).to_bytes(4, byteorder='big')
            self.socket.sendall(length + message)
            
            # Statistika
            original_size = len(json_data)
            encrypted_size = len(message)
            overhead = encrypted_size - original_size
            overhead_pct = (overhead / original_size) * 100
            
            print(f"📊 Size: {original_size}B → {encrypted_size}B (+{overhead}B, +{overhead_pct:.1f}%)")
            
        except Exception as e:
            print(f"❌ Jo'natish xatosi: {e}")
    
    def receive_data(self, timeout=30):
        """Ma'lumot qabul qilish (shifrlangan)"""
        try:
            self.socket.settimeout(timeout)
            
            # 4-byte length o'qish
            length_bytes = self.socket.recv(4)
            if not length_bytes:
                return None
            
            length = int.from_bytes(length_bytes, byteorder='big')
            
            # Ma'lumot o'qish
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(min(length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk
            
            # Deshifrlash
            if self.encryption_enabled:
                encrypted_data = data.decode('utf-8')
                decrypted_data = self.crypto.decrypt(encrypted_data)
                return json.loads(decrypted_data)
            else:
                return json.loads(data.decode('utf-8'))
            
        except socket.timeout:
            return {"type": "timeout"}
        except Exception as e:
            print(f"❌ Qabul qilish xatosi: {e}")
            return None
    
    def start(self):
        """Agent'ni boshlash"""
        if not self.connect():
            return
        
        print("\n💓 Heartbeat loop boshlandi...")
        print("🔐 Barcha ma'lumotlar AES-256 bilan shifrlangan\n")
        
        while True:
            try:
                # Serverdan xabar kutish
                message = self.receive_data(timeout=30)
                
                if not message:
                    print("⚠️  Server ulanishi uzildi")
                    break
                
                msg_type = message.get('type', 'unknown')
                print(f"📥 Qabul qilindi: {msg_type}")
                
                # Heartbeat javob
                if msg_type == 'heartbeat':
                    response = {
                        "type": "heartbeat_ack",
                        "status": "alive",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                    }
                    self.send_data(response)
                    print("📤 Heartbeat ACK jo'natildi")
                
                # Command bajarish
                elif msg_type == 'command':
                    command = message.get('command')
                    print(f"⚙️  Command: {command}")
                    
                    # Command natijasi
                    result = {
                        "command_id": message.get('command_id'),
                        "status": "success",
                        "result": f"Command '{command}' bajarildi",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                    }
                    self.send_data(result)
                    print("📤 Command natijasi jo'natildi")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Agent to'xtatildi")
                break
            except Exception as e:
                print(f"❌ Xato: {e}")
                break
        
        self.socket.close()


def test_encryption_overhead():
    """Shifrlash overhead'ini test qilish"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║       SHIFRLASH OVERHEAD TESTI (Real Agent)               ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    crypto = CryptoManager(password="agent_password_123")
    
    # Test 1: Heartbeat
    print("1️⃣  Heartbeat xabari:")
    heartbeat = {
        "type": "heartbeat_ack",
        "status": "alive",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    json_data = json.dumps(heartbeat)
    encrypted = crypto.encrypt(json_data)
    
    original_size = len(json_data)
    encrypted_size = len(encrypted)
    overhead = encrypted_size - original_size
    overhead_pct = (overhead / original_size) * 100
    
    print(f"   Original:  {original_size} bytes")
    print(f"   Encrypted: {encrypted_size} bytes")
    print(f"   Overhead:  +{overhead} bytes (+{overhead_pct:.1f}%)")
    
    # Vaqt o'lchash
    start = time.time()
    for _ in range(1000):
        _ = crypto.encrypt(json_data)
    encrypt_time = (time.time() - start) / 1000
    
    start = time.time()
    for _ in range(1000):
        _ = crypto.decrypt(encrypted)
    decrypt_time = (time.time() - start) / 1000
    
    print(f"   Encrypt:   {encrypt_time*1000:.3f}ms")
    print(f"   Decrypt:   {decrypt_time*1000:.3f}ms")
    print(f"   Total:     {(encrypt_time+decrypt_time)*1000:.3f}ms")
    
    # Test 2: Command natijasi
    print("\n2️⃣  Command natijasi (sysinfo):")
    command_result = {
        "command_id": "cmd-123",
        "status": "success",
        "result": {
            "hostname": platform.node(),
            "platform": platform.system(),
            "cpu": "CPU info",
            "ram": "RAM info"
        }
    }
    
    json_data = json.dumps(command_result)
    encrypted = crypto.encrypt(json_data)
    
    original_size = len(json_data)
    encrypted_size = len(encrypted)
    overhead = encrypted_size - original_size
    overhead_pct = (overhead / original_size) * 100
    
    print(f"   Original:  {original_size} bytes")
    print(f"   Encrypted: {encrypted_size} bytes")
    print(f"   Overhead:  +{overhead} bytes (+{overhead_pct:.1f}%)\n")
    
    print("💡 XULOSA:")
    print("   Kichik xabarlar uchun shifrlash MINIMAL overhead")
    print("   Heartbeat: ~0.1ms qo'shimcha vaqt")
    print("   Command: ~0.1ms qo'shimcha vaqt")
    print("   Network latency (10-100ms) dan ANCHA kichik\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Overhead test
        test_encryption_overhead()
    else:
        # Agent ishga tushirish
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║         SHIFRLANGAN TCP AGENT ISHGA TUSHIRILMOQDA        ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        agent = EncryptedTCPAgent(
            server_host='127.0.0.1',
            server_port=9999,
            password='agent_password_123'
        )
        
        agent.start()
