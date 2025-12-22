# Scripts - Django Production Launchers

Barcha launcher scriptlar bu yerda.

## 📂 Scriptlar

### Setup:
- `setup.bat` / `setup.sh` - Django production setup

### Server:
- `start_server.bat` / `start_server.sh` - Django server (Gunicorn + Daphne)
- `start_tcp_server.bat` / `start_tcp_server.sh` - TCP socket server

### Agent:
- `start_tcp_agent.bat` / `start_tcp_agent.sh` - TCP agent client

### GUI:
- `start_havoc_gui.bat` / `start_havoc_gui.sh` - Havoc-style main GUI
- `start_payload_gui.bat` / `start_payload_gui.sh` - Payload Generator GUI

### CLI:
- `start_cli.bat` / `start_cli.sh` - Command line interface
- `start_payload_generator.bat` / `start_payload_generator.sh` - Payload CLI

## 🚀 Foydalanish

### Interaktiv (Tavsiya):
```bash
# Windows
..\launcher.bat

# Linux/macOS
../launcher.sh
```

### To'g'ridan-to'g'ri:
```bash
# Windows
setup.bat
start_server.bat

# Linux/macOS
chmod +x *.sh
./setup.sh
./start_server.sh
```
