#!/bin/bash
# Payload Generator GUI starter
# Bu script payload yaratish GUI'ni ishga tushiradi

echo ""
echo "========================================"
echo "   C2 PAYLOAD GENERATOR GUI"
echo "========================================"
echo ""
echo "Starting graphical payload generator..."
echo ""

# Python environment setup
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
    echo ""
fi

# GUI ishga tushirish
python3 gui/payload_generator_gui.py

echo ""
echo "========================================"
echo "GUI closed"
echo "========================================"
