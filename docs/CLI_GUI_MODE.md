# CLI va GUI Ishlash Rejimi

## Muammo
CLI va GUI bir vaqtda ishlamaydi chunki CLI interaktiv rejimda ishlaydi va main thread'ni to'sadi.

## Yechim
Server'ga `--no-cli` parametri qo'shildi:

### 1. CLI Rejimi (Terminal foydalanuvchilari uchun)
```bash
# Windows
START_CLI.bat

# Linux/Mac
python server/tcp_server.py
```

**Xususiyatlari:**
- Interaktiv CLI
- Agent'lar bilan real-time muloqot
- Barcha komandalar terminalda

**CLI Komandalar:**
```
agents                       - Agentlar ro'yxati  
send <agent_id> <cmd> <args> - Komanda yuborish
remove <agent_id>            - Ro'yxatdan o'chirish
kill <agent_id>              - Agent'ni to'xtatish
commands                     - Barcha komandalar
status                       - Server holati
help                         - Yordam
quit                         - Chiqish
```

### 2. GUI Rejimi (Visual interface)
```bash
# Windows
START_GUI.bat

# Linux/Mac
./START_GUI.sh
```

**Xususiyatlari:**
- Modern visual interface
- Agent'larni ko'rish va boshqarish
- Quick commands
- Console logging

**Ishlash tartibi:**
1. Server --no-cli rejimda ishga tushadi (background)
2. GUI ochiladi va server'ga ulanadi
3. Ikkalasi parallel ishlaydi

## Manual Ishga Tushirish

### CLI Mode:
```bash
python server/tcp_server.py
```

### GUI Mode:
```bash
# Terminal 1: Server (no CLI)
python server/tcp_server.py --no-cli

# Terminal 2: GUI
python gui/tcp_server_gui.py
```

## Server Parametrlari

```bash
python server/tcp_server.py --help

Options:
  --host HOST         Server host (default: 0.0.0.0)
  --port PORT         Server port (default: 9999)
  --no-cli            CLI ni o'chirish (GUI uchun)
  --timeout TIMEOUT   Agent timeout in seconds (default: 30)
```

### Misollar:

```bash
# Boshqa portda ishga tushirish
python server/tcp_server.py --port 8888

# GUI rejimi, custom timeout
python server/tcp_server.py --no-cli --timeout 60

# CLI rejimi, custom host
python server/tcp_server.py --host 192.168.1.100
```

## Arxitektura

```
┌─────────────────┐
│   CLI Rejimi    │
│                 │
│  ┌───────────┐  │
│  │  Server   │  │
│  │ + CLI     │  │
│  └───────────┘  │
└─────────────────┘

┌─────────────────────────────────┐
│        GUI Rejimi               │
│                                 │
│  ┌───────────┐   ┌───────────┐ │
│  │  Server   │◄──┤    GUI    │ │
│  │ (no CLI)  │   │           │ │
│  └───────────┘   └───────────┘ │
└─────────────────────────────────┘
```

## Health Monitoring

Server har ikki rejimda ham agent health monitoring qiladi:
- **Timeout**: 30 soniya (default)
- **Health Check**: Har 5 soniyada
- **Status**: ACTIVE / INACTIVE

Agent 30 soniya javob bermasa avtomatik INACTIVE bo'ladi.

## Tavsiyalar

**CLI uchun:**
- Terminal bilan ishlashni yaxshi ko'rganlar
- Scriptlar va automation
- SSH orqali masofaviy boshqarish

**GUI uchun:**
- Visual interface kerak bo'lganda
- Ko'p agent'lar bilan ishlash
- Quick commands
- Real-time monitoring

## Xatolarni tuzatish

### GUI ochilmayapti
```bash
# Server'ni --no-cli bilan ishga tushiring
python server/tcp_server.py --no-cli
```

### CLI ishlayapti lekin GUI ochilmayapti
- Ikkita terminalni alohida oching
- Birinchi terminalda: `python server/tcp_server.py --no-cli`
- Ikkinchi terminalda: `python gui/tcp_server_gui.py`

### Port band
```bash
# Boshqa port ishlatish
python server/tcp_server.py --port 8888
```

## Qo'shimcha

Agent ulanishi uchun server manzilini to'g'ri ko'rsating:

```python
# agent/tcp_client.py
SERVER_HOST = "10.0.0.45"  # Server IP
SERVER_PORT = 9999
```
