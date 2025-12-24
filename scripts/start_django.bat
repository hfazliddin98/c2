@echo off
echo ========================================
echo    C2 PLATFORM - DJANGO SERVER
echo ========================================
echo.

echo Django serverni ishga tushirish...
echo.

REM Network IP ni ko'rsatish
echo Network IP:
python common/network_helper.py
echo.

echo ========================================
echo Django Server: http://0.0.0.0:8000
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

pause
