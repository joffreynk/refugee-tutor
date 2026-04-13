#!/bin/bash
# Camp Tutor - Start Robot

echo "========================================"
echo "  CAMP TUTOR ROBOT"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

# Run system test first
echo ""
echo "Running system test..."
python3 test_all.py

echo ""
echo "Starting Camp Tutor..."
python3 main.py
