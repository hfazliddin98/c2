@echo off
REM SSL Sertifikat Generatori
REM C2 Platform uchun HTTPS sertifikat yaratadi

echo.
echo ========================================
echo   SSL SERTIFIKAT GENERATOR
echo ========================================
echo.

cd /d "%~dp0\.."
if not exist certs mkdir certs
cd certs

echo [*] SSL sertifikat yaratilmoqda...
echo.

REM Private key yaratish
openssl genrsa -out server.key 2048

REM Certificate Signing Request (CSR) yaratish
openssl req -new -key server.key -out server.csr -subj "/C=UZ/ST=Tashkent/L=Tashkent/O=C2Platform/OU=Security/CN=localhost"

REM Self-signed sertifikat yaratish (365 kun)
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

REM PEM format yaratish (Django uchun)
copy server.crt server.pem
type server.key >> server.pem

echo.
echo [+] SSL sertifikat muvaffaqiyatli yaratildi!
echo.
echo Fayllar:
echo   - certs\server.key  (Private Key)
echo   - certs\server.crt  (Certificate)
echo   - certs\server.pem  (Combined PEM)
echo.
echo [+] Django HTTPS serverni ishga tushirish mumkin
echo.

pause
