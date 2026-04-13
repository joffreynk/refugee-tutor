#!/bin/bash
# Camp Tutor - Pi Setup Script

echo "========================================"
echo "  CAMP TUTOR - PI SETUP"
echo "========================================"

# Update
echo ""
echo "[1] Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install system packages
echo ""
echo "[2] Installing system packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    mpg123 \
    espeak \
    i2c-tools \
    libopencv-dev \
    python3-opencv \
    raspi-config

# Enable interfaces
echo ""
echo "[3] Enabling interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Install Python packages
echo ""
echo "[4] Installing Python packages..."
pip3 install -r requirements_pi.txt

# Install REX firmware
echo ""
echo "[5] REX firmware..."
echo "  Upload rex_v2.ino to ESP32 via Arduino IDE"

# Done
echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Test: python3 test_all.py"
echo "Run:  python3 main.py"
echo ""
echo "Say: Hello Tutor Robot"
echo "========================================"