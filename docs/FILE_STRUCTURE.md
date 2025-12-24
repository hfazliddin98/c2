# Loyiha Fayl Strukturasi

## ✅ Tartibga Keltirilgan Struktura

### 📁 ROOT Papka
Faqat asosiy fayllar:
- `README.md` - Asosiy dokumentatsiya
- `manage.py` - Django management
- `requirements.txt` - Python dependencies
- `QUICK_START.bat/sh` - Tezkor ishga tushirish
- `db.sqlite3` - Development database
- `start_all_servers.py` - Server orchestrator
- `test_*.py` - Test scriptlar

### 📚 docs/ - Barcha Dokumentatsiya
**11 ta .md fayl:**
- `QUICK_START.md` - Tezkor boshlash
- `STRUCTURE.md` - Arxitektura
- `CLI_GUI_MODE.md` - CLI va GUI rejimi
- `COMMAND_SYSTEM.md` - Komanda tizimi
- `ANDROID_SETUP.md` - Android agent setup
- `PAYLOAD_GENERATOR.md` - Payload generator
- `STEGANOGRAPHY_PAYLOADS.md` - Steganografiya
- `IP_MANAGEMENT_GUIDE.md` - IP boshqaruv
- `AUTO_IP_MANAGER_GUIDE.md` - Auto IP manager
- `DYNAMIC_IP_GUIDE.md` - Dynamic IP
- `GLOBAL_DEPLOYMENT.md` - Global deployment

### ⚙️ scripts/ - Barcha Scriptlar
**34 ta script (.bat va .sh):**

#### Ishga tushirish:
- `START_CLI.bat/sh` - CLI rejimi
- `START_GUI.bat/sh` - GUI rejimi
- `START_ALL.bat/sh` - Full stack
- `launcher.bat/sh` - Interaktiv launcher

#### Server scriptlar:
- `start_server.bat/sh` - Django server
- `start_tcp_server.bat/sh` - TCP server
- `start_websocket_server.bat` - WebSocket
- `start_https_server.bat` - HTTPS
- `start_dns_server.bat` - DNS
- `start_udp_server.bat` - UDP
- `start_icmp_server.bat` - ICMP
- `start_rtsp_server.bat` - RTSP

#### Agent scriptlar:
- `start_tcp_agent.bat/sh` - TCP agent

#### GUI scriptlar:
- `start_havoc_gui.bat/sh` - Havoc GUI
- `start_payload_gui.bat/sh` - Payload Generator GUI
- `start_payload_generator.bat/sh` - CLI Payload Gen

#### Setup scriptlar:
- `setup.bat/sh` - Virtual env setup
- `setup_auto_ip.bat/sh` - Auto IP setup
- `show_ip.bat/sh` - IP ko'rsatish

### 🖥️ server/ - Server Komponentlari
- `tcp_server.py` - Asosiy TCP C2 server
- `command_handler.py` - Komanda handler
- `cli.py` - CLI interface
- `session_manager.py` - Session boshqaruv
- `listener_manager.py` - Listener boshqaruv
- `*_server.py` - Turli protokol serverlari

### 🤖 agent/ - Agent Clients
- `tcp_client.py` - Desktop agent (Windows/Linux/Mac)
- `mobile_agent.py` - Mobile agent (Android)
- `smart_client.py` - Smart reconnect agent

### 🎨 gui/ - GUI Interfaces
- `tcp_server_gui.py` - Modern TCP GUI
- `havoc_gui.py` - Havoc-style interface
- `payload_generator_gui.py` - Payload generator
- `modular_gui.py` - Modular interface
- `screenshot_viewer.py` - Screenshot viewer
- `modules/` - GUI modules

### 📦 common/ - Umumiy Modullar
- `config.py` - Konfiguratsiya
- `utils.py` - Utility functions
- `payload_generator.py` - Payload generator
- `crypto.py` - Enkriptsiya
- `network_helper.py` - Network utilities
- `commands.py` - Komanda definitsiyalari
- `auto_ip_manager.py` - Auto IP manager

### ⚙️ Django Apps
- `asosiy/` - Django project settings
- `c2_agents/` - Agent management app
- `c2_core/` - Core C2 functionality

## 🎯 Ishga Tushirish

### Quick Start Menu:
```bash
# Windows
QUICK_START.bat

# Linux/Mac
./QUICK_START.sh
```

### To'g'ridan-to'g'ri:
```bash
# CLI rejimi
scripts\START_CLI.bat

# GUI rejimi
scripts\START_GUI.bat

# Full stack
scripts\START_ALL.bat
```

## 📊 Statistika

- **Root:** 7 ta asosiy fayl
- **Docs:** 11 ta .md fayl
- **Scripts:** 34 ta script
- **Server:** 12 ta server komponenti
- **Agent:** 3 ta agent turi
- **GUI:** 6 ta interface
- **Common:** 9 ta utility modul
- **Django:** 2 ta app

**Jami:** 80+ fayl, tartibli va tushunarliroq!

## 🔍 Qidiruv

Barcha dokumentatsiya: `docs/`  
Barcha scriptlar: `scripts/`  
Asosiy kod: `server/`, `agent/`, `gui/`, `common/`

Har qanday `.md`, `.bat`, `.sh` fayl endi o'z joyida!
