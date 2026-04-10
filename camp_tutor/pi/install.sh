#!/bin/bash

# Camp Tutor - Dependency Installation Script
# Run on Raspberry Pi: chmod +x install.sh && ./install.sh

set -e

echo "========================================="
echo "  Camp Tutor - Installation Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 1: Updating system..."
echo "========================================="
sudo apt update && sudo apt upgrade -y

echo ""
echo "Step 2: Installing system dependencies..."
echo "========================================="
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-full \
    python3-dev \
    espeak \
    festival \
    mpg123 \
    portaudio19-dev \
    libportaudio2 \
    libopencv-dev \
    libcap-dev \
    git \
    network-manager \
    i2c-tools \
    raspi-config \
    python3-raspberry-gpio

echo ""
echo "Step 3: Creating virtual environment..."
echo "========================================="

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
else
    echo "Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip in venv
pip3 install --upgrade pip setuptools wheel

echo ""
echo "Step 4: Installing Python packages..."
echo "========================================="

# Function to install package if not already installed
install_if_missing() {
    package=$1
    extra_args="${2:-}"
    if pip3 show "$package" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $package already installed"
    else
        echo -e "${YELLOW}Installing${NC} $package..."
        pip3 install $extra_args "$package" || echo -e "${RED}✗${NC} Failed to install $package"
    fi
}

echo "Installing core packages..."
install_if_missing "flask"
install_if_missing "werkzeug"
install_if_missing "numpy"
install_if_missing "Pillow"

echo "Installing audio packages..."
install_if_missing "pvporcupine"
install_if_missing "pvrecorder"
install_if_missing "speechrecognition"
install_if_missing "pyttsx3"
install_if_missing "gtts"

echo "Installing Bluetooth..."
install_if_missing "bleak"

echo "Installing camera & vision..."
install_if_missing "picamera2"
install_if_missing "opencv-python"
install_if_missing "opencv-contrib-python"

echo "Installing hardware packages..."
install_if_missing "smbus2"
install_if_missing "adafruit-circuitpython-pcd8544" "--break-system-packages"
install_if_missing "adafruit-blinka" "--break-system-packages"

echo ""
echo "Step 5: Enabling required interfaces..."
echo "========================================="
echo -e "${YELLOW}Please ensure the following are enabled in raspi-config:${NC}"
echo "  - SPI"
echo "  - I2C"
echo "  - Camera"
echo "  - SSH"
echo ""

# Try to enable interfaces automatically (may require sudo)
if command -v raspi-config &> /dev/null; then
    echo -e "${YELLOW}Attempting to enable interfaces...${NC}"
    sudo raspi-config nonint do_spi 0 2>/dev/null || true
    sudo raspi-config nonint do_i2c 0 2>/dev/null || true
    sudo raspi-config nonint do_camera 0 2>/dev/null || true
    echo -e "${GREEN}Interface configuration attempted${NC}"
fi

echo ""
echo "========================================="
echo "  Optional: Extra TTS Voices"
echo "========================================="
sudo apt install -y espeak mbrola-us || true

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Connect LCD following README pin connections"
echo "  3. Run: python3 main.py"
echo "  4. Access web UI: http://refugeetutor:5000/"
echo ""
echo "To test individually:"
echo "  - Test LCD: python3 -c \"from display.lcd5110 import get_lcd; lcd = get_lcd(); lcd.initialize()\""
echo "  - Test camera: python3 -c \"from vision.camera_capture import get_camera; cam = get_camera(); cam.initialize()\""
echo ""

# Deactivate venv
deactivate