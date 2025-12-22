@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   DNS Tunneling C2 Server - Firewall Bypass
echo ====================================================
echo.
python server\dns_server.py
pause
