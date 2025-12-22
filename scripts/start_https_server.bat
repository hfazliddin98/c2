@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   HTTPS C2 Server - Secure Encrypted Communication
echo   SSL/TLS Shifrlangan Aloqa
echo ====================================================
echo.
echo GLOBAL ULANISH uchun:
echo   1. Router'da port forwarding: 8443
echo   2. Firewall'da ruxsat bering
echo   3. Public IP: https://YOUR_IP:8443/
echo.
python server\https_server.py
pause
