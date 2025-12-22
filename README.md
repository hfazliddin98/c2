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

## 📂 Tarkibi

- `asosiy/` - Django project (settings, urls, wsgi, asgi, celery)
- `c2_agents/` - Django app (models, views, tasks)
- `c2_core/` - Django app (consumers, routing, websocket)
- `server/` - TCP server, CLI, listener/session managers
- `agent/` - TCP agent client
- `common/` - Umumiy funksiyalar va payload generator
- `gui/` - Havoc-style GUI va Payload Generator GUI
- `scripts/` - Launcher scriptlar

## 🚀 Tezkor Ishga Tushirish

### 1. O'rnatish:
```bash
# Windows
scripts\setup.bat

# Linux/macOS
chmod +x scripts/setup.sh && scripts/setup.sh
```

### 2. Server ishga tushirish:
```bash
# Windows
scripts\start_server.bat

# Linux/macOS
scripts/start_server.sh
```

### 3. Interaktiv Launcher (Barchasi):
```bash
# Windows
launcher.bat

# Linux/macOS
./launcher.sh
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