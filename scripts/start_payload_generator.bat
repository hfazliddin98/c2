@echo off
REM C2 Platform - Payload Generator Standalone
REM Windows batch script

echo ============================================
echo    Payload Generator
echo ============================================
echo.

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python topilmadi!
    echo Python o'rnatilganini tekshiring.
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Run payload generator
echo Starting Payload Generator GUI...
echo.

python gui\payload_generator_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Payload Generator ishga tushmadi!
    pause
)
