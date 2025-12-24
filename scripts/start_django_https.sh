#!/bin/bash
# Django HTTPS Server Launcher
# SSL/TLS bilan xavfsiz server

echo ""
echo "========================================"
echo "   DJANGO HTTPS SERVER"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

# Virtual environment
if [ -f venv_django/bin/activate ]; then
    source venv_django/bin/activate
fi

# Sertifikatni tekshirish
if [ ! -f certs/server.crt ]; then
    echo "[!] SSL sertifikat topilmadi!"
    echo "[*] Sertifikat yaratilmoqda..."
    python scripts/generate_ssl_cert.py
fi

echo "[*] Django HTTPS Server ishga tushirilmoqda..."
echo ""

# Django migrations
python manage.py migrate --noinput

# Superuser yaratish (agar mavjud bo'lmasa)
echo ""
echo "[*] Admin foydalanuvchi tekshirilmoqda..."
python -c "import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

echo ""
echo "[+] HTTPS Server tayyor!"
echo ""
echo "    URL: https://localhost:8443"
echo "    Admin: https://localhost:8443/admin/"
echo "    API: https://localhost:8443/api/"
echo "    Login: https://localhost:8443/api/auth/token/"
echo ""
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo "[*] Server ishga tushirilmoqda..."
echo ""

# Django runserver (SSL)
python server/start_django_https.py --host 0.0.0.0 --port 8443
