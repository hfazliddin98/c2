# C2 Platform - Django Production

Django 5.0 asosidagi professional C2 (Command and Control) platformasi. 10,000+ concurrent users uchun optimallashtirilgan.

## ⚠️ Ogohlantirish

Bu dastur faqat **ta'lim va tadqiqot maqsadlarida** ishlatilishi kerak. Noqonuniy faoliyat uchun foydalanish man etiladi.

## 🎯 Texnologiyalar

- **Backend:** Django 5.0 + Django REST Framework
- **WebSocket:** Django Channels 4.0 + Daphne ASGI
- **Task Queue:** Celery 5.3 + Redis
- **Database:** PostgreSQL 15 (production) / SQLite (dev)
- **Cache:** Redis 7 + django-redis
- **Server:** Gunicorn (HTTP) + Daphne (WebSocket)
- **Scalability:** 10,000+ concurrent connections

## 🏗️ Arxitektura

```
┌─────────────┐
│  OPERATOR   │
│ (CLI / GUI) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   SERVER LAYER      │
│                     │
│  • TCP Server       │ ◄──► Agent'lar (TCP Socket)
│  • Command Handler  │
│  • Health Monitor   │
│  • Django (Optional)│
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│   AGENT LAYER       │
│                     │
│  • Desktop Agent    │
│  • Mobile Agent     │
└─────────────────────┘
```

**To'liq:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 📂 Loyiha Strukturasi

```
c2/
├── README.md                    # Asosiy dokumentatsiya
├── manage.py                    # Django management
├── requirements.txt             # Python dependencies
├── db.sqlite3                  # Development database
│
├── docs/                       # 📚 Dokumentatsiya
│   ├── QUICK_START.md         # Tezkor boshlash
│   ├── STRUCTURE.md           # Arxitektura
│   ├── CLI_GUI_MODE.md        # CLI va GUI rejimi
│   ├── ANDROID_SETUP.md       # Android agent setup
│   ├── PAYLOAD_GENERATOR.md   # Payload generator guide
│   └── ...
│
├── scripts/                    # ⚙️ Barcha scriptlar
│   ├── START_CLI.bat/sh       # CLI rejimi
│   ├── START_GUI.bat/sh       # GUI rejimi
│   ├── START_ALL.bat/sh       # Full stack
│   ├── launcher.bat/sh        # Interaktiv launcher
│   ├── setup.bat/sh           # O'rnatish
│   └── ...
│
├── server/                     # 🖥️ Server komponentlari
│   ├── tcp_server.py          # TCP C2 Server
│   ├── command_handler.py     # Komanda handler
│   ├── cli.py                 # CLI interface
│   └── ...
│
├── agent/                      # 🤖 Agent clients
│   ├── tcp_client.py          # Desktop agent
│   ├── mobile_agent.py        # Mobile agent
│   └── smart_client.py        # Smart agent
│
├── gui/                        # 🎨 GUI interfaces
│   ├── tcp_server_gui.py      # Modern TCP GUI
│   ├── havoc_gui.py           # Havoc-style interface
│   └── payload_generator_gui.py
│
├── common/                     # 📦 Umumiy modullar
│   ├── config.py              # Konfiguratsiya
│   ├── utils.py               # Utility functions
│   ├── payload_generator.py   # Payload generator
│   └── ...
│
└── asosiy/                     # ⚙️ Django core
    ├── settings.py
    ├── urls.py
    └── ...
```

## 🚀 Tezkor Ishga Tushirish

### Variant 1: Quick Start (Tavsiya etiladi)
```bash
# Windows
QUICK_START.bat

# Linux/macOS
chmod +x QUICK_START.sh && ./QUICK_START.sh
```

### Variant 2: CLI Rejimi (Terminal)
```bash
# Windows
scripts\START_CLI.bat

# Linux/macOS
scripts/START_CLI.sh
```

### Variant 3: GUI Rejimi (Visual Interface)
```bash
# Windows
scripts\START_GUI.bat

# Linux/macOS
scripts/START_GUI.sh
```

### Variant 4: Full Stack (Django + Barcha serverlar)
```bash
# Windows
scripts\START_ALL.bat

# Linux/macOS
scripts/START_ALL.sh
```

## 📋 Barcha Komandalar

### Development (SQLite):
```bash
# Setup
scripts/setup.bat

# Migrate database
python manage.py migrate

# Create superuser
python manage.py createsuperuser
⚡ Xususiyatlar

### Core Framework
- [x] **Django 5.0** - Production-ready web framework
- [x] **REST API** - Django REST Framework
- [x] **WebSocket** - Real-time bi-directional communication
- [x] **Async Tasks** - Celery + Redis background processing
- [x] **Database** - PostgreSQL with connection pooling
- [x] **Cache** - Redis for high-performance caching
- [x] **Scalability** - 10,000+ concurrent users

### C2 Features
- [x] **Agent Management** - Session tracking, metadata, heartbeat
- [x] **TCP Server** - Raw socket protocol
- [x] **Listener Management** - HTTP, TCP listeners
- [x] **Command System** - Shell, PowerShell, file operations
- [x] **Payload Generator** - 15 formats (Python, PowerShell, EXE, DLL, JPG, PNG, PDF)
- [x] **GUI Interface** - Havoc-style + Payload Generator GUI
- [x] **CLI Interface** - Command line management

### Performance
- [x] **5-10ms** heartbeat latency (vs 50-100ms Flask)
- [x] **10x** faster queries (Redis cache)
- [x] **10,000+** concurrent WebSocket connections
- [x] **Async** task processing (non-blocking)
- [x] **Connection pooling** (PostgreSQL)
- [x] **Load balancing** (Nginx + Gunicorn)

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│           Nginx (Reverse Proxy)         │
│         SSL/TLS + Load Balancer         │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────┐
│Gunicorn │     │ Daphne   │
│  (HTTP) │     │(WebSocket)│
│8 workers│     │  ASGI    │
└────┬────┘     └────┬─────┘
     │               │
     └───────┬───────┘
             ▼
    ┌────────────────┐
    │ Django 5.0     │
    │ asosiy project │
    └────────┬───────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│c2_agents │    │ c2_core  │
│  (REST)  │    │(WebSocket)│
└──────────┘    └──────────┘
     │                │
     └────────┬───────┘
              ▼
    ┌────────────────────┐
    │  Celery Workers    │
    │  (Async Tasks)     │
    └─────────┬──────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌──────────┐      ┌───────────┐
│PostgreSQL│      │   Redis   │
│(Database)│      │(Cache+Queue)│
└──────────┘      └───────────┘
```
# Start Celery beat
celery -A asosiy beat -l info

# Start Gunicorn (HTTP)
gunicorn asosiy.wsgi:application --config server/gunicorn_config.py

# Start Daphne (WebSocket)
daphne -b 0.0.0.0 -p 8001 asosiy.asgi:application
```

### Barcha Scriptlar:
```bash
# Server
scripts/start_server.bat        # Django server (HTTP + WebSocket)
scripts/start_tcp_server.bat    # TCP socket server

# Agent
scripts/start_tcp_agent.bat     # TCP agent client

# GUI
scripts/start_havoc_gui.bat     # Havoc-style main GUI
scripts/start_payload_gui.bat   # Payload Generator GUI

# CLI
scripts/start_cli.bat            # Command line interface
scripts/start_payload_generator.bat  # Payload CLI
```

## 🎯 Xususiyatlar

### Asosiy Framework
- [x] HTTP Flask server (Development)
- [x] TCP Socket server  
- [x] Django server (Production - 10,000+ users)
- [x] HTTP/TCP agentlar
- [x] Havoc-style GUI
- [x] CLI interface

### Professional Features
- [x] **Listener Management** - HTTP, TCP listeners
- [x] **Payload Generator** - 15 format (Python, PowerShell, EXE, DLL, JPG, PNG, PDF)
- [x] **Payload GUI** - Grafik interfeys, HTTP/TCP tanlash
- [x] **Session Management** - Agent monitoring
- [x] **Command System** - Shell, PowerShell, file operations
- [x] **Scalability** - 10,000+ concurrent users (Django)
- [x] **WebSocket** - Real-time communication
- [x] **Async Tasks** - Celery + Redis

## Dokumentatsiya

- [README.md](README.md) - Asosiy qo'llanma
- [docs/PAYLOAD_GENERATOR.md](docs/PAYLOAD_GENERATOR.md) - Payload yaratish (CLI)
- [docs/GUI_PAYLOAD_GENERATOR.md](docs/GUI_PAYLOAD_GENERATOR.md) - Grafik payload generator
- [docs/STEGANOGRAPHY_PAYLOADS.md](docs/STEGANOGRAPHY_PAYLOADS.md) - JPG/PNG/PDF polyglot

## Litsenziya

Faqat ta'lim maqsadida.