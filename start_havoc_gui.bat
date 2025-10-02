@echo off
echo ================================================
echo Havoc-Style C2 GUI ishga tushirilmoqda...
echo ================================================

cd /d "%~dp0"

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python o'rnatilmagan yoki PATH da yo'q
    pause
    exit /b 1
)

REM GUI ishga tushirish
echo 🚀 Havoc GUI ishga tushirilmoqda...
cd gui
python havoc_gui.py

pause