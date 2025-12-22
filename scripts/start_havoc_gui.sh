#!/bin/bash
# C2 Platform - Havoc GUI (Linux/macOS)

echo "================================================"
echo "🎯 C2 Platform Havoc GUI"
echo "================================================"
echo ""

# Ranglar
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 topilmadi!${NC}"
    exit 1
fi

# tkinter tekshirish (Linux uchun)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${RED}❌ tkinter topilmadi!${NC}"
        echo "O'rnatish:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  Fedora: sudo dnf install python3-tkinter"
        exit 1
    fi
fi

# Virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Dependencies
echo -e "${YELLOW}📦 Dependencies tekshirilmoqda...${NC}"
pip3 install -r requirements.txt > /dev/null 2>&1

# GUI ishga tushirish
echo -e "${GREEN}🎯 Havoc GUI ishga tushirilmoqda...${NC}"
echo ""

cd gui
python3 havoc_gui.py
