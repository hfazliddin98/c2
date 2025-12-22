@echo off
cd /d "%~dp0\.."
echo.
echo ====================================================
echo   RTSP C2 Server - Video Streaming Covert Channel
echo   Video Stream Yashirin Kanal
echo ====================================================
echo.
python server\rtsp_server.py
pause
