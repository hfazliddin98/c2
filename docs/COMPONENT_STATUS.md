# Komponentlarning Holati va Vazifalari

## ✅ ISHLAB TURGAN KOMPONENTLAR

### 1️⃣ Health Checker - ✅ TO'LIQ ISHGA TUSHGAN

**Fayl:** `server/tcp_server.py` (205-qator)

**Vazifasi:**
```python
def health_checker(self):
    """Agent'larning sog'lig'ini tekshirish"""
    while self.running:
        # Har 5 soniyada:
        # 1. Barcha agent'larni tekshiradi
        # 2. last_seen vaqtini hisoblaydi
        # 3. Agar timeout > 30s bo'lsa → INACTIVE
        # 4. Agar 3 ta heartbeat o'tkazsa → INACTIVE
```

**Javob beradigan savollar:**
- ✅ Agent hali ishlab turibdimi?
- ✅ Agent qachon oxirgi marta javob berdi?
- ✅ Agent necha ta heartbeat o'tkazdi?
- ✅ Agent ACTIVE yoki INACTIVE?

**Ishlash printsipi:**
```
┌─────────────────┐
│ Health Checker  │ (Background Thread)
└────────┬────────┘
         │
         ├─► Har 5 soniya: Check all agents
         │
         ├─► Agent A: last_seen = 10s ago → ACTIVE ✅
         ├─► Agent B: last_seen = 35s ago → INACTIVE ❌
         └─► Agent C: missed_heartbeats = 4 → INACTIVE ❌
```

**Test qilish:**
```bash
# Server ishga tushiring
python server/tcp_server.py

# Log ko'rasiz:
[2025-12-24 10:00:00] [TCP-SERVER] 💓 Health checker thread boshlandi
[2025-12-24 10:00:00] [TCP-SERVER] 💓 Health checker ishga tushdi (timeout: 30s)

# Agent ulansin, keyin to'xtating
# 30 soniyadan keyin:
[2025-12-24 10:00:35] [TCP-SERVER] ⚠️ Agent timeout: 8ee97a39 (35s)
```

---

### 2️⃣ Session Manager - ✅ TO'LIQ ISHGA TUSHGAN

**Fayl:** `server/session_manager.py`

**Vazifasi:**
```python
class SessionManager:
    """Havoc-style session boshqaruv"""
    
    def __init__(self):
        # Agent session'larini saqlash
        self.sessions = {}
        self.command_queue = {}
        self.command_results = {}
        
        # Background monitoring
        self.monitoring_thread.start()
```

**Javob beradigan savollar:**
- ✅ Agent qachon ulanganini?
- ✅ Agent qaysi listener orqali ulanganini?
- ✅ Agent'ning to'liq ma'lumotlari (hostname, IP, OS, etc)?
- ✅ Nechta task bajarildi?
- ✅ Qancha data yuborildi/qabul qilindi?

**Session Ma'lumotlari:**
```python
SessionInfo:
    session_id: "8ee97a39-..."
    hostname: "USER-PC"
    username: "admin"
    os_version: "Windows 11"
    ip_internal: "192.168.1.100"
    ip_external: "8.8.8.8"
    first_checkin: "2025-12-24T10:00:00"
    last_checkin: "2025-12-24T10:05:00"
    status: "active"
    privileges: "admin"
    tasks_pending: 2
    tasks_completed: 15
```

**Funksiyalari:**
- `register_session()` - Yangi agent ro'yxatga olish
- `update_session()` - Session ma'lumotlarini yangilash
- `get_session()` - Session olish
- `get_all_sessions()` - Barcha sessionlar
- `remove_session()` - Session o'chirish
- `queue_command()` - Komanda qo'shish
- `get_pending_commands()` - Kutayotgan komandalar

**Monitoring Thread:**
```python
def _monitor_sessions(self):
    """Session'larni kuzatish"""
    while True:
        # 1. Uzoq vaqt javob bermagan session'larni topish
        # 2. Status'ni "lost" ga o'zgartirish
        # 3. Dead session'larni tozalash
        time.sleep(30)
```

---

### 3️⃣ Command Handler - ⚠️ QISMAN (Integratsiya kerak)

**Holat:** Kod yozilgan, lekin TCP Server bilan integratsiya qilinmagan

**Kutilgan fayl:** `server/command_handler.py` (YO'Q ❌)

**Mavjud funksiyalar:** TCP Server ichida qisman

**Kerakli bo'lgan vazifalar:**
```python
class CommandHandler:
    """Komandalarni boshqarish"""
    
    AVAILABLE_COMMANDS = {
        'sysinfo': {...},
        'screenshot': {...},
        'camera_photo': {...},
        # ... 23 ta komanda
    }
    
    def validate_command(cmd):
        # Komanda to'g'rimi?
        pass
    
    def detect_platform(agent_info):
        # Desktop yoki Mobile?
        pass
    
    def get_available_commands(platform):
        # Platformaga mos komandalar
        pass
```

**Javob berishi kerak bo'lgan savollar:**
- ✅ Bu komanda mavjudmi?
- ✅ Bu komanda ushbu platformada ishlaydimi?
- ✅ Komanda parametrlari to'g'rimi?
- ✅ Qanday komandalar mavjud?

**Hozirgi holat:**
- Komanda validatsiyasi YO'Q ❌
- Platform detection YO'Q ❌
- Komanda ro'yxati bor (23 ta) lekin alohida modulda emas ❌

---

### 4️⃣ Listener Manager - ✅ TO'LIQ ISHGA TUSHGAN

**Fayl:** `server/listener_manager.py`

**Vazifasi:**
```python
class ListenerManager:
    """Listener boshqaruv tizimi"""
    
    def create_http_listener(...)
    def create_tcp_listener(...)
    def start_listener(...)
    def stop_listener(...)
```

**Javob beradigan savollar:**
- ✅ Qanday listener'lar mavjud?
- ✅ Qaysi portlar ochiq?
- ✅ Nechta agent ulangan?
- ✅ Listener ishlayaptimi?

**Listener Turlari:**
- HTTP Listener (port 8080)
- HTTPS Listener (SSL)
- TCP Listener (port 9999)

**Ishlash sxemasi:**
```
Listener Manager
    │
    ├─► HTTP Listener (8080)
    │     └─► 5 agents connected
    │
    ├─► HTTPS Listener (8443)
    │     └─► 3 agents connected
    │
    └─► TCP Listener (9999) ← Current
          └─► 1 agent connected
```

---

## 📊 KOMPONENTLAR HOLATI

| Komponent | Holat | Fayl | Integratsiya |
|-----------|-------|------|--------------|
| Health Checker | ✅ Ishga tushgan | tcp_server.py | ✅ TCP Server |
| Session Manager | ✅ Ishga tushgan | session_manager.py | ⚠️ Alohida |
| Command Handler | ❌ Yo'q | - | ❌ Kerak |
| Listener Manager | ✅ Ishga tushgan | listener_manager.py | ⚠️ Alohida |

---

## 🔄 ULAR QANDAY ISHLASHI KERAK

### Ideal Integratsiya:

```python
# server/tcp_server.py

from server.session_manager import SessionManager
from server.command_handler import CommandHandler
from server.listener_manager import ListenerManager

class TCPServer:
    def __init__(self):
        # 1. Session Manager
        self.session_manager = SessionManager()
        
        # 2. Command Handler
        self.command_handler = CommandHandler()
        
        # 3. Health Checker (o'zida)
        self.health_checker_thread.start()
    
    def handle_client(self, client_socket, client_address):
        # 1. Session Manager'ga ro'yxatdan o'tkazish
        session_id = self.session_manager.register_session(client_info)
        
        while True:
            # 2. Command Handler orqali komanda yuborish
            commands = self.command_handler.get_pending_commands(session_id)
            
            # 3. Health Checker avtomatik ishlaydi (background)
```

---

## ✅ NIMA ISHLAYAPTI

### 1. Health Checker (100% ✅)
```bash
# Test qilish:
python server/tcp_server.py
# Agent ulansin
# 30s kutib to'xtating
# Status INACTIVE bo'ladi
```

### 2. Session Manager (80% ✅)
```bash
# Alohida ishlaydi, lekin TCP Server bilan bog'lanmagan
# Django API orqali foydalanish mumkin
```

### 3. Listener Manager (80% ✅)
```bash
# Alohida ishlaydi
# TCP Listener ishga tushirish mumkin
```

---

## ❌ NIMA ISHLAMAYAPTI

### 1. Command Handler (0% ❌)
- Alohida modul yo'q
- TCP Server'ga integratsiya qilinmagan
- Komanda validatsiyasi yo'q

**Yechim:** `server/command_handler.py` yaratish kerak

---

## 🎯 XULOSA

**Ishga tushgan:**
- ✅ Health Checker - To'liq ishlaydi
- ✅ Session Manager - Ishga tushgan, integratsiya qilish kerak
- ✅ Listener Manager - Ishga tushgan, alohida

**Ishlamayapti:**
- ❌ Command Handler - Modul yo'q, yaratish kerak

**Integration Status:**
```
TCP Server
    │
    ├─► Health Checker    ✅ Integratsiyalangan
    ├─► Session Manager   ⚠️ Alohida (integratsiya kerak)
    ├─► Command Handler   ❌ Yo'q (yaratish kerak)
    └─► Listener Manager  ⚠️ Alohida (ixtiyoriy)
```

**Tavsiya:**
1. Command Handler modulini yaratish
2. Session Manager'ni TCP Server'ga integratsiya qilish
3. Barcha komponentlar birgalikda ishlashi uchun refactoring

Hozircha **Health Checker** to'liq ishlayapti va agent'larni real-time monitoring qiladi! 🎉
