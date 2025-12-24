@echo off
REM C2 Platform - Quick Start
echo ============================================
echo   C2 Platform - Quick Start
echo ============================================
echo.
echo Tanlang:
echo.
echo [1] CLI Mode - Terminal interface
echo [2] GUI Mode - Visual interface
echo [3] Full Stack - Django + All Servers
echo [4] Exit
echo.
set /p choice="Tanlang (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting CLI Mode...
    call scripts\START_CLI.bat
) else if "%choice%"=="2" (
    echo.
    echo Starting GUI Mode...
    call scripts\START_GUI.bat
) else if "%choice%"=="3" (
    echo.
    echo Starting Full Stack...
    call scripts\START_ALL.bat
) else if "%choice%"=="4" (
    exit
) else (
    echo Invalid choice!
    pause
)
