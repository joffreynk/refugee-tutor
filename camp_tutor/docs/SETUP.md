# Camp Tutor - Setup and Installation Guide

## 1. Hardware Requirements

### Raspberry Pi Side
- Raspberry Pi 3 B+
- 32GB+ microSD card with Raspberry Pi OS
- Pi Camera v2
- USB microphone (e.g., Blue Mic or generic USB mic)
- 3.5mm speaker or Bluetooth speaker
- Nokia LCD 5110 display with backpack

### REX Side
- ESP32 development board (e.g., ESP32-WROOM-32)
- 2x SG90 servo motors (pan/tilt)
- HC-SR04 ultrasonic sensor
- L298N motor driver
- 4x DC motors for omni-drive (optional)
- 5V power supply
- 12V power supply (for motors)

## 2. Wiring Diagram

### I2C Connection
```
Raspberry Pi     ESP32
GPIO 22 (SCL) -> GPIO 22 (SCL)
GPIO 21 (SDA) -> GPIO 21 (SDA)
GND           -> GND
3.3V          -> EN (via 10K resistor)
```

### Servo Connections (ESP32)
```
Pan Servo   -> GPIO 13
Tilt Servo -> GPIO 12
VCC       -> 5V
GND       -> GND
```

### Ultrasonic Connections (ESP32)
```
TRIG  -> GPIO 14
ECHO  -> GPIO 15
VCC  -> 5V
GND  -> GND
```

### Motor Connections (ESP32)
```
Left Motor 1  -> GPIO 32
Left Motor 2  -> GPIO 33
Right Motor 1 -> GPIO 25
Right Motor 2 -> GPIO 26
Enable      -> GPIO 27
```

### Nokia LCD Connections (Raspberry Pi)
```
RST  -> GPIO 24
DC   -> GPIO 23
MOSI -> GPIO 19 (SPI MOSI)
MISO -> GPIO 21 (SPI MISO)
CLK  -> GPIO 11 (SPI CLK)
CS   -> GPIO 8  (SPI CE0)
VCC  -> 3.3V
GND  -> GND
```

## 3. Software Installation

### Raspberry Pi OS Setup

1. Install Raspberry Pi OS Lite:
```bash
sudo raspi-config
# Enable Camera, I2C, SPI
# Set audio output
```

2. Install system packages:
```bash
sudo apt update
sudo apt install -y python3-pip git i2c-tools libasound2-dev \
    libportaudio2 portaudio19-dev mpg123
```

3. Install Python packages:
```bash
pip3 install RPi.Gpio smbus2 pvporcupine pvrecorder \
    speechrecognition pyttsx3 gtts pillow numpy
```

4. Install TensorFlow Lite:
```bash
pip3 install tflite-runtime
```

### REX Firmware Upload

1. Install Arduino IDE or PlatformIO

