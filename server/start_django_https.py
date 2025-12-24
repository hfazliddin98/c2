"""
Django HTTPS Server Launcher
SSL/TLS bilan Django serverni ishga tushiradi
"""

import os
import sys
import django
from pathlib import Path

# Django settings
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')

try:
    django.setup()
except Exception as e:
    print(f"[!] Django setup xatolik: {e}")
    sys.exit(1)

from django.conf import settings
from django.core.management import execute_from_command_line

def start_https_server(host='0.0.0.0', port=8443):
    """HTTPS serverni SSL sertifikat bilan ishga tushirish"""
    
    # SSL fayllarni tekshirish
    ssl_cert = settings.SSL_CERTIFICATE
    ssl_key = settings.SSL_PRIVATE_KEY
    
    if not ssl_cert.exists():
        print(f"\n[!] SSL sertifikat topilmadi: {ssl_cert}")
        print("[*] Iltimos, avval sertifikat yarating:")
        print("    python scripts/generate_ssl_cert.py")
        return False
    
    if not ssl_key.exists():
        print(f"\n[!] SSL private key topilmadi: {ssl_key}")
        print("[*] Iltimos, avval sertifikat yarating:")
        print("    python scripts/generate_ssl_cert.py")
        return False
    
    print("\n" + "="*60)
    print("   DJANGO HTTPS SERVER")
    print("="*60 + "\n")
    
    print(f"[+] SSL Certificate: {ssl_cert}")
    print(f"[+] SSL Private Key: {ssl_key}")
    print(f"[+] Server Address: https://{host}:{port}")
    print(f"[+] Admin Panel: https://{host}:{port}/admin/")
    print(f"[+] API Endpoint: https://{host}:{port}/api/")
    print(f"[+] JWT Login: https://{host}:{port}/api/auth/token/")
    print("\n[*] Server ishga tushirilmoqda...\n")
    
    # Django runserver_plus (SSL support bilan)
    try:
        # runserver_plus (django-extensions kerak)
        execute_from_command_line([
            'manage.py',
            'runserver_plus',
            f'{host}:{port}',
            '--cert-file', str(ssl_cert),
            '--key-file', str(ssl_key),
        ])
    except:
        # Fallback: gunicorn
        print("\n[!] django-extensions topilmadi, gunicorn ishlatilmoqda...")
        os.system(f'gunicorn asosiy.wsgi:application --bind {host}:{port} '
                  f'--certfile={ssl_cert} --keyfile={ssl_key} '
                  f'--workers=4 --timeout=120')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Django HTTPS Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=8443, help='Port number')
    
    args = parser.parse_args()
    start_https_server(args.host, args.port)
