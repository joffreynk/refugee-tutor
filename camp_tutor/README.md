# Camp Tutor - Mobile AI Learning Robot

A mobile AI learning robot for educational purposes, built with Raspberry Pi and ESP32.

## Features

- **Wake Word Detection**: Activates on "Camp Tutor" phrase
- **Language-Aware Tutoring**: Detects and adapts to learner's language
- **Multi-language Support**: English, Mandarin Chinese, Hindi, Spanish, Standard Arabic, French, Bengali, Portuguese, Russian, Indonesian, Urdu, German, Japanese, Nigerian Pidgin, Egyptian Arabic, Marathi, Vietnamese, Telugu, Turkish, Cantonese
- **Progress Tracking**: Tracks student progress over time
- **Homework Generation**: Creates personalized homework assignments
- **Assessment Engine**: Generates quizzes and evaluates responses
- **AI Models**: On-device AI for language detection and recommendations
- **Visual Feedback**: Nokia LCD 5110 display
- **Safe Movement**: LOOK->MEASURE->DECIDE->MOVE protocol

## Quick Start

```bash
# Install all dependencies (run from pi directory)
cd pi
chmod +x install.sh
./install.sh

# Run the robot
python3 main.py --interactive
```

## Important Discoveries

- **Wake Word Detection**: Porcupine requires API key from picovoice.ai. Fallback to simple detector included.
- **Voice Output**: pyttsx3 voice "gmw/en" not found on Pi. Uses gTTS as fallback.
- **Camera**: python-prctl requires `libcap-dev` system package.
- **AI Models**: TensorFlow too large (~282MB) for Pi 3B+ 32GB SD. Uses fallback rule-based AI instead.

## Key Accomplishments

- `install.sh` - Dependency installation script that skips already installed packages
- `config/wifi_manager.py` - WiFi management for offline/online mode
- `vision/camera_capture.py` - Camera capture module
- `vision/facial_recognition.py` - Offline facial recognition
- Web UI pages: `/wifi`, `/bluetooth`, `/devices` with test buttons
- Independent device initialization - each device works independently
- Device status tracking in web UI

## Still Needed

- Flash ESP32 with REX firmware
- Verify I2C wiring between Pi and ESP32
- Test Bluetooth audio output with speaker/headphones
- Add HTML templates for student_add, student_detail pages

## Hardware

- **Raspberry Pi 3 B+** - Master controller (runs Python, web UI, AI)
  - Built-in WiFi (no USB needed)
  - Built-in Bluetooth (for audio output to speakers/headphones)
- **ESP32 (REX)** - Motor controller (handles motors, servos, ultrasonic sensor)
- **USB** - Microphone only
- **Pi Camera v2** - CSI port
- **Nokia LCD 5110** - SPI display

## System Architecture

| Component | Controller | Connection |
|-----------|------------|-------------|
| Camera | Raspberry Pi | CSI port (built-in) |
| LCD Display | Raspberry Pi | SPI |
| Audio Input (Mic) | Raspberry Pi | USB |
| Audio Output (Speaker) | Raspberry Pi | Bluetooth OR 3.5mm jack |
| WiFi | Raspberry Pi | Built-in |
| Bluetooth | Raspberry Pi | Built-in |
| Motors (4x omni) | REX (ESP32) | I2C |
| Servo 1 (Left/Right) | REX (ESP32) | I2C |
| Servo 2 (Up/Down) | REX (ESP32) | I2C |
| Ultrasonic Sensor | REX (ESP32) | I2C |

**I2C Communication**: Raspberry Pi communicates with REX at I2C address `0x42`

## GPIO Pin Connections (Raspberry Pi 3 B+)

### Nokia LCD 5110 (SPI)

| LCD Pin | Function | Raspberry Pi Pin | GPIO Number |
|---------|----------|------------------|-------------|
| VCC | Power (3.3V) | Pin 1 | 3.3V |
| GND | Ground | Pin 6 | GND |
| RST | Reset | Pin 18 | GPIO 24 |
| CE | Chip Enable (CS) | Pin 24 | GPIO 8 |
| DC | Data/Command | Pin 16 | GPIO 23 |
| DIN | MOSI (SPI) | Pin 19 | GPIO 19 (MOSI) |
| CLK | SCK (SPI) | Pin 23 | GPIO 11 (SCK) |

```
LCD Pinout (Top View - Left to Right):
┌────┬────┬────┬────┬────┬────┬────┐
│ VCC│ GND│ RST│ CE │ DC │ DIN│ CLK│
└────┴────┴────┴────┴────┴────┴────┘

Raspberry Pi 3B+ GPIO Layout:
    3.3V  (1) (2)  5V
  GPIO2  (3) (4)  5V
  GPIO3  (5) (6)  GND
  GPIO4  (7) (8)  GPIO14
    GND  (9) (10) GPIO15
 GPIO17 (11) (12) GPIO18
 GPIO27 (13) (14) GND
 GPIO22 (15) (16) GPIO23
    3.3V(17) (18) GPIO24
 GPIO10 (19) (20) GND
  GPIO9 (21) (22) GPIO25
 GPIO11 (23) (24) GPIO8
    GND (25) (26) GPIO7
```

