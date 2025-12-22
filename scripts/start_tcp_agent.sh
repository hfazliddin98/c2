#!/bin/bash
# C2 Platform - TCP Agent ishga tushirish (Linux/macOS)

echo "================================================"
echo "🤖 C2 Platform TCP Agent"
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

# Virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Dependencies
echo -e "${YELLOW}📦 Dependencies tekshirilmoqda...${NC}"
pip3 install -r requirements.txt > /dev/null 2>&1

# Agent ishga tushirish
echo -e "${GREEN}🤖 TCP Agent ishga tushirilmoqda...${NC}"
echo ""
echo "Server: 127.0.0.1:9999"
echo ""
echo "To'xtatish uchun: Ctrl+C"
echo ""

cd agent
python3 tcp_client.py
