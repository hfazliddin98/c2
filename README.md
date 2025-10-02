# C2 Platform - Command and Control Framework

Bu Python'da yozilgan C2 (Command and Control) platformasidir. Bu loyiha faqat ta'lim maqsadida yaratilgan.

## ⚠️ Ogohlantirish

Bu dastur faqat **ta'lim va tadqiqot maqsadlarida** ishlatilishi kerak. Noqonuniy faoliyat uchun foydalanish man etiladi.

## Tarkibi

- `server/` - C2 server komponentlari
  - `app.py` - HTTP/Flask server (Web dashboard)  
  - `tcp_server.py` - TCP socket server (Raw protocol)
  - `cli.py` - Command line interface
- `agent/` - Target mashinada ishlaydigan agentlar
  - `client.py` - HTTP agent
  - `tcp_client.py` - TCP agent
- `common/` - Umumiy funksiyalar va utilities
- `web/` - Web dashboard interface (kelajakda)

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishlatish

### HTTP Server (Tavsiya etiladi):
```bash
start_server.bat     # Web dashboard bilan
```

### TCP Server (Professional):
```bash
start_tcp_server.bat # Raw socket server
```

### Agent (Client):
```bash
start_agent.bat      # HTTP agent
start_tcp_agent.bat  # TCP agent
```

### Havoc-Style GUI:
```bash
start_havoc_gui.bat  # Modern GUI interface
```

### CLI Interface:
```bash
start_cli.bat        # Command line interface
```

## 🎯 Havoc-Style Xususiyatlar

### Asosiy Framework
- [x] HTTP Flask server (Web dashboard)
- [x] TCP Socket server (Raw protocol)
- [x] HTTP agent client  
- [x] TCP agent client
- [x] Modern Havoc-style GUI interface
- [x] CLI interface (HTTP va TCP)

### Professional Features (Havoc-like)
- [x] **Listener Management** - HTTP, HTTPS, TCP listeners
- [x] **Payload Generator** - EXE, DLL, PowerShell, Python payloads
- [x] **Session Management** - Advanced agent metadata va monitoring
- [x] **Command System** - Shell, PowerShell, file operations
- [x] **File Browser** - Remote filesystem navigation
- [x] **Team Server** - Multi-operator support

### Security Features
- [x] Session encryption va authentication
- [x] Advanced command queuing
- [x] Process monitoring va injection (educational)
- [x] Privilege escalation detection
- [x] Stealth communication protocols

## Qo'shimcha Fayllar

- `demo.py` - To'liq demo ishga tushirish
- `start_cli.bat` - CLI ishga tushirish
- `STRUCTURE.md` - Loyiha strukturasi haqida

## Demo Ishga Tushirish

Eng oson yo'l:
```bash
python demo.py
```

Bu script avtomatik ravishda:
1. Dependencies o'rnatadi
2. Server ishga tushiradi
3. Agent ulaydi
4. Interaktiv menu ochadi

## Litsenziya

Bu loyiha faqat ta'lim maqsadida yaratilgan.