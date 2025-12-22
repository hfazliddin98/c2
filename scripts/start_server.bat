@echo off
REM C2 Platform - Production Server (Windows)
REM waitress-serve bilan

title C2 Platform - Production Server
color 0A

echo ================================================
echo      C2 Platform - Production Server
echo ================================================
echo.

REM Virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
)

REM waitress o'rnatish (Windows uchun yaxshi)
echo [1/2] waitress o'rnatilmoqda...
pip install waitress eventlet >nul 2>&1

REM Server ishga tushirish
echo [2/2] Production server ishga tushirilmoqda...
echo.
echo Workers: Auto (CPU cores)
echo Bind: 0.0.0.0:8080
echo.
echo Dashboard: http://127.0.0.1:8080
echo.

cd server

REM waitress-serve (Windows uchun eng yaxshi)
waitress-serve --host=0.0.0.0 --port=8080 --threads=8 --channel-timeout=120 app:app

REM Yoki eventlet
REM python -c "from app import app, socketio; socketio.run(app, host='0.0.0.0', port=8080)"

pause
