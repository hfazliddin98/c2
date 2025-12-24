#!/bin/bash
# C2 Platform - CLI Mode

echo "============================================"
echo "  C2 Platform - CLI Mode"
echo "============================================"
echo ""

echo "Starting TCP Server with CLI..."
cd "$(dirname "$0")/.."
python3 server/tcp_server.py

# Virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Dependencies
echo -e "${YELLOW}📦 Dependencies tekshirilmoqda...${NC}"
pip3 install -r requirements.txt > /dev/null 2>&1

# CLI ishga tushirish
echo -e "${GREEN}💻 CLI ishga tushirilmoqda...${NC}"
echo ""

cd server
python3 cli.py
