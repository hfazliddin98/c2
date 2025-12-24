#!/bin/bash
# C2 Platform - Full Monitoring GUI

echo "============================================"
echo "  C2 Platform - Full Monitoring GUI"
echo "============================================"
echo ""
echo "Starting monitoring interface..."
echo ""

cd "$(dirname "$0")/.."
python3 gui/monitoring_gui.py
