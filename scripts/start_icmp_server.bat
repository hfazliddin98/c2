@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   ICMP Tunneling C2 Server - Ping Covert Channel
echo   OGOHLANTIRISH: Administrator huquqlari kerak!
echo ====================================================
echo.
echo Administrator sifatida ishga tushiring!
echo.
python server\icmp_server.py
pause
