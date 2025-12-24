# C2 Platform Deployment Guide

Server hostingga qo'yish bo'yicha to'liq qo'llanma

---

## 📋 Deployment Variantlari

| Hosting | Narx | SSL | Difficulty | Tavsiya |
|---------|------|-----|------------|---------|
| **PythonAnywhere** | Bepul tier bor | ✅ Auto | ⭐⭐ Oson | Yangi boshlovchilar uchun |
| **Railway** | $5/oy | ✅ Auto | ⭐⭐ Oson | Modern, oson |
| **Render** | Bepul tier bor | ✅ Auto | ⭐⭐ Oson | GitHub integratsiya |
| **Heroku** | $7/oy | ✅ Auto | ⭐⭐⭐ O'rtacha | Keng tarqalgan |
| **DigitalOcean** | $6/oy | ❌ Manual | ⭐⭐⭐⭐ Qiyin | To'liq nazorat |
| **AWS EC2** | $5-10/oy | ❌ Manual | ⭐⭐⭐⭐⭐ Juda qiyin | Enterprise |
| **VPS (Ubuntu)** | $5+/oy | ❌ Manual | ⭐⭐⭐⭐ Qiyin | Maxsus konfiguratsiya |

---

## 🌟 1. PythonAnywhere (BEPUL) - ENG OSON

### ✅ Afzalliklari:
- Bepul tier (500MB disk, 1 web app)
- SSL sertifikat bepul
- Web-based console
- Python 3.10 support
- Oson setup

### ⚠️ Cheklovlar:
- Outbound connections bloklangan (agent uchun muammo!)
- Static IP yo'q
- 100 sekund CPU/day (free tier)
- Only WSGI (WebSocket ishlamaydi)

### 📝 Qo'yish Bosqichlari:

#### 1. Account yaratish
```
https://www.pythonanywhere.com/registration/
```

#### 2. Bash Console ochish
```bash
# Git clone
git clone https://github.com/yourusername/c2.git
cd c2

# Virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Requirements
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Settings.py sozlash
```python
# asosiy/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# Static files
STATIC_ROOT = '/home/yourusername/c2/staticfiles'

# Database (SQLite yoki)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/c2/db.sqlite3',
    }
}

# Security (PythonAnywhere HTTPS)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 4. Web App sozlash
PythonAnywhere Dashboard:
- Web tab → Add a new web app
- Python 3.10
- Manual configuration
- **Source code:** `/home/yourusername/c2`
- **Working directory:** `/home/yourusername/c2`

#### 5. WSGI Configuration
`/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import os
import sys

path = '/home/yourusername/c2'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'asosiy.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 6. Static files
```bash
python manage.py collectstatic --noinput
```

#### 7. Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 8. Reload
PythonAnywhere Dashboard → Web → Reload

**URL:** `https://yourusername.pythonanywhere.com`

### ❌ Muammo: Agent ulanish ishlamaydi!
PythonAnywhere outbound connections bloklaydi, shuning uchun **agent server uchun mos emas**.

**Yechim:** Faqat Controller (GUI/CLI) uchun ishlatish, agent serverni boshqa joyga deploy qilish.

---

## 🚂 2. Railway (TAVSIYA QILINADI) - $5/oy

### ✅ Afzalliklari:
- Modern UI
- GitHub auto-deploy
- SSL bepul
- Outbound connections ruxsat
- PostgreSQL bepul
- WebSocket support

### 📝 Qo'yish Bosqichlari:

#### 1. railway.json yaratish
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn asosiy.wsgi:application --bind 0.0.0.0:$PORT --workers 4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. requirements.txt yangilash
```bash
# Add
gunicorn==21.2.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
whitenoise==6.6.0
```

#### 3. settings.py yangilash
```python
import dj_database_url

# Railway environment
if os.environ.get('RAILWAY_ENVIRONMENT'):
    DEBUG = False
    ALLOWED_HOSTS = ['*']  # Railway domain
    
    # Database (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600
        )
    }
    
    # Static files
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

#### 4. Procfile yaratish
```
web: gunicorn asosiy.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

#### 5. Railway Deploy
```bash
# Railway CLI
npm i -g @railway/cli
railway login
railway init
railway up
```

Yoki GitHub orqali:
- Railway.app → New Project
- GitHub repo connect
- Auto-deploy

**URL:** `https://c2-production.up.railway.app`

---

## 🎨 3. Render (BEPUL TIER) - GitHub Integration

### ✅ Afzalliklari:
- Bepul tier
- SSL bepul
- GitHub auto-deploy
- PostgreSQL bepul
- Easy setup

### ⚠️ Cheklovlar:
- Free tier: 750 soat/oy
- Cold start (15s)
- 512MB RAM

### 📝 Qo'yish Bosqichlari:

#### 1. render.yaml yaratish
```yaml
services:
  - type: web
    name: c2-platform
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate"
    startCommand: "gunicorn asosiy.wsgi:application --bind 0.0.0.0:$PORT --workers 2"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DJANGO_SETTINGS_MODULE
        value: asosiy.settings
      - key: DEBUG
        value: False
```

#### 2. Render Dashboard
- render.com → New Web Service
- GitHub repo connect
- Auto-detect Django
- Deploy

**URL:** `https://c2-platform.onrender.com`

---

## 🌊 4. DigitalOcean Droplet - $6/oy

### ✅ Afzalliklari:
- To'liq nazorat
- Root access
- Multiple apps
- Scalable

### 📝 Qo'yish Bosqichlari:

#### 1. Droplet yaratish
```
- OS: Ubuntu 22.04
- Plan: Basic $6/oy (1GB RAM)
- Region: Singapore yoki yaqin
```

#### 2. Server setup
```bash
# SSH orqali ulanish
ssh root@your_server_ip

# Update
apt update && apt upgrade -y

# Python 3.10
apt install python3.10 python3.10-venv python3-pip -y

# Nginx
apt install nginx -y

# Git
apt install git -y

# Clone project
cd /var/www
git clone https://github.com/yourusername/c2.git
cd c2

# Virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Environment sozlash
```bash
# .env file
nano .env
```
```
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your_domain.com,your_server_ip
DATABASE_URL=sqlite:///db.sqlite3
```

#### 4. Gunicorn service
```bash
nano /etc/systemd/system/c2.service
```
```ini
[Unit]
Description=C2 Platform Gunicorn
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/c2
Environment="PATH=/var/www/c2/venv/bin"
ExecStart=/var/www/c2/venv/bin/gunicorn --workers 3 --bind unix:/var/www/c2/c2.sock asosiy.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 5. Nginx sozlash
```bash
nano /etc/nginx/sites-available/c2
```
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/c2;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/c2/c2.sock;
    }
}
```

#### 6. Enable va start
```bash
# Nginx
ln -s /etc/nginx/sites-available/c2 /etc/nginx/sites-enabled
nginx -t
systemctl restart nginx

# Gunicorn
systemctl start c2
systemctl enable c2

# Firewall
ufw allow 80
ufw allow 443
ufw allow 22
ufw enable
```

#### 7. SSL (Let's Encrypt)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your_domain.com
```

**URL:** `https://your_domain.com`

---

## 🔧 5. VPS Custom Setup (Ubuntu)

### Nginx + Gunicorn + Supervisor

#### 1. Install dependencies
```bash
apt update
apt install python3.10 python3.10-venv python3-pip nginx supervisor git -y
```

#### 2. Project setup
```bash
cd /opt
git clone https://github.com/yourusername/c2.git
cd c2

python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

#### 3. Django setup
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Supervisor config
```bash
nano /etc/supervisor/conf.d/c2.conf
```
```ini
[program:c2_gunicorn]
directory=/opt/c2
command=/opt/c2/venv/bin/gunicorn asosiy.wsgi:application --bind 127.0.0.1:8000 --workers 4
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/c2/gunicorn.log
```

#### 5. Start services
```bash
supervisorctl reread
supervisorctl update
supervisorctl start c2_gunicorn
```

---

## 📊 Qaysi Hostingni Tanlash?

### Yangi boshlovchilar uchun:
🥇 **Railway** - Eng oson, auto-deploy, $5/oy  
🥈 **Render** - Bepul tier, GitHub integration  
🥉 **PythonAnywhere** - Bepul, lekin agent ishlamaydi

### Agent + Controller uchun:
🥇 **Railway** - WebSocket + Outbound support  
🥈 **DigitalOcean** - To'liq nazorat  
🥉 **VPS** - Custom setup

### Production uchun:
🥇 **DigitalOcean** - Scalable, reliable  
🥈 **AWS EC2** - Enterprise-level  
🥉 **VPS** - Arzon, ishonchli

---

## 🚀 Qo'shimcha Fayllar

### requirements.txt (Production)
```txt
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
channels==4.0.0
daphne==4.0.0
gunicorn==21.2.0
uvicorn[standard]==0.25.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
python-decouple==3.8
cryptography==41.0.7
Pillow==12.0.0
```

### .env Template
```bash
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

### Dockerfile (Docker deployment)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "asosiy.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## ✅ Deployment Checklist

### Pre-deployment:
- [ ] DEBUG = False
- [ ] SECRET_KEY environment variable
- [ ] ALLOWED_HOSTS to'g'ri
- [ ] Static files collected
- [ ] Database migrations
- [ ] Superuser created
- [ ] SSL certificate (production)

### Security:
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Strong SECRET_KEY
- [ ] Firewall configured
- [ ] Regular backups

### Performance:
- [ ] Gunicorn workers (CPU cores × 2 + 1)
- [ ] Redis caching
- [ ] Static files CDN (optional)
- [ ] Database optimization
- [ ] Monitoring setup

---

## 🎯 Tavsiya

**Eng yaxshi variant - Railway:**

1. GitHub repo yarating
2. Railway.app ga login
3. GitHub connect
4. Auto-deploy
5. Environment variables sozlang
6. Deploy!

**URL:** `https://c2-production.up.railway.app`

**Cost:** $5/oy, SSL bepul, WebSocket support, outbound connections ✅

---

## 📝 Xulosa

| Use Case | Recommended Hosting |
|----------|-------------------|
| Learning/Testing | **PythonAnywhere** (bepul) |
| Full C2 Platform | **Railway** ($5/oy) |
| Production | **DigitalOcean** ($6/oy) |
| Enterprise | **AWS EC2** |

**Warning:** C2 platformani faqat o'quv maqsadida deploy qiling. Production uchun qonuniy ruxsat kerak!
