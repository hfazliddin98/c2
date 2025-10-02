# C2 Platform - Loyiha Strukturasi

## 📁 Asosiy Papkalar

```
c2/
├── 📄 README.md                 # Loyiha haqida ma'lumot
├── 📄 requirements.txt          # Python dependencies
├── 🚀 start_server.bat          # Server ishga tushirish
├── 🚀 start_agent.bat           # Agent ishga tushirish  
├── 🚀 start_cli.bat             # CLI ishga tushirish
│
├── 📁 server/                   # C2 Server komponenti
│   ├── 📄 app.py               # Asosiy Flask server
│   └── 📄 cli.py               # Command Line Interface
│
├── 📁 agent/                    # Agent (Client) komponenti
│   └── 📄 client.py            # Agent client dasturi
│
├── 📁 common/                   # Umumiy modullar
│   ├── 📄 config.py            # Konfiguratsiya sozlamalari
│   ├── 📄 utils.py             # Utility funksiyalar
│   ├── 📄 crypto.py            # Shifrash funksiyalari
│   └── 📄 commands.py          # Komandalar moduli
│
└── 📁 web/                      # Web interface (kelajak)
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