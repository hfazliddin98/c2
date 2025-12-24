#!/bin/bash
# C2 Platform - Quick Start

echo "============================================"
echo "  C2 Platform - Quick Start"
echo "============================================"
echo ""
echo "Tanlang:"
echo ""
echo "[1] CLI Mode - Terminal interface"
echo "[2] GUI Mode - Visual interface"
echo "[3] Full Stack - Django + All Servers"
echo "[4] Exit"
echo ""
read -p "Tanlang (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting CLI Mode..."
        bash scripts/START_CLI.sh
        ;;
    2)
        echo ""
        echo "Starting GUI Mode..."
        bash scripts/START_GUI.sh
        ;;
    3)
        echo ""
        echo "Starting Full Stack..."
        bash scripts/START_ALL.sh
        ;;
    4)
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        ;;
esac