2. Install ESP32 board support:
```
Arduino IDE: File -> Preferences -> Additional Board Manager URLs
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

3. Install libraries:
- Servo
- Wire

4. Upload `rex_firmware.ino` to ESP32

## 4. Running Camp Tutor

### Quick Start
```bash
cd camp_tutor/pi
python3 main.py
```

### Interactive Mode
```bash
python3 main.py --interactive
```

### Systemd Service
```bash
sudo cp camp_tutor.service /etc/systemd/system/
sudo systemctl enable camp_tutor
sudo systemctl start camp_tutor
```

## 5. Configuration

### Audio Device Selection
```bash
arecord -l            # List input devices
aplay -l             # List output devices
```

Edit `config/settings.py` to set audio device.

### I2C Address
Default REX I2C address: `0x42`

To change:
1. Edit `settings.py` on Pi
2. Edit `i2c_protocol.h` on REX

## 6. Testing

### Test Wake Word
```bash
python3 -c "from audio import wake_word; w = wake_word.WakeWordDetector(); print(w.is_active())"
```

### Test I2C Connection
```bash
i2cdetect -y 1
# Should show 0x42 (REX)
```

### Test Servos
Connect to REX serial monitor and send:
- `LOOK:LEFT`
- `LOOK:CENTER`
- `LOOK:RIGHT`

### Test Motors
Connect to REX serial monitor and send:
- `MOVE:FWD`
- `MOVE:BACK`

## 7. Troubleshooting

### Common Issues

1. **Wake word not detected**
   - Check microphone permissions
   - Adjust sensitivity in `settings.py`

2. **I2C communication fails**
   - Check wiring (SCL/SDA)
   - Verify I2C is enabled via `raspi-config`
   - Check pull-up resistors

3. **TTS not working**
   - Install espeak: `sudo apt install espeak`
   - Try offline TTS mode

4. **LCD not displaying**
   - Check SPI connections
   - Install Adafruit libraries

### Debug Logging
```bash
export LOG_LEVEL=DEBUG
python3 main.py
```

## 8. Safety Notes

- Always supervise robot use by children
- Keep workspace clear of obstacles
- Test emergency stop regularly
- Keep battery charged
- Store in dry location

## 9. Supported Languages

Camp Tutor supports the 20 most spoken languages in the world:

| Code | Language | Rank | Speakers (Est.) |
|------|----------|------|-----------------|
| en   | English  | 1 | 1.53 Billion |
| zh   | Mandarin Chinese | 2 | 1.18 Billion |
| hi   | Hindi | 3 | 611 Million |
| ar   | Standard Arabic | 5 | 335 Million |
| fr   | French | 6 | 312 Million |
| bn   | Bengali | 7 | 284 Million |
| pt   | Portuguese | 8 | 267 Million |
| ru   | Russian | 9 | 253 Million |
| id   | Indonesian | 10 | 252 Million |
| ur   | Urdu | 11 | 246 Million |
| de   | German | 12 | 134 Million |
| ja   | Japanese | 13 | 126 Million |
| pcm  | Nigerian Pidgin | 14 | 121 Million |
| ar-eg| Egyptian Arabic | 15 | 119 Million |
| mr   | Marathi | 16 | 99 Million |
| vi   | Vietnamese | 17 | 97 Million |
| te   | Telugu | 18 | 96 Million |
| tr   | Turkish | 19 | 91 Million |
| yue  | Cantonese (Yue) | 20 | 86 Million |

Note: Rank numbers reference the global language ranking (some ranks skipped due to regional variants).

## 10. Noise Filtering and Distance Control

### Audio Processing Features

Camp Tutor includes advanced audio processing for noisy environments:

| Parameter | Value | Description |
|-----------|-------|-------------|
| High Pass Filter | 80 Hz | Removes low frequency noise |
| Low Pass Filter | 8000 Hz | Removes high frequency noise |
| Noise Threshold | 0.02 | Minimum signal level |
| Voice Activation | 0.015 | Minimum voice level |
| SNR Minimum | 10 dB | Signal-to-noise ratio |
| Max Distance | 500 cm | Voice capture limit |

### Distance-Based Capture

The robot only captures voice within 5 meters:
- Uses ultrasonic sensor to measure distance
- Applies distance-based attenuation
- Full gain at optimal distance (<1m)
- Gradual attenuation beyond 1m
- Silence beyond 5m

### Noise Calibration

To calibrate for your environment:
```python
from audio.audio_processor import get_audio_processor
processor = get_audio_processor()
processor.calibrate(duration=2.0)  # 2 seconds of ambient noise
```

## 11. Curriculum (Pearson Edexcel Aligned)

### Age Groups

| Group | Ages | Description |
|-------|------|-------------|
| Early Years | 3-5 | Pre-school, basic concepts |
| Primary | 5-11 | Elementary school |
| Lower Secondary | 11-14 | Middle school |
| Upper Secondary | 14-18 | High school |

### Subjects

| Subject | Description |
|---------|-------------|
| Mathematics | Number, algebra, geometry, statistics |
| Science | Biology, chemistry, physics |
| English | Reading, writing, speaking, listening |
| Global Citizenship | World issues, sustainability, culture |
| Computing | Digital systems, data, networks |
| Programming | Algorithms, block coding, Python |

## 12. Class Management System

### One Class at a Time

The robot handles one class (age group) at a time:
- Switch between Early Years, Primary, Lower Secondary, Upper Secondary
- Each class has its own timetable and progress tracking
- Sessions are recorded with timestamp and topics covered

### Timetable Generation

Each age group has a configurable timetable:

| Age Group | Lessons/Week | Duration | Subjects |
|-----------|--------------|----------|----------|
| Early Years | 5 | 20 min | Math, Science, English, GC, Computing |
| Primary | 6 | 30 min | + Programming |
| Lower Secondary | 7 | 35 min | All subjects |
| Upper Secondary | 8 | 40 min | All subjects (Advanced) |

### Progress Tracking

The system tracks:
- Lessons completed per age group
- Topics covered in each subject
- Session duration and timestamps
- AI recommendation for next lesson

### AI Sequencing

Before teaching, the system:
1. Generates timetable for selected age group
2. Analyzes lesson history to identify weak areas
3. Recommends next subject/topic based on:
   - Timetable order
   - Completed lessons
   - Subject performance

### Usage

```python
from storage import get_class_manager
from ui import get_age_selector, get_timetable_display

# Switch age group
selector = get_age_selector()
selector.select_age_group(2)  # Lower Secondary

# Get AI recommendation
tm = get_timetable_display()
rec = tm.get_ai_recommendation()
print(f"Next: {rec['subject']} - {rec['topic']}")

# Start class
cm = get_class_manager()
cm.start_class(student_count=5)
# ... teaching ...
cm.end_class()
```

## 13. Next Steps

1. Train custom TensorFlow Lite models
2. Add more lesson content
3. Implement OCR for worksheets
4. Add cloud sync for progress
5. Extend to more languages