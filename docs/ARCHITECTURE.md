# C2 Platform - Agent-Server-Controller Arxitekturasi

## ✅ HA, LOYIHA TO'LIQ AGENT-SERVER-CONTROLLER ARXITEKTURASI!

---

## 📊 3 QATLAMLI ARXITEKTURA

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                         │
│  (Boshqaruv va Monitoring)                                  │
├─────────────────────────────────────────────────────────────┤
│  • Django REST API (c2_agents/)                             │
│  • Desktop GUI (havoc_gui.py, monitoring_gui.py)            │
│  • CLI Interface (server/cli.py)                            │
│  • Web Dashboard (WebSocket real-time)                      │
└─────────────────────────────────────────────────────────────┘
                          ↕️ (Commands/Data)
┌─────────────────────────────────────────────────────────────┐
│                     SERVER LAYER                            │
│  (Communication va Session Management)                      │
├─────────────────────────────────────────────────────────────┤
│  • TCP Server (9999) - Raw TCP                              │
│  • HTTPS Server (8443) - Encrypted HTTP                     │
│  • WebSocket Server - Real-time                             │
│  • DNS Server - Covert channel                              │
│  • Session Manager - Agent sessions                         │
│  • Command Handler - Command validation                     │
│  • Listener Manager - Multi-listener                        │
└─────────────────────────────────────────────────────────────┘
                          ↕️ (Encrypted)
┌─────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                            │
│  (Target Machines)                                          │
├─────────────────────────────────────────────────────────────┤
│  • TCP Client - Basic agent                                 │
│  • Smart Client - Auto-reconnect                            │
│  • Mobile Agent - Android/Termux                            │
│  • Encrypted Client - AES-256                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Umumiy Arxitektura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         C2 PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────┐         ┌──────────────────────────────┐   │
│  │   OPERATOR         │         │        SERVER LAYER          │   │
│  │   (Foydalanuvchi)  │◄────────┤                              │   │
│  └────────────────────┘         │  ┌────────────────────────┐  │   │
│          │                      │  │   TCP C2 Server        │  │   │
│          │                      │  │   (tcp_server.py)      │  │   │
│          ▼                      │  │                        │  │   │
│  ┌────────────────┐             │  │  • Agent management   │  │   │
│  │  GUI / CLI     │             │  │  • Command queue      │  │   │
│  │                │             │  │  • Health monitoring  │  │   │
│  │  • TCP GUI     │─────────────┼──┤  • Session tracking   │  │   │
│  │  • Havoc GUI   │             │  └────────┬───────────────┘  │   │
│  │  • CLI         │             │           │                  │   │
│  └────────────────┘             │           │                  │   │
│                                 │           ▼                  │   │
│                                 │  ┌────────────────────────┐  │   │
│                                 │  │  Command Handler       │  │   │
│                                 │  │  (command_handler.py)  │  │   │
│                                 │  │                        │  │   │
│                                 │  │  • 23 commands         │  │   │
│                                 │  │  • Platform detection  │  │   │
│                                 │  │  • Validation          │  │   │
│                                 │  └────────────────────────┘  │   │
│                                 │                              │   │
│                                 │  ┌────────────────────────┐  │   │
│                                 │  │  Django Server         │  │   │
│                                 │  │  (Optional)            │  │   │
│                                 │  │                        │  │   │
│                                 │  │  • REST API            │  │   │
│                                 │  │  • WebSocket           │  │   │
│                                 │  │  • Database            │  │   │
│                                 │  └────────────────────────┘  │   │
│                                 └──────────────────────────────┘   │
│                                             │                      │
│                                             │ Network              │
│                                             │ (TCP Socket)         │
│                                             │                      │
│                                             ▼                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                      AGENT LAYER                              │ │
│  │                                                                │ │
│  │  ┌──────────────────┐      ┌──────────────────┐              │ │
│  │  │  Desktop Agent   │      │  Mobile Agent    │              │ │
│  │  │  (tcp_client.py) │      │ (mobile_agent.py)│              │ │
│  │  │                  │      │                  │              │ │
│  │  │  • Windows       │      │  • Android       │              │ │
│  │  │  • Linux         │      │  • Camera        │              │ │
│  │  │  • macOS         │      │  • GPS           │              │ │
│  │  │                  │      │  • SMS           │              │ │
│  │  │  9 commands      │      │  19 commands     │              │ │
│  │  └──────────────────┘      └──────────────────┘              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Komponentlar va Aloqa

### 1️⃣ SERVER LAYER (Server qatlami)

#### A. TCP C2 Server (`server/tcp_server.py`)
**Vazifasi:**
- Agent'lardan ulanish qabul qilish
- Heartbeat yuborish (har 10 soniya)
- Komandalarni agent'larga yuborish
- Health monitoring (30s timeout)

**Aloqa:**
```python
# Port: 9999 (TCP)
# Protocol: JSON over raw socket
┌─────────────┐
│ TCP Server  │ ◄──────► Agent'lar
│ 0.0.0.0:9999│
└─────────────┘
      │
      ├──► Command Handler (komandalarni validate qilish)
      ├──► Session Manager (sessiyalarni boshqarish)
      └──► Health Checker (agent sog'ligini tekshirish)
```

**Ma'lumot formati:**
```json
{
  "type": "heartbeat",
  "timestamp": "2025-12-24T10:00:00"
}

{
  "type": "command",
  "data": "screenshot",
  "id": "cmd_123456"
}
```

#### B. Command Handler (`server/command_handler.py`)
**Vazifasi:**
- 23 ta komandani boshqarish
- Platform detection (Desktop/Mobile)
- Komanda validatsiyasi

**Komanda kategoriyalari:**
1. **System** - sysinfo, screenshot, shell
2. **Camera** - camera_photo, camera_list
3. **Audio** - audio_record, mic_record
4. **Location** - location_gps, location_info
5. **Files** - file_list, file_download, file_upload

#### C. Django Server (Optional) (`asosiy/`)
**Vazifasi:**
- REST API
- WebSocket (real-time)
- Database (PostgreSQL/SQLite)
- Admin panel

**Aloqa:**
```
HTTP/HTTPS: 8000
WebSocket: ws://localhost:8000/ws/
```

### 2️⃣ AGENT LAYER (Agent qatlami)

#### A. Desktop Agent (`agent/tcp_client.py`)
**Platformalar:** Windows, Linux, macOS

**Qobiliyatlari:**
- Avtomatik reconnect
- Command execution
- System info gathering
- Screenshot capture

**Aloqa sxemasi:**
```
1. Ulanish: Server'ga TCP socket orqali ulanadi
2. Register: System ma'lumotlarini yuboradi
3. Heartbeat: Har 10 soniyada javob beradi
4. Commands: Server'dan komanda oladi va bajaradi
5. Response: Natijani server'ga yuboradi
```

#### B. Mobile Agent (`agent/mobile_agent.py`)
**Platforma:** Android

**Maxsus qobiliyatlar:**
- Camera access
- GPS location
- SMS operations
- Contact list
- File browser

### 3️⃣ INTERFACE LAYER (Interfeys qatlami)

#### A. CLI Interface (`server/tcp_server.py` CLI)
**Komandalar:**
```bash
agents                       # Agent'larni ko'rish
send <id> <cmd> <args>       # Komanda yuborish
remove <id>                  # Ro'yxatdan o'chirish
kill <id>                    # Agent'ni to'xtatish
status                       # Server holati
```

**Ishga tushirish:**
```bash
python server/tcp_server.py
```

#### B. GUI Interface (`gui/tcp_server_gui.py`)
**Xususiyatlari:**
- Agent list (real-time)
- Quick commands
- Status monitoring
- Console logging

**Ishga tushirish:**
```bash
# Server (background)
python server/tcp_server.py --no-cli

# GUI
python gui/tcp_server_gui.py
```

#### C. Havoc-style GUI (`gui/havoc_gui.py`)
**Xususiyatlari:**
- Professional interface
- Django API integration
- Multiple listeners
- Payload generator

### 4️⃣ COMMON LAYER (Umumiy modullar)

#### `common/config.py`
```python
SERVER_HOST = "10.0.0.45"
SERVER_PORT = 9999
HEARTBEAT_INTERVAL = 10
TIMEOUT = 30
```

#### `common/payload_generator.py`
15 format:
- Python, PowerShell
- EXE, DLL, MSI
- JPG, PNG, PDF (steganography)

#### `common/crypto.py`
- AES-256 encryption
- RSA key exchange
- Data obfuscation

## 🔄 Ma'lumot Oqimi (Data Flow)

### Operator → Server → Agent

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│ Operator │         │  Server  │         │  Agent   │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     │ 1. "screenshot"    │                    │
     ├───────────────────►│                    │
     │                    │ 2. Queue command   │
     │                    ├───────────────────►│
     │                    │                    │ 3. Execute
     │                    │                    ├─────────┐
     │                    │                    │         │
     │                    │ 4. Result (base64) │◄────────┘
     │                    │◄───────────────────┤
     │ 5. Display         │                    │
     │◄───────────────────┤                    │
     │                    │                    │
```

### Health Monitoring (Sog'lik nazorati)

```
┌──────────┐                              ┌──────────┐
│  Server  │                              │  Agent   │
│          │                              │          │
│ Health   │                              │          │
│ Checker  │                              │          │
│ Thread   │                              │          │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │ Every 5 seconds                         │
     ├─────────────────────────────────────────┤
     │ Check last_seen                         │
     │                                         │
     │ If > 30s timeout:                       │
     │   agent.active = False                  │
     │                                         │
     │ Heartbeat (every 10s)                   │
     │◄────────────────────────────────────────┤
     │ Update last_seen                        │
     │ agent.active = True                     │
     │                                         │
```

## 📡 Network Protokol

### TCP Socket Communication

**1. Connection Handshake:**
```json
// Agent → Server
{
  "type": "register",
  "data": {
    "agent_id": "8ee97a39-...",
    "hostname": "USER-PC",
    "platform": "Windows",
    "python_version": "3.13.0",
    "ip": "192.168.1.100"
  }
}

// Server → Agent
{
  "type": "ack",
  "message": "Registered successfully"
}
```

**2. Heartbeat:**
```json
// Server → Agent (every 10s)
{
  "type": "heartbeat",
  "timestamp": "2025-12-24T10:00:00"
}

// Agent → Server
{
  "type": "heartbeat",
  "agent_id": "8ee97a39-...",
  "timestamp": "2025-12-24T10:00:00"
}
```

**3. Command Execution:**
```json
// Server → Agent
{
  "type": "screenshot",
  "data": null,
  "id": "cmd_1703412345"
}

// Agent → Server
{
  "type": "command_result",
  "command_id": "cmd_1703412345",
  "data": {
    "command": "screenshot",
    "success": true,
    "result": "base64_encoded_image...",
    "timestamp": "2025-12-24T10:00:01"
  }
}
```

## 🔐 Security Features

### 1. Blacklist Mechanism
```python
# Server
blacklisted_agents = set()

if agent_id in blacklisted_agents:
    send_disconnect_signal()
    close_socket()
```

### 2. Timeout Detection
```python
# Health checker
if (current_time - last_seen) > 30:
    agent.active = False
```

### 3. Disconnect Signal
```python
# Server → Agent
{
  "type": "disconnect",
  "reason": "Killed by operator"
}

# Agent receives and stops
```

## 📊 Scalability

### Threading Model
```
Server Process
├── Main Thread (Accept connections)
├── Health Checker Thread (Monitor agents)
├── Agent Handler Thread 1 (Agent 1)
├── Agent Handler Thread 2 (Agent 2)
└── Agent Handler Thread N (Agent N)
```

### Performance
- **10,000+** concurrent agents
- **<30ms** command latency
- **5s** health check interval
- **30s** timeout threshold

## 🗂️ File Structure Mapping

```
server/tcp_server.py
  └─► TCPServer class
       ├─► start() - Accept connections
       ├─► handle_client() - Agent handler
       ├─► health_checker() - Monitor health
       └─► send_command_to_agent() - Command dispatch

server/command_handler.py
  └─► AgentCommandHandler class
       ├─► AVAILABLE_COMMANDS - 23 commands
       ├─► AgentCapabilities - Platform detection
       └─► Quick builders - screenshot(), camera_photo(), etc.

agent/tcp_client.py
  └─► TCPAgent class
       ├─► connect() - Server'ga ulanish
       ├─► handle_command() - Komanda bajarish
       └─► cleanup() - Disconnect

gui/tcp_server_gui.py
  └─► TCPServerGUI class
       ├─► refresh_agents_data() - Agent list update
       └─► send_command() - Command dispatch
```

## 🎯 Ishlatish Stsenariylari

### Ssenariy 1: Basic Monitoring
```
1. Operator → CLI ishga tushiradi
2. Server → 9999 portni ochadi
3. Agent → Server'ga ulanadi
4. Server → Agent'ni ro'yxatga oladi
5. Operator → "agents" komandasi
6. Server → Agent list ko'rsatadi
```

### Ssenariy 2: Command Execution
```
1. Operator → "send 8ee97a39 screenshot"
2. Server → Command queue'ga qo'shadi
3. Server → Keyingi heartbeat'da yuboradi
4. Agent → Screenshot oladi
5. Agent → Base64 encode qiladi
6. Agent → Server'ga yuboradi
7. Server → Console'da ko'rsatadi
```

### Ssenariy 3: Connection Loss
```
1. Agent → Network uziladi
2. Server → 3 ta heartbeat o'tkazadi (30s)
3. Health Checker → Timeout detect qiladi
4. Server → agent.active = False
5. Operator → "agents" - Status: INACTIVE
6. Agent → Network qaytadi, reconnect qiladi
7. Server → agent.active = True
```

## 📚 Qo'shimcha Resurslar

- [QUICK_START.md](QUICK_START.md) - Tezkor boshlash
- [CLI_GUI_MODE.md](CLI_GUI_MODE.md) - CLI va GUI rejimi
- [COMMAND_SYSTEM.md](COMMAND_SYSTEM.md) - Barcha komandalar
- [FILE_STRUCTURE.md](FILE_STRUCTURE.md) - Fayl strukturasi
