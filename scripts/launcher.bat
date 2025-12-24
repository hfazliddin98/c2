@echo off
REM C2 Platform - Django Production Launcher

echo.
echo ================================
echo    C2 PLATFORM (DJANGO)
echo ================================
echo.
echo [1] Setup Django
echo [2] Start Django Server
echo [3] Start TCP Server
echo [4] Start TCP Agent
echo [5] Start Havoc GUI
echo [6] Start CLI
echo [7] Start Payload Generator GUI
echo [8] Start Payload Generator CLI
echo.
set /p choice="Tanlang (1-8): "

if "%choice%"=="1" call scripts\setup.bat
if "%choice%"=="2" call scripts\start_server.bat
if "%choice%"=="3" call scripts\start_tcp_server.bat
if "%choice%"=="4" call scripts\start_tcp_agent.bat
if "%choice%"=="5" call scripts\start_havoc_gui.bat
if "%choice%"=="6" call scripts\start_cli.bat
if "%choice%"=="7" call scripts\start_payload_gui.bat
if "%choice%"=="8" call scripts\start_payload_generator.bat

pause
