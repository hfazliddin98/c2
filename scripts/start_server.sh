#!/bin/bash
# C2 Platform - Production Server (Linux/macOS)
# Gunicorn bilan

echo "================================================"
echo "🚀 C2 Platform - Production Server"
echo "================================================"
echo ""

# Ranglar
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Gunicorn o'rnatish
echo -e "${YELLOW}📦 Gunicorn tekshirilmoqda...${NC}"
pip install gunicorn eventlet > /dev/null 2>&1

# Server ishga tushirish
echo -e "${GREEN}🚀 Production server ishga tushirilmoqda...${NC}"
echo ""
echo "Workers: $(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')"
echo "Bind: 0.0.0.0:8080"
echo "Worker Class: eventlet"
echo ""

cd server

gunicorn -c gunicorn_config.py \
    --bind 0.0.0.0:8080 \
    --worker-class eventlet \
    --workers $(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)') \
    --worker-connections 1000 \
    --timeout 120 \
    --log-level info \
    app:app

# Yoki oddiy:
# gunicorn -w 4 -k eventlet -b 0.0.0.0:8080 app:app
