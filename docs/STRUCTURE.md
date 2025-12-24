# C2 Platform - Loyiha Strukturasi

Bu loyihada **ikki xil server** mavjud:

## 🌐 HTTP Server (Flask-based)
- **Fayl**: `server/app.py`
- **Port**: 8080 
- **Protokol**: HTTP/JSON
- **Xususiyatlari**:
  - Web Dashboard (http://127.0.0.1:8080)
  - REST API endpoints
  - Real-time updates
  - Browser-friendly interface

## 🔌 TCP Server (Raw Socket)
- **Fayl**: `server/tcp_server.py` 
- **Port**: 9999
- **Protokol**: Raw TCP Socket
- **Xususiyatlari**:
  - Tezkor aloqa
  - Kam traffic
  - Binary data support
  - CLI interface

## 🎯 Havoc C2 Framework

Professional Havoc C2 ga o'xshash qilib yaratilgan framework.

## 📂 Loyiha Strukturasi

```
c2/
├── 📄 README.md                    # Loyiha haqida
├── 📄 STRUCTURE.md                 # Loyiha strukturasi  
├── 📄 CROSS_PLATFORM.md            # Ko'p platformali qo'llanma
├── 📄 requirements.txt             # Dependencies
├── 🐍 demo.py                      # Avtomatik demo
├── 🐍 check_platform.py            # Platform detector
│
├── 🚀 Windows Scripts              # Windows uchun
│   ├── setup.bat                  # Avtomatik o'rnatish
│   ├── start_server.bat           # HTTP server
│   ├── start_agent.bat            # HTTP agent
│   ├── start_tcp_server.bat       # TCP server
│   ├── start_tcp_agent.bat        # TCP agent
│   ├── start_havoc_gui.bat        # Havoc-style GUI
│   └── start_cli.bat              # CLI interface
│
├── 🐧 Linux/macOS Scripts         # Linux/macOS uchun
│   ├── setup.sh                   # Avtomatik o'rnatish
│   ├── start_server.sh            # HTTP server
│   ├── start_agent.sh             # HTTP agent
│   ├── start_tcp_server.sh        # TCP server
│   ├── start_tcp_agent.sh         # TCP agent
│   ├── start_havoc_gui.sh         # Havoc-style GUI
│   └── start_cli.sh               # CLI interface
│
├── 📁 server/                      # Server komponentlari
│   ├── app.py                     # HTTP Flask server
│   ├── tcp_server.py              # Raw TCP server
│   ├── cli.py                     # CLI interface
│   ├── listener_manager.py        # Listener boshqaruvi
│   └── session_manager.py         # Session boshqaruvi
│
├── 📁 agent/                      # Agent komponentlari
│   ├── client.py                  # HTTP agent
│   └── tcp_client.py              # TCP agent
│
├── 📁 gui/                        # GUI komponentlari
│   └── havoc_gui.py               # Havoc-style GUI
│
├── 📁 common/                     # Umumiy modullar
│   ├── config.py                  # Konfiguratsiya
│   ├── utils.py                   # Utility funksiyalar (platform detection)
│   ├── crypto.py                  # Shifrash
│   └── commands.py                # Komanda handler (cross-platform)
│
└── 📁 web/                        # Web interface (kelajak)
    └── (bo'sh)
```

## 🚀 Ishga Tushirish

### 1. Server ishga tushirish:
```bash
# Windows
start_server.bat

# Yoki qo'lda:
cd server
python app.py
```

### 2. Agent ishga tushirish:
```bash  
# Windows
start_agent.bat

# Yoki qo'lda:
cd agent
python client.py
```

### 3. CLI ishga tushirish:
```bash
# Windows
start_cli.bat

# Yoki qo'lda:
cd server
python cli.py
```

## 🌐 Web Dashboard

Server ishga tushgandan keyin brauzerda oching:
**http://127.0.0.1:8080**

## 💻 CLI Komandalar

| Komanda | Tavsif |
|---------|--------|
| `agents` | Barcha agentlar ro'yxati |
| `select <id>` | Agentni tanlash |
| `exec <cmd>` | Komanda bajarish |
| `sysinfo` | Sistem ma'lumotlari |
| `status` | Server holati |
| `help` | Yordam |

## 🔒 Xavfsizlik

⚠️ **Muhim:** Bu loyiha faqat **ta'lim maqsadida** yaratilgan!

- Faqat o'z kompyuteringizda sinang
- Real tarmowlarda ishlatmang
- Noqonuniy faoliyat uchun foydalanmang

## 📦 Dependencies

Asosiy kutubxonalar:
- `flask` - Web server
- `requests` - HTTP client
- `cryptography` - Shifrash
- `psutil` - Sistem ma'lumotlari
- `colorama` - Rangli chiqarish

## 🛠️ Texnik Ma'lumotlar

- **Til:** Python 3.7+
- **Framework:** Flask
- **Protokol:** HTTP/JSON
- **Port:** 8080 (default)
- **OS:** Windows/Linux/macOS