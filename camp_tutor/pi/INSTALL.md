# Camp Tutor - Dependencies Installation

## System Requirements
- Raspberry Pi 3B+ or 4
- 32GB+ SD card
- Raspbian/Debian-based OS

## Installation Steps

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install System Dependencies
```bash
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-full \
    espeak \
    festival \
    mpg123 \
    portaudio19-dev \
    libportaudio2 \
    git \
    network-manager
```

### 3. Create Virtual Environment
```bash
cd /home/refugeetutor
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies
```bash
pip3 install --upgrade pip setuptools wheel

# Core dependencies (offline capable)
pip3 install flask>=2.0.0
pip3 install werkzeug>=2.0.0
pip3 install numpy>=1.21.0
pip3 install Pillow>=9.0.0

# Audio - Speech Recognition & TTS
pip3 install pvporcupine>=2.0.0
pip3 install pvrecorder>=1.0.0
pip3 install speechrecognition>=3.8.0
pip3 install pyttsx3>=2.90
pip3 install gtts>=2.2.0

# Bluetooth
pip3 install bleak>=0.20.0

# Camera & Vision (choose one based on your camera)
pip3 install picamera2>=0.2.0   # For Raspberry Pi Camera
pip3 install opencv-python>=4.5.0
pip3 install opencv-contrib-python>=4.5.0

# Hardware
pip3 install RPi.GPIO>=0.7.0
pip3 install smbus2>=0.4.1
```

### 5. Optional - AI Features (requires internet or more storage)

#### Option A: Cloud AI (recommended for Pi 3B+)
```bash
# For cloud-based AI responses (needs internet)
pip3 install groq  # Fast, free tier available
```

#### Option B: Local AI (requires more storage, Pi 4 recommended)
```bash
# TensorFlow Lite - NOT recommended for Pi 3B+
# Will likely fail due to storage constraints

# ONNX Runtime (lighter alternative)
pip3 install onnxruntime
```

### 6. Verify Installation
```bash
python3 -c "import flask; import cv2; import numpy; print('All OK!')"
```

### 7. Set Hostname (Optional)
To access at `http://refugeetutor:5000/`:
```bash
sudo raspi-config
# Navigate to: System Options > Hostname
# Set to: refugeetutor
```

## Running the App
```bash
cd /home/refugeetutor
source venv/bin/activate
python3 main.py
```

Access the web interface at: **http://refugeetutor:5000/**

## Troubleshooting

### WiFi Connection Issues
```bash
# Check WiFi status
nmcli device status

# Scan for networks
nmcli device wifi list

# Connect manually
nmcli device wifi connect "SSID" password "PASSWORD"
```

### Camera Not Working
```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options > Camera > Yes
```

### Audio Issues
```bash
# Test espeak
espeak "Hello, I am Camp Tutor"

# Test microphone
arecord -l
```

## Offline vs Online Mode

| Feature | Offline | Online |
|---------|---------|--------|
| Student Database | ✅ | ✅ |
| Facial Recognition | ✅ | ✅ |
| Progress Tracking | ✅ | ✅ |
| Curriculum Teaching | ✅ | ✅ |
| Voice Output (pyttsx3) | ✅ | ✅ |
| Voice Output (gTTS) | ❌ | ✅ |
| Speech Recognition | ❌ | ✅ |
| Cloud AI (Groq) | ❌ | ✅ |