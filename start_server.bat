@echo off
echo ================================================
echo C2 Platform Server ishga tushirilmoqda...
echo ================================================

cd /d "%~dp0"

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python o'rnatilmagan yoki PATH da yo'q
    pause
    exit /b 1
)

REM Dependencylar o'rnatish
echo 📦 Dependencylarni o'rnatish...
pip install -r requirements.txt

REM Server ishga tushirish
echo 🚀 Server ishga tushirilmoqda...
cd server
python app.py

pause