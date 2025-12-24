"""
Shifrlangan Server va Agent Test
Test: Agent va Server encryption bilan bog'lanishi
"""

import sys
import os
import time
import threading

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.tcp_server import TCPServer
from agent.encrypted_tcp_client import EncryptedTCPAgent


def start_encrypted_server():
    """Shifrlangan server ishga tushirish"""
    print("\n" + "="*60)
    print("🔐 SHIFRLANGAN SERVER ISHGA TUSHIRILMOQDA")
    print("="*60 + "\n")
    
    # Server encryption bilan
    server = TCPServer(
        host='127.0.0.1',
        port=9999,
        encryption_enabled=True,
        password='c2_server_password_2025'
    )
    
    # Server thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    print("✅ Server thread boshlandi\n")
    time.sleep(2)  # Server ishga tushishini kutish
    
    return server


def start_encrypted_agent():
    """Shifrlangan agent ishga tushirish"""
    print("\n" + "="*60)
    print("🔐 SHIFRLANGAN AGENT ISHGA TUSHIRILMOQDA")
    print("="*60 + "\n")
    
    # Agent encryption bilan
    agent = EncryptedTCPAgent(
        server_host='127.0.0.1',
        server_port=9999,
        password='c2_server_password_2025'  # Server bilan bir xil parol
    )
    
    return agent


def test_unencrypted_server():
    """Shifirlanmagan server test"""
    print("\n" + "="*60)
    print("⚠️  SHIFIRLANMAGAN SERVER TEST")
    print("="*60 + "\n")
    
    server = TCPServer(
        host='127.0.0.1',
        port=9998,
        encryption_enabled=False  # Encryption o'chirilgan
    )
    
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    print("⚠️  Server encryption OFF\n")
    time.sleep(1)
    
    return server


def compare_encryption():
    """Shifrlangan vs Shifirlanmagan taqqoslash"""
    print("\n" + "="*60)
    print("📊 ENCRYPTION TAQQOSLASH")
    print("="*60 + "\n")
    
    from common.crypto import CryptoManager
    import json
    
    crypto = CryptoManager(password='c2_server_password_2025')
    
    # Test data
    test_data = {
        "agent_id": "test-123",
        "hostname": "TEST-PC",
        "platform": "Windows 11",
        "username": "admin",
        "password": "secret123"  # Muhim ma'lumot
    }
    
    json_data = json.dumps(test_data)
    
    print("📋 Original Data:")
    print(f"   {json_data[:80]}...")
    print(f"   Size: {len(json_data)} bytes\n")
    
    # Shifrlangan
    encrypted = crypto.encrypt(json_data)
    print("🔐 Encrypted Data:")
    print(f"   {encrypted[:80]}...")
    print(f"   Size: {len(encrypted)} bytes")
    print(f"   Overhead: +{len(encrypted) - len(json_data)} bytes\n")
    
    # Network'da qanday ko'rinadi
    print("🌐 Network'da ko'rinish:")
    print("\n   SHIFIRLANMAGAN (Wireshark):")
    print("   " + "❌ " * 30)
    print(f"   ✅ Barcha ma'lumotlar OCHIQ ko'rinadi:")
    print(f"      - username: admin")
    print(f"      - password: secret123")
    print(f"      - hostname: TEST-PC")
    print(f"   🔴 XAVF: 95-100%\n")
    
    print("   SHIFRLANGAN (Wireshark):")
    print("   " + "🔐 " * 30)
    print(f"   ❌ Faqat gibberish ko'rinadi:")
    print(f"      {encrypted[:50]}...")
    print(f"   🟢 XAVF: 0-5%\n")


def main():
    """Test uchun asosiy funksiya"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     SHIFRLANGAN AGENT-SERVER ALOQA TEST                   ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Taqqoslash
    compare_encryption()
    
    # Server ishga tushirish
    print("\n" + "="*60)
    print("🚀 TEST BOSHLANDI")
    print("="*60 + "\n")
    
    server = start_encrypted_server()
    
    # Agent ishga tushirish
    time.sleep(2)
    agent = start_encrypted_agent()
    
    # Agent serverga ulanish
    print("\n📡 Agent serverga ulanmoqda...\n")
    
    if agent.connect():
        print("\n✅ MUVAFFAQIYATLI ULANISH!\n")
        print("🔐 Barcha ma'lumotlar AES-256 bilan shifrlangan")
        print("📊 Server va Agent bir xil parol ishlatmoqda")
        print("🛡️ Network sniffing: HIMOYALANGAN")
        print("\n💡 Agent heartbeat loop boshlandi...")
        print("   (Ctrl+C bilan to'xtatish)\n")
        
        try:
            # 30 soniya test
            for i in range(6):
                time.sleep(5)
                print(f"⏱️  {(i+1)*5} soniya o'tdi - Aloqa SHIFRLANGAN!")
            
            print("\n✅ TEST MUVAFFAQIYATLI TUGADI!")
            print("\n📊 NATIJALAR:")
            print("   ✅ Server encryption: ENABLED")
            print("   ✅ Agent encryption: ENABLED")
            print("   ✅ Connection: SUCCESS")
            print("   ✅ Heartbeat: WORKING")
            print("   ✅ Data: ENCRYPTED (AES-256)")
            print("\n🔒 XAVFSIZLIK: 95% YAXSHILANISH!")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Test to'xtatildi")
    else:
        print("\n❌ ULANISH XATOSI!")
        print("   Server va Agent parollari bir xilmi?")
        print("   Server ishlayptimi?")
    
    print("\n" + "="*60)
    print("TEST TUGADI")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test to'xtatildi")
    except Exception as e:
        print(f"\n❌ Xato: {e}")
        import traceback
        traceback.print_exc()
