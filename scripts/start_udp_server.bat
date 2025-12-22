@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   UDP C2 Server - Tez va Engil Protokol
echo ====================================================
echo.
python server\udp_server.py
pause
