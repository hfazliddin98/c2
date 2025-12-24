#!/bin/bash
# C2 Platform - Django Production Launcher

echo ""
echo "================================"
echo "   C2 PLATFORM (DJANGO)"
echo "================================"
echo ""
echo "[1] Setup Django"
echo "[2] Start Django Server"
echo "[3] Start TCP Server"
echo "[4] Start TCP Agent"
echo "[5] Start Havoc GUI"
echo "[6] Start CLI"
echo "[7] Start Payload Generator GUI"
echo "[8] Start Payload Generator CLI"
echo ""
read -p "Tanlang (1-8): " choice

case $choice in
    1) bash scripts/setup.sh ;;
    2) bash scripts/start_server.sh ;;
    3) bash scripts/start_tcp_server.sh ;;
    4) bash scripts/start_tcp_agent.sh ;;
    5) bash scripts/start_havoc_gui.sh ;;
    6) bash scripts/start_cli.sh ;;
    7) bash scripts/start_payload_gui.sh ;;
    8) bash scripts/start_payload_generator.sh ;;
    *) echo "Noto'g'ri tanlov!" ;;
esac
