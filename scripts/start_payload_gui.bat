@echo off
REM Payload Generator GUI starter
REM Bu script payload yaratish GUI'ni ishga tushiradi

title Payload Generator GUI
color 0A

echo.
echo ========================================
echo    C2 PAYLOAD GENERATOR GUI
echo ========================================
echo.
echo Starting graphical payload generator...
echo.

REM Python environment setup
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
)

REM GUI ishga tushirish
python gui\payload_generator_gui.py

echo.
echo ========================================
echo GUI closed
echo ========================================
pause
