# 🚀 C2 Platform - Quick Start Guide

## 📍 Birinchi: IP Manzilni Aniqlash

Server qaysi IP da ishlayotganini bilish kerak:

```bash
python common/network_helper.py
```

Yoki:
```bash
show_ip.bat  # Windows
./show_ip.sh # Linux/Mac
```

**Natija:**
```
📍 Local IP: 192.168.1.2    ← Wi-Fi/LAN orqali
🌍 Public IP: 84.54.86.9    ← Internet orqali (port forwarding kerak)
```

---

## Barcha Serverlarni Bir Vaqtda Ishga Tushirish

### ⚡ Tezkor Usul (Recommended)

**Windows:**
```batch
START_ALL.bat
```

**Linux/Mac:**
```bash
chmod +x START_ALL.sh
./START_ALL.sh
```

**Python (Platform-independent):**
```bash
python start_all_servers.py
```

---

## 🎯 3 Xil Usul

### 1️⃣ Master Launcher (Eng Oson)

Barcha serverlarni avtomatik ishga tushiradi va monitoring qiladi:

```bash
python start_all_servers.py
```

**Tanlovlar:**
- `1` - Barcha serverlar + Monitoring (to'xtatish: Ctrl+C)
- `2` - Barcha serverlar background'da
- `3` - Chiqish

**Qanday ishlaydi:**
- ✅ 8 ta server bir vaqtda ishga tushadi
- 🔄 Agar server to'xtasa, avtomatik qayta ishga tushadi
- 📊 Real-time monitoring
- 🛑 Ctrl+C bilan hammasi to'xtatiladi

---

### 2️⃣ Django Management Command

Agar Django ishlatayotgan bo'lsangiz:

```bash
python manage.py startservers
```

**Options:**
```bash
# Monitoring bilan
python manage.py startservers

# Monitoring'siz (background)
python manage.py startservers --no-monitor
```

---

### 3️⃣ Qo'lda Har Birini Alohida

Har bir serverni alohida ishga tushirish:

```bash
# TCP Server
python server/tcp_server.py

# HTTP Server  
python server/http_server.py

# HTTPS Server
python server/https_server.py

# WebSocket Server
python server/websocket_server.py

# UDP Server
python server/udp_server.py

# DNS Server
python server/dns_server.py

# ICMP Server (admin kerak)
sudo python server/icmp_server.py  # Linux/Mac
python server/icmp_server.py       # Windows (admin)

# RTSP Server
python server/rtsp_server.py
```

---

## 📋 Ishga Tushirilgan Serverlar

| Server | Port | Protokol | Vazifasi |
|--------|------|----------|----------|
| 🔵 TCP | 9999 | TCP | Raw socket, eng tez |
| 🌐 HTTP | 8080 | HTTP | Firewall friendly |
| 🔒 HTTPS | 8443 | HTTPS | SSL/TLS encrypted |
| 🔌 WebSocket | 8765 | WS | Real-time bidirectional |
| 📡 UDP | 5353 | UDP | Connectionless, fast |
| 🌍 DNS | 5353 | DNS | Tunneling, bypass |
| 📶 ICMP | raw | ICMP | Ping covert channel |
| 📹 RTSP | 8554 | RTSP | Video streaming |

---

## 🖥️ GUI Ishga Tushirish

Serverlar ishga tushgandan keyin:

```bash
python gui/modular_gui.py
```

GUI'da:
1. **Server IP AVTOMATIK aniqlangan** (masalan: 192.168.1.2)
2. Protokol tanlang (TCP, HTTP, HTTPS, ...)
3. Port avtomatik to'ldiriladi
4. "🔌 Ulaning" tugmasini bosing

### ⚠️ DIQQAT: IP Manzillar

**Local network (Wi-Fi/LAN):**
- Server IP: `192.168.1.2` (yoki sizning local IP)
- Agent'dan ulanish: `192.168.1.2:9999`
- Faqat bir xil Wi-Fi/LAN da ishlaydi

**Internet orqali:**
- Server IP: Public IP (masalan: `84.54.86.9`)
- Port forwarding kerak!
- Router'da 9999 portini ochish kerak

---

## ✅ Tekshirish

Barcha serverlar ishlayotganini tekshirish:

```bash
# Windows
netstat -ano | findstr "9999 8080 8443 8765 5353 8554"

# Linux/Mac
netstat -tuln | grep -E "9999|8080|8443|8765|5353|8554"
```

Yoki GUI'da:
- "🔊 TCP Status" tugmasini bosing
- Barcha serverlar holati ko'rsatiladi

---

## 🛑 To'xtatish

### Master Launcher orqali:
- `Ctrl+C` - Barcha serverlar to'xtatiladi

### Alohida:
- Har bir console/terminal'ni yoping
- Yoki process manager orqali:

**Windows:**
```batch
taskkill /F /IM python.exe
```

**Linux/Mac:**
```bash
pkill -f "server/"
```

---

## 🔧 Troubleshooting

### Port band bo'lsa:

```bash
# Portni kim ishlatayotganini topish
# Windows:
netstat -ano | findstr "9999"
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :9999
kill -9 <PID>
```

### Admin ruxsati kerak (ICMP):

**Windows:**
- PowerShell'ni Administrator sifatida oching

**Linux/Mac:**
```bash
sudo python server/icmp_server.py
```

---

## 📊 Auto-Start Features

Master launcher quyidagilarni avtomatik bajaradi:

✅ Barcha serverlarni parallel ishga tushiradi
✅ Script mavjudligini tekshiradi
✅ Port conflict'larni handle qiladi
✅ Crash bo'lgan serverlarni restart qiladi
✅ Real-time monitoring
✅ Graceful shutdown (Ctrl+C)

---

## 🎯 Recommended Workflow

1. **Barcha serverlarni ishga tushiring:**
   ```bash
   python start_all_servers.py
   ```

2. **GUI'ni oching:**
   ```bash
   python gui/modular_gui.py
   ```

3. **Protokol tanlang va ulaning**

4. **Agent'ni telefon/PC'da ishga tushiring**

5. **To'xtatish: Ctrl+C**

---

## 💡 Tips

- **Background'da ishlatish:** Tanlov 2'ni tanlang
- **Debugging:** Har bir serverni alohida ishga tushiring
- **Production:** Supervisor yoki systemd ishlatish tavsiya etiladi
- **Windows Service:** NSSM orqali service qilish mumkin

---

✅ **Tayyor!** Barcha serverlar bir vaqtda ishga tushadi! 🚀
