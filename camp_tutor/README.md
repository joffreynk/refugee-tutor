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
# Install dependencies
pip3 install -r requirements.txt

# Run the robot
cd pi
python3 main.py --interactive
```

## Hardware

- Raspberry Pi 3 B+ (master controller)
- ESP32 (REX controller)
- Pi Camera v2
- USB Microphone
- Nokia LCD 5110
- Servo motors, ultrasonic sensor

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

### I2C (Optional LCD via I2C)

| I2C Device | Raspberry Pi Pin |
|------------|------------------|
| SCL | Pin 5 (GPIO 3) |
| SDA | Pin 3 (GPIO 2) |
| VCC | Pin 1 (3.3V) |
| GND | Pin 9 (GND) |

### Ultrasonic Sensor (HC-SR04)

| Sensor Pin | Raspberry Pi Pin | GPIO |
|------------|------------------|-----|
| VCC | Pin 2 (5V) | - |
| GND | Pin 14 (GND) | - |
| TRIG | Pin 12 | GPIO 18 |
| ECHO | Pin 16 | GPIO 23 |

### Servo Motors (SG90)

| Servo | Raspberry Pi Pin | GPIO |
|-------|------------------|------|
| VCC | Pin 2 (5V) | - |
| GND | Pin 6 (GND) | - |
| Signal (Pan) | Pin 11 | GPIO 17 |
| Signal (Tilt) | Pin 13 | GPIO 27 |

### Bluetooth (USB)

- Plug USB Bluetooth dongle into any USB port
- Or use onboard Bluetooth (if available)

### Camera

- CSI port on Raspberry Pi
- Flat cable facing the HDMI port

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
   ```

3. **LCD Installation**
   - Connect LCD as per pin table above
   - Install library: `pip3 install adafruit-circuitpython-pcd8544`

## Web Interface

Access the robot at: **http://refugeetutor:5000/**

### Pages
- `/` - Dashboard
- `/students` - Student management
- `/wifi` - WiFi settings
- `/bluetooth` - Bluetooth settings
- `/devices` - Device status & testing
- `/config` - Configuration

## Troubleshooting

### LCD Not Working
1. Check SPI is enabled: `sudo raspi-config` → Interface Options → SPI
2. Verify wiring matches pin table
3. Test: `python3 -c "import board; print(board.SCK)`

### Audio Issues
1. Check microphone: `arecord -l`
2. Test speaker: `espeak "test"`

### Camera Issues
1. Enable camera: `sudo raspi-config` → Interface Options → Camera
2. Test: `raspistill -o test.jpg`

## Documentation

See `docs/` folder for detailed documentation:
- `SPEC.md` - System architecture and specifications
- `SETUP.md` - Hardware wiring and installation guide
- `INSTALL.md` - Software installation guide

## License

MIT