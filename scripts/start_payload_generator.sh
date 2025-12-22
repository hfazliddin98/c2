#!/bin/bash
# C2 Platform - Payload Generator Standalone
# Linux/macOS shell script

echo "============================================"
echo "   Payload Generator"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 topilmadi!"
    echo "Python3 o'rnatilganini tekshiring."
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Run payload generator
echo "Starting Payload Generator GUI..."
echo ""

python3 gui/payload_generator_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Payload Generator ishga tushmadi!"
    read -p "Press Enter to continue..."
fi
