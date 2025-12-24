@echo off
REM C2 Platform - GUI Mode
echo ============================================
echo   C2 Platform - GUI Mode
echo ============================================
echo.

REM Server'ni background'da ishga tushirish
echo [1/2] Starting TCP Server (no CLI)...
start "C2 TCP Server" cmd /k python server\tcp_server.py --no-cli
timeout /t 3 /nobreak >nul

REM GUI'ni ishga tushirish
echo [2/2] Starting GUI...
python gui\tcp_server_gui.py

echo.
echo Done!
pause
