#!/bin/bash
# C2 Platform - GUI Mode

echo "============================================"
echo "  C2 Platform - GUI Mode"
echo "============================================"
echo ""

# Server'ni background'da ishga tushirish
echo "[1/2] Starting TCP Server (no CLI)..."
python3 server/tcp_server.py --no-cli &
SERVER_PID=$!
sleep 3

# GUI'ni ishga tushirish
echo "[2/2] Starting GUI..."
python3 gui/tcp_server_gui.py

# GUI yopilganda server'ni to'xtatish
kill $SERVER_PID 2>/dev/null

echo ""
echo "Done!"
