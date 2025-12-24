# Render Deployment Guide - C2 Platform

## 🚀 Render.com ga Deploy Qilish

### 1️⃣ Tayorgarlik

**Kerakli fayllar (allaqachon yaratilgan):**
- ✅ `render.yaml` - Render konfiguratsiya
- ✅ `build.sh` - Build script
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Backup (Heroku-style)

**GitHub:**
```bash
# Git init (agar qilmagan bo'lsangiz)
git init
git add .
git commit -m "Ready for Render deployment"

# GitHub repo yarating va push qiling
git remote add origin https://github.com/yourusername/c2.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Render Account

1. [render.com](https://render.com) ga o'ting
2. Sign up (GitHub bilan login qiling)
3. Dashboard ochiladi

---

### 3️⃣ Deploy Qilish

#### Option 1: render.yaml orqali (TAVSIYA)

1. **New** → **Blueprint**
2. **Connect GitHub repository**
3. Repository tanlang (c2)
4. Render `render.yaml` ni auto-detect qiladi
5. **Apply** tugmasini bosing

✅ **Natija:** 
- Web Service: `c2-platform`
- PostgreSQL Database: `c2-database`
- Auto-deploy configured

#### Option 2: Manual setup

1. **New** → **Web Service**
2. **Connect GitHub repository**
3. Settings:
   - **Name:** `c2-platform`
   - **Region:** `Singapore` (yaqin)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn asosiy.wsgi:application --bind 0.0.0.0:$PORT --workers 2`

4. **Environment Variables:**
   ```
   SECRET_KEY = [Auto-generated]
   DEBUG = False
   PYTHON_VERSION = 3.10.0
   ```

5. **Create Web Service** tugmasini bosing

---

### 4️⃣ PostgreSQL Database Qo'shish

1. Dashboard → **New** → **PostgreSQL**
2. Settings:
   - **Name:** `c2-database`
   - **Region:** `Singapore`
   - **Plan:** `Free` (256MB RAM, 1GB disk)
3. **Create Database**

4. Web Service ga bog'lash:
   - Web Service → **Environment**
   - **Add Environment Variable**
   - Key: `DATABASE_URL`
   - Value: Internal Database URL (c2-database dan copy)

---

### 5️⃣ Environment Variables Sozlash

Web Service → **Environment** → **Add Environment Variable**:

```bash
# Required
SECRET_KEY = your-secret-key-here  # Render auto-generate qiladi
DEBUG = False
DATABASE_URL = [Auto from c2-database]

# Optional
ALLOWED_HOSTS = .onrender.com,yourdomain.com
CORS_ORIGINS = https://yourdomain.com
```

---

### 6️⃣ Deploy Monitoring

**Build Logs:**
- Web Service → **Logs**
- Build progress ko'rsatadi:
  ```
  🚀 Render Build Script Started...
  📦 Installing dependencies...
  📁 Collecting static files...
  🗄️ Running database migrations...
  👤 Creating superuser...
  ✅ Build completed successfully!
  ```

**Deploy Status:**
- ✅ Green: Live
- 🟡 Yellow: Deploying
- 🔴 Red: Failed

---

### 7️⃣ URL va Access

**Web Service URL:**
```
https://c2-platform.onrender.com
```

**Admin Panel:**
```
https://c2-platform.onrender.com/admin/
Username: admin
Password: admin123
```

**API Endpoints:**
```
https://c2-platform.onrender.com/api/
https://c2-platform.onrender.com/api/auth/token/  # JWT login
```

---

### 8️⃣ Custom Domain (Optional)

1. Web Service → **Settings** → **Custom Domains**
2. **Add Custom Domain**
3. Domain: `yourdomain.com`
4. DNS sozlash:
   ```
   Type: CNAME
   Name: www
   Value: c2-platform.onrender.com
   ```
