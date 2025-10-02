@echo off
echo ================================================
echo C2 TCP Server ishga tushirilmoqda...
echo ================================================

cd /d "%~dp0"

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python o'rnatilmagan yoki PATH da yo'q
    pause
    exit /b 1
)

REM TCP Server ishga tushirish
echo 🚀 TCP Server ishga tushirilmoqda...
cd server
python tcp_server.py

pause