# Controller-Server Aloqa Xavfsizligi

## ⚠️ HOZIRGI HOLAT: SHIFIRLANMAGAN!

Controller (GUI/CLI) va Server orasidagi aloqa **hozirda shifirlanmagan HTTP** orqali amalga oshirilmoqda.

---

## 📊 XAVFSIZLIK TAHLILI

### Hozirgi Aloqa Protokollari

| Controller | Server | Protocol | Encryption | Xavf |
|------------|--------|----------|------------|------|
| **GUI** → Django API | HTTP | `requests` | ❌ NO | 🔴 95% |
| **CLI** → Django API | HTTP | `requests` | ❌ NO | 🔴 95% |
| **Agent** → TCP Server | TCP | AES-256 | ✅ YES | 🟢 5% |

### Xavf Tahlili

**Controller → Server (HTTP):**
```python
# GUI (havoc_gui.py)
self.server_url = "http://localhost:8000"
response = requests.get(f"{self.server_url}/api/agents")

# CLI (cli.py)
self.server_url = "http://localhost:8000"
response = requests.get(f"{self.server_url}/api/agents")
```

**Muammolar:**
- ❌ HTTP (shifirlanmagan)
- ❌ Authentication yo'q
- ❌ CSRF protection kam
- ❌ Network sniffing mumkin
- ❌ MITM attack mumkin

**Xavf:** 95% (Agent-Server kabi)

---

## ✅ YECHIM: HTTPS + AUTHENTICATION

### Option 1: HTTPS bilan (Tavsiya Etiladi)

**Django Settings:**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**GUI Update:**
```python
# havoc_gui.py
self.server_url = "https://localhost:8443"  # HTTPS!
self.session.verify = '/path/to/cert.pem'   # SSL verification
```

**CLI Update:**
```python
# cli.py
self.server_url = "https://localhost:8443"  # HTTPS!
self.session.verify = '/path/to/cert.pem'
```

**Xavf Kamayishi:** 95% → 5% (90% yaxshilanish)

---

### Option 2: JWT Token Authentication

**Django Implementation:**
```python
# Install
pip install djangorestframework-simplejwt

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# urls.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
]
```

**GUI Login:**
```python
# havoc_gui.py
def login(self, username, password):
    response = requests.post(
        f"{self.server_url}/api/token/",
        json={'username': username, 'password': password}
    )
    token = response.json()['access']
    self.session.headers['Authorization'] = f'Bearer {token}'
```

**Xavf Kamayishi:** Authentication + HTTPS = 98% xavfsiz

---

### Option 3: API Key Authentication

**Django Middleware:**
```python
# middleware.py
class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = 'SECRET_API_KEY_2025'
    
    def __call__(self, request):
        if request.path.startswith('/api/'):
            key = request.headers.get('X-API-Key')
            if key != self.api_key:
                return JsonResponse({'error': 'Invalid API key'}, status=401)
        return self.get_response(request)
```

**GUI Request:**
```python
# havoc_gui.py
self.session.headers['X-API-Key'] = 'SECRET_API_KEY_2025'
```

**Xavf Kamayishi:** 95% → 30% (API key sniffing mumkin, HTTPS kerak)

---

## 🚀 TAVSIYA ETILGAN YECHIM

### Full Security Stack

```python
# Django (HTTPS + JWT + CSRF)
HTTPS: SSL/TLS encryption
JWT: Token-based authentication
CSRF: Cross-Site Request Forgery protection
API Key: Additional layer

# GUI/CLI
HTTPS client
JWT token management
Certificate pinning
Request signing
```

### Implementation Priority

1. **HTTPS** - Transport layer encryption (CRITICAL)
2. **JWT Authentication** - User authentication (HIGH)
3. **API Key** - Service authentication (MEDIUM)
4. **Certificate Pinning** - MITM prevention (MEDIUM)
5. **Request Signing** - Integrity verification (LOW)

---

## 📊 TAQQOSLASH

### Oldin (HTTP)

```
GUI/CLI → HTTP → Django Server
 
Network sniffing: ✅ Barcha ma'lumotlar ko'rinadi
MITM attack: ✅ Ma'lumot o'zgartiriladi
Authentication: ❌ Yo'q
Xavf: 95%
```

### Keyin (HTTPS + JWT)

```
GUI/CLI → HTTPS + JWT → Django Server

Network sniffing: ❌ Encrypted data
MITM attack: ❌ Certificate pinning
Authentication: ✅ JWT tokens
Xavf: 2-5%
```

---

## 🛠️ IMPLEMENTATION STEPS

### Step 1: HTTPS Setup

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Django HTTPS (using gunicorn)
gunicorn asosiy.wsgi:application --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:8443
```

### Step 2: JWT Authentication

```bash
# Install JWT
pip install djangorestframework-simplejwt

# Add to settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### Step 3: Update GUI/CLI

```python
# GUI login screen
class LoginWindow:
    def login(self):
        response = requests.post(
            'https://localhost:8443/api/token/',
            json={'username': self.username, 'password': self.password},
            verify='cert.pem'
        )
        token = response.json()['access']
        self.session.headers['Authorization'] = f'Bearer {token}'
```

---

## 📋 CHECKLIST

### Backend (Django)

- [ ] HTTPS enabled (gunicorn with SSL)
- [ ] JWT authentication configured
- [ ] CSRF protection enabled
- [ ] Secure cookies (SESSION_COOKIE_SECURE)
- [ ] API key middleware (optional)

### Frontend (GUI/CLI)

- [ ] HTTPS URL (https://localhost:8443)
- [ ] SSL certificate verification
- [ ] Login screen (username/password)
- [ ] Token storage and refresh
- [ ] Certificate pinning (optional)

### Testing

- [ ] HTTPS connection test
- [ ] JWT token generation test
- [ ] Token refresh test
- [ ] API authentication test
- [ ] Wireshark verification (encrypted traffic)

---

## 🎯 FINAL RECOMMENDATION

**Controller-Server aloqa shifrlash MAJBURIY!**

**Minimal Setup:**
```
1. HTTPS (SSL/TLS)
2. JWT Authentication
3. SSL Certificate Verification
```

**Xavfsizlik Yaxshilanish:** 95% → 5% (90% kamayish)

**Implementation Time:** 2-3 soat

---

## 📖 SUMMARY

**Savol:** Boshqaruv paneli va server aloqasi ham shiferlangan yoki yo'q?

**Javob:** 

**HOZIR:** ❌ **YO'Q** - HTTP shifirlanmagan (95% xavf)

**KERAK:** ✅ **HA** - HTTPS + JWT (5% xavf)

**Yechim:**
1. HTTPS (SSL/TLS) - Transport encryption
2. JWT - Authentication
3. Certificate pinning - MITM prevention

**Status:** ⚠️ CRITICAL - Controller-Server aloqani TEZDA shifrlash kerak!

---

**Hujjatlar:**
- [docs/ENCRYPTION_GUIDE.md](ENCRYPTION_GUIDE.md) - Agent encryption
- [docs/SECURITY_RISK_ANALYSIS.md](SECURITY_RISK_ANALYSIS.md) - Risk analysis
- [docs/CONTROLLER_SECURITY.md](CONTROLLER_SECURITY.md) - This file

**Next Steps:** HTTPS + JWT implementation (CRITICAL priority!)