### I2C Connection to REX (ESP32)

| Raspberry Pi | REX (ESP32) | Description |
|--------------|-------------|-------------|
| Pin 3 (GPIO 2) | SDA | I2C Data |
| Pin 5 (GPIO 3) | SCL | I2C Clock |
| Pin 1 (3.3V) | VCC | Power |
| Pin 9 (GND) | GND | Ground |

**I2C Address**: `0x42` (66 decimal)

### REX (ESP32) Pin Mapping

Based on REX-RDT documentation:

#### Motors (4x Omni Wheels)
| Motor | ESP32 Pin | Description |
|-------|-----------|-------------|
| Motor A1 | GPIO 15 | Forward |
| Motor A2 | GPIO 23 | Backward |
| Motor B1 | GPIO 32 | Forward |
| Motor B2 | GPIO 33 | Backward |
| Motor C1 | GPIO 5 | Forward |
| Motor C2 | GPIO 4 | Backward |
| Motor D1 | GPIO 27 | Forward |
| Motor D2 | GPIO 14 | Backward |

#### Servos
| Servo | ESP32 Pin | Description |
|-------|-----------|-------------|
| Servo 1 (Pan) | GPIO 2 | Left/Right rotation |
| Servo 2 (Tilt) | GPIO 26 | Up/Down rotation |

#### Ultrasonic Sensor (HC-SR04)
| Sensor Pin | ESP32 Pin | Description |
|------------|-----------|-------------|
| TRIG | GPIO 17 | Trigger pulse |
| ECHO | GPIO 16 | Echo response |

#### Buzzer
| Component | ESP32 Pin | Description |
|-----------|-----------|-------------|
| Buzzer | GPIO 25 | Audio alert |

## REX Commands (via I2C)

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS?` | Check REX status | Returns "OK" |
| `DISTANCE?` | Get ultrasonic distance in cm | Returns "25" |
| `MOVE:FWD:30` | Move forward 30 units | |
| `MOVE:BACK:30` | Move backward 30 units | |
| `MOVE:LEFT:30` | Move left 30 units | |
| `MOVE:RIGHT:30` | Move right 30 units | |
| `STOP` | Stop all motors | |
| `LOOK:LEFT` | Pan camera left | |
| `LOOK:RIGHT` | Pan camera right | |
| `LOOK:CENTER` | Pan camera to center | |
| `SERVO:1:90` | Set servo 1 angle | |
| `SERVO:2:90` | Set servo 2 angle | |

## Installation

See `INSTALL.md` for detailed installation steps:

1. **System Setup**
   ```bash
   sudo apt update && sudo apt upgrade
   sudo raspi-config
   # Enable: Camera, SSH, I2C, SPI
   ```

2. **Python Dependencies**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install core dependencies
   pip3 install flask numpy Pillow

   # Install audio dependencies
   pip3 install pvporcupine pvrecorder speechrecognition pyttsx3 gtts

   # Install hardware dependencies
   pip3 install adafruit-circuitpython-pcd8544 RPi.GPIO smbus2

   # Install vision
   pip3 install opencv-python picamera2

   # Install Bluetooth (for audio output)
   pip3 install bleak
   ```

3. **LCD Installation**
   - Connect LCD as per pin table above
   - Install library: `pip3 install adafruit-circuitpython-pcd8544`

4. **Enable Built-in WiFi & Bluetooth**
   - WiFi: Use raspi-config or connect via GUI
   - Bluetooth: Use `bluetoothctl` to pair speakers

## Web Interface

Access the robot at: **http://refugeetutor:5000/**

### Pages
- `/` - Dashboard
- `/students` - Student management
- `/wifi` - WiFi settings (built-in)
- `/bluetooth` - Bluetooth audio output settings
- `/devices` - Device status & testing
- `/config` - Configuration

## Troubleshooting

### WiFi Not Connecting
1. Check: `nmcli device wifi list`
2. Connect: `nmcli device wifi connect SSID password PASSWORD`

### Bluetooth Audio Output
1. Pair: `bluetoothctl`
2. Connect to speaker/headphones
3. Set as output: `pactl set-default-sink bluez_sink.XX_XX_XX`

### LCD Not Working
1. Check SPI is enabled: `sudo raspi-config` → Interface Options → SPI
2. Verify wiring matches pin table
3. Test: `python3 -c "import board; print(board.SCK)"`

### Audio Issues
1. Check microphone: `arecord -l`
2. Test speaker: `espeak "test"`

### Camera Issues
1. Enable camera: `sudo raspi-config` → Interface Options → Camera
2. Test: `raspistill -o test.jpg`

### REX (ESP32) Not Responding
1. Check I2C: `i2cdetect -y 1`
2. Should show address `0x42`
3. Flash ESP32 with REX firmware

## Documentation

See `docs/` folder for detailed documentation:
- `SPEC.md` - System architecture and specifications
- `SETUP.md` - Hardware wiring and installation guide
- `INSTALL.md` - Software installation guide

## License

MIT