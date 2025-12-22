@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   WebSocket C2 Server - Real-time Communication
echo ====================================================
echo.
python server\websocket_server.py
pause