5. SSL auto-enabled (Let's Encrypt)

---

### 9️⃣ Auto-Deploy Setup

**GitHub push orqali auto-deploy:**

1. Web Service → **Settings** → **Build & Deploy**
2. **Auto-Deploy:** `Yes` (default)
3. Har safar `main` branchga push qilsangiz auto-deploy

**Manual deploy:**
```bash
# Code update
git add .
git commit -m "Update code"
git push

# Render auto-deploy qiladi
```

---

### 🔟 Monitoring va Logs

**Real-time Logs:**
```
Web Service → Logs
```

**Metrics:**
- CPU usage
- Memory usage
- Request count
- Response time

**Health Check:**
Render avtomatik health check qiladi:
- URL: `https://c2-platform.onrender.com/`
- Interval: 30s
- Timeout: 10s

---

## 📊 Free Tier Limits

| Resource | Free Tier |
|----------|-----------|
| **Web Service** | 750 hours/month |
| **RAM** | 512 MB |
| **Disk** | Temporary |
| **Database** | 256 MB RAM, 1 GB disk |
| **Bandwidth** | 100 GB/month |
| **Build time** | 500 min/month |

**⚠️ Free tier cheklovlar:**
- 15 minutdan keyin sleep mode (inactivity)
- Cold start: 30-60s (birinchi request)
- 1 web service + 1 database bepul

---

## 🔧 Troubleshooting

### Build Failed

**Sabab:** Dependencies install xatolik

**Yechim:**
```bash
# Local test
pip install -r requirements.txt
python manage.py check
```

### Database Connection Error

**Sabab:** DATABASE_URL noto'g'ri

**Yechim:**
1. Database → **Connect** → Internal Connection String
2. Copy URL
3. Web Service → Environment → DATABASE_URL paste

### Static Files 404

**Sabab:** collectstatic ishlamagan

**Yechim:**
```bash
# build.sh ichida:
python manage.py collectstatic --no-input
```

### Superuser Not Found

**Manual yaratish:**
```bash
# Render Shell
python manage.py createsuperuser
```

---

## 🎯 Production Checklist

Deploy qilishdan oldin tekshiring:

- [ ] `DEBUG = False` (settings.py)
- [ ] `SECRET_KEY` environment variable
- [ ] `ALLOWED_HOSTS` to'g'ri
- [ ] `DATABASE_URL` configured
- [ ] `build.sh` executable (`chmod +x build.sh`)
- [ ] `requirements.txt` to'liq
- [ ] `.gitignore` to'g'ri (db.sqlite3, venv, etc.)
- [ ] Static files path to'g'ri
- [ ] CORS settings configured

---

## 🚀 Deploy Commands Cheat Sheet

```bash
# Local test
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Static files
python manage.py collectstatic --noinput

# Superuser
python manage.py createsuperuser

# Git push (auto-deploy)
git add .
git commit -m "Deploy to Render"
git push origin main
```

---

## 💰 Cost Estimate

**Free Tier:** $0/month
- 1 Web Service (750 hours)
- 1 PostgreSQL Database
- SSL certificate
- Auto-deploy

**Paid Plan (agar kerak bo'lsa):**
- Starter: $7/month (always-on, no sleep)
- Standard: $25/month (more RAM, faster)
- Database: $7/month (larger storage)

---

## 📝 Next Steps

1. ✅ Deploy muvaffaqiyatli
2. 🔒 Custom domain qo'shish (optional)
3. 📊 Monitoring setup (Sentry, etc.)
4. 🔐 Environment secrets qo'shish
5. 🚀 Production-ready!

---

## 🆘 Help & Support

**Render Docs:**
- https://render.com/docs
- https://render.com/docs/deploy-django

**C2 Platform:**
- GitHub Issues
- Documentation: `docs/DEPLOYMENT_GUIDE.md`

---

## ✅ Deploy Checklist Summary

```
1. ✅ GitHub repo created
2. ✅ render.yaml configured
3. ✅ build.sh executable
4. ✅ Render account
5. ✅ Blueprint deployed
6. ✅ Database connected
7. ✅ Environment variables set
8. ✅ Build successful
9. ✅ Web service live
10. ✅ Admin accessible

URL: https://c2-platform.onrender.com
Admin: admin / admin123
```

**🎉 DEPLOYMENT COMPLETE!**
