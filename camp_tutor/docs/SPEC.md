# Camp Tutor - Mobile AI Learning Robot

**Version:** 2.2  
**Date:** April 10, 2026

---

## Quick Start - How to Make the Robot Work

```bash
# On Raspberry Pi - Run these commands:

# 1. Start Bluetooth
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# 2. Start NetworkManager
sudo systemctl start NetworkManager
sudo systemctl enable NetworkManager

# 3. Install I2C tools
sudo apt-get install -y i2c-tools

# 4. Install BLEAK for Bluetooth scanning
pip install bleak

# 5. Enable camera (run raspi-config)
sudo raspi-config
# → Interface Options → Legacy Camera → Enable

# 6. Restart
sudo reboot

# 7. Run the application
cd ~/camp_tutor/pi
python main.py
```

### Web Interface

1. **Save Sudo Password First**: Go to `/wifi`, enter `Refugee123@` in admin password
2. **WiFi Scanning**: Uses `nmcli` with sudo from `passwords.txt`
3. **Bluetooth Scanning**: Uses `bleak` library for real BLE discovery

---

## 1. Architecture Overview

### System Design Principle
Camp Tutor is a mobile AI learning robot that follows the core behavior rule:
**LOOK -> MEASURE -> DECIDE -> MOVE**

Before any movement, the robot must:
1. Point the camera/sensor head in the intended direction
2. Measure distance with the ultrasonic sensor
3. Decide whether the path is clear
4. Only then initiate movement (if safe)

### Hardware Architecture

#### Raspberry Pi Side (Master)
- **Raspberry Pi 3 B+**: Main controller, runs all AI/learning logic
- **Pi Camera v2**: Visual input for interaction awareness
- **USB Microphone**: Audio input for wake word and speech recognition
- **Audio Output**: 3.5mm jack and/or Bluetooth speaker
- **Nokia LCD 5110**: Status display and visualization
- **I2C Master**: Communicates with REX controller

#### REX Side (Slave)
- **ESP32-based REX controller**: Real-time hardware control
- **Pan-Tilt Servo Mechanism**: Head direction control
- **Ultrasonic Sensor (HC-SR04)**: Distance measurement
- **Omni-directional Drive Base**: Holonomic movement
- **Emergency Stop**: Local safety enforcement

### Communication Architecture
- **I2C Bus**: SCL on GPIO 22, SDA on GPIO 21
- **Protocol**: Master/Slave with command-response pattern
- **Transport-agnostic**: Protocol designed for future transport adaptation

### Hardware Responsibilities Matrix

| Component | Raspberry Pi (Master) | REX (Slave) |
|-----------|---------------------|------------|
| Wake Word Detection | ✓ | - |
| Speech Recognition | ✓ | - |
| Language Detection | ✓ | - |
| Text-to-Speech | ✓ | - |
| Camera Capture | ✓ | - |
| Student Records | ✓ | - |
| Progress Tracking | ✓ | - |
| Homework Generation | ✓ | - |
| Assessment Generation | ✓ | - |
| TensorFlow Lite Inference | ✓ | - |
| LCD 5110 Display | ✓ | - |
| Pan Servo Control | - | ✓ |
| Tilt Servo Control | - | ✓ |
| Ultrasonic Reading | - | ✓ |
| Omni-wheel Movement | - | ✓ |
| Obstacle Avoidance | - | ✓ |
| Emergency Stop | - | ✓ |
| Real-time Safety | - | ✓ |

### Core Behavior Flow

```
[IDLE] -> Wake Word Detected -> [LISTENING]
[LISTENING] -> Language Confirmed -> [TEACHING]
[TEACHING] -> Student Present -> [ENGAGED]
[ENGAGED] -> Movement Request -> LOOK -> MEASURE -> DECIDE -> MOVE
[MOVING] -> Arrived/Obstacle -> [ENGAGED/TEACHING]
[TEACHING] -> Inactivity Timeout -> [IDLE]
```

---

## 2. File Tree

```
camp_tutor/
├── pi/
│   ├── main.py                      # Main entry point
│   ├── passwords.txt                # Sudo password (Refugee123@)
│   ├── requirements.txt            # Python dependencies
│   ├── install.sh                  # Installation script
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── wake_word.py              # Wake word detection
│   │   ├── speech_to_text.py         # Speech recognition
│   │   ├── text_to_speech.py       # TTS output
│   │   ├── audio_device.py        # Audio device management
│   │   └── audio_processor.py    # Audio processing
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── language_detection.py   # Language identification
│   │   ├── tutor_engine.py       # Core tutoring logic
│   │   ├── homework_generator.py # Homework creation
│   │   ├── assessment_engine.py # Quiz/assessment logic
│   │   ├── progress_tracker.py  # Progress tracking
│   │   ├── tflite_models.py     # TensorFlow Lite wrapper
│   │   └── ai_controller.py    # AI controller
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── camera.py             # Pi Camera interface
│   │   ├── camera_capture.py    # Camera capture
│   │   ├── visual_monitor.py    # Visual awareness
│   │   └── facial_recognition.py # Face recognition
│   ├── bluetooth/
│   │   ├── __init__.py
│   │   └── bluetooth_manager.py # BLE scanning with bleak
│   ├── display/
│   │   ├── __init__.py
│   │   └── lcd5110.py          # Nokia LCD 5110 driver
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── student_db.py        # Student database
│   │   ├── class_manager.py   # Class management
│   │   └── session_logger.py  # Session logging
│   ├── student_management/
│   │   ├── __init__.py
│   │   └── student_recognition.py # Student recognition
│   ├── control/
│   │   ├── __init__.py
│   │   ├── rex_client.py       # I2C REX client
│   │   └── decision_manager.py # LOOK->MEASURE->DECIDE->MOVE
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py        # Configuration
│   │   └── wifi_manager.py   # WiFi management
│   ├── web/
│   │   ├── __init__.py
│   │   ├── web_ui.py        # Flask web server
│   │   └── templates/       # HTML templates
│   │       ├── dashboard.html
│   │       ├── students.html
│   │       ├── wifi.html
│   │       ├── bluetooth.html
│   │       ├── devices.html
│   │       └── config.html
│   └── ui/
│       ├── __init__.py
│       ├── ui_controls.py    # UI controls
│       └── diagnostics.py   # Diagnostics
├── rex/
│   ├── rex_firmware.ino       # Main ESP32 firmware
│   ├── command_parser.cpp     # Command parsing
│   ├── servo_controller.cpp/h # Pan-tilt control
│   ├── ultrasonic.cpp/h     # Distance sensor
│   ├── motor_controller.cpp/h # Omni-drive control
│   ├── safety_controller.cpp/h # Safety enforcement
│   └── i2c_protocol.h      # I2C protocol definitions
├── docs/
│   ├── SPEC.md
│   ├── REPORT.md
│   ├── SETUP.md
│   └── MULTI_LANGUAGE_REPORT.md
└── README.md
```
camp_tutor/
├── pi/
│   ├── main.py                      # Main entry point
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── wake_word.py              # Wake word detection (Precise LEDE)
│   │   ├── speech_to_text.py         # Speech recognition
│   │   ├── text_to_speech.py         # TTS output
│   │   └── audio_device.py           # Audio device management
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── language_detection.py    # Language identification
│   │   ├── tutor_engine.py           # Core tutoring logic
│   │   ├── homework_generator.py    # Homework creation
│   │   ├── assessment_engine.py     # Quiz/assessment logic
│   │   ├── progress_tracker.py      # Progress tracking
│   │   └── tflite_models.py          # TensorFlow Lite wrapper
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── camera.py                 # Pi Camera interface
│   │   └── visual_monitor.py         # Visual awareness
│   ├── display/
│   │   ├── __init__.py
│   │   └── lcd5110.py                # Nokia LCD 5110 driver
│   ├── storage/
��   │   ├── __init__.py
│   │   ├── student_db.py             # Student database
│   │   └── session_logger.py         # Session logging
│   ├── control/
│   │   ├── __init__.py
│   │   ├── rex_client.py             # I2C REX client
│   │   └── decision_manager.py       # LOOK->MEASURE->DECIDE->MOVE
│   └── config/
│       ├── __init__.py
│       └── settings.py               # Configuration
├── rex/
│   ├── rex_firmware.ino             # Main ESP32 firmware
│   ├── command_parser.h              # Command parsing
│   ├── servo_controller.h           # Pan-tilt control
│   ├── ultrasonic.h                 # Distance sensor
│   ├── motor_controller.h            # Omni-drive control
│   ├── safety_controller.h          # Safety enforcement
│   └── i2c_protocol.h               # I2C protocol definitions
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROTOCOL.md
│   ├── DATABASE_SCHEMA.md
│   └── SETUP.md
└── README.md
```

---

## 3. I2C Protocol Specification

### Command Format
```
Master (Pi) -> Slave (REX): COMMAND:PARAM
Slave (REX) -> Master (Pi): RESPONSE:VALUE
```

### Commands (Pi -> REX)

| Command | Parameters | Description |
|---------|------------|-------------|
| LOOK | LEFT/CENTER/RIGHT/HOME | Pan/tilt head direction |
| DIST? | - | Request distance reading |
| MOVE | FWD/LEFT/RIGHT/BACK | Basic omni movement |
| OMNI | FWD/BACK/LEFT/RIGHT/FL/FR/BL/BR/RL/RR/STOP | Extended omni movement |
| STOP | - | Emergency stop |
| RESET | - | Reset system after emergency |
| HOME | - | Return to home position |
| CALIBRATE | - | Calibrate sensors |
| PING | - | Health check |
| BUZZER | SHORT/LONG | Control buzzer |
| STATUS? | - | Request REX status |

### Responses (REX -> Pi)

| Response | Value | Description |
|----------|-------|-------------|
| OK | - | Command acknowledged |
| ERROR | code | Error with code |
| DIST | cm | Distance in centimeters |
| BLOCKED | - | Path blocked or emergency stop active |
| READY | - | REX ready |
| RESET | - | System reset complete |
| PONG | - | Ping response |
| STATUS | state | Current REX state |

### Protocol Flow

```
Pi: "LOOK:CENTER" -> REX: "OK" -> Pi: "DIST?" -> REX: "DIST:45" -> 
Pi: Decision (safe) -> Pi: "MOVE:FWD" -> REX: "OK" -> [movement]
```

### Safety Rules
1. REX must always respond to DIST? before any MOVE command
2. REX must reject MOVE if distance < 20cm
3. REX must stop immediately on STOP command
4. REX must timeout movement after 5 seconds
5. Communication timeout: 2 seconds

---

## 4. Database Schema

### Tables

#### students
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Unique student ID |
| name | TEXT | Student name |
| created_at | TEXT | Creation timestamp |
| preferred_language | TEXT | Default language |
| current_level | INTEGER | Current skill level (1-10) |
| total_sessions | INTEGER | Session count |
| total_time_minutes | INTEGER | Total learning time |

#### sessions
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Session ID |
| student_id | TEXT | Foreign key to students |
| start_time | TEXT | Session start |
| end_time | TEXT | Session end |
| language | TEXT | Session language |
| topic | TEXT | Topic covered |
| completed | INTEGER | Completion status |

#### progress
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Progress ID |
| student_id | TEXT | Foreign key |
| topic | TEXT | Topic name |
| correct_count | INTEGER | Correct answers |
| total_count | INTEGER | Total questions |
| timestamp | TEXT | When recorded |

#### homework
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Homework ID |
| student_id | TEXT | Foreign key |
| topic | TEXT | Topic |
| questions | TEXT | JSON questions |
| assigned_at | TEXT | Assignment time |
| due_at | TEXT | Due date |
| completed | INTEGER | Completion status |

---

## 5. TensorFlow Lite Integration

### Models

1. **language_classifier.tflite**: Multilingual text classification
   - Input: Text string (tokenized)
   - Output: Language probability (en/fr/es/de/zh)
   - Size: < 500KB

2. **difficulty_classifier.tflite**: Student level estimation
   - Input: Performance features
   - Output: Level (1-10)
   - Size: < 200KB

3. **recommendation_model.tflite**: Topic recommendation
   - Input: Student history features
   - Output: Recommended topic
   - Size: < 300KB

### Inference Pipeline
1. Preprocess input (tokenize/normalize)
2. Load TFLite model
3. Run inference
4. Postprocess output
5. Return result

---

## 6. Supported Languages

| Code | Language | TTS Voice | Rank | Speakers (Est.) |
|------|----------|-----------|------|-----------------|
| en | English | en-US | 1 | 1.53 Billion |
| zh | Mandarin Chinese | zh-CN | 2 | 1.18 Billion |
| hi | Hindi | hi-IN | 3 | 611 Million |
| ar | Standard Arabic | ar-SA | 5 | 335 Million |
| fr | French | fr-FR | 6 | 312 Million |
| bn | Bengali | bn-BD | 7 | 284 Million |
| pt | Portuguese | pt-BR | 8 | 267 Million |
| ru | Russian | ru-RU | 9 | 253 Million |
| id | Indonesian | id-ID | 10 | 252 Million |
| ur | Urdu | ur-PK | 11 | 246 Million |
| de | German | de-DE | 12 | 134 Million |
| ja | Japanese | ja-JP | 13 | 126 Million |
| pcm | Nigerian Pidgin | en-NG | 14 | 121 Million |
| ar-eg | Egyptian Arabic | ar-EG | 15 | 119 Million |
| mr | Marathi | mr-IN | 16 | 99 Million |
| vi | Vietnamese | vi-VN | 17 | 97 Million |
| te | Telugu | te-IN | 18 | 96 Million |
| tr | Turkish | tr-TR | 19 | 91 Million |
| yue | Cantonese (Yue) | yue-HK | 20 | 86 Million |

### Language Detection
The system uses keyword-based language detection with language-specific keywords for accurate identification across all 20 supported languages.

---

## 7. Noise Filtering and Distance Control

### Audio Processing Pipeline

The system includes multi-stage audio processing for noisy environments:

```
Input Audio -> High Pass Filter -> Low Pass Filter -> Noise Gate -> 
Spectral Subtraction -> SNR Enhancement -> Distance Attenuation -> Output
```

### Noise Filter Specifications

| Parameter | Value | Purpose |
|-----------|-------|---------|
| High Pass | 80 Hz | Remove low frequency hum |
| Low Pass | 8000 Hz | Remove high frequency noise |
| Noise Floor | Adaptive | Auto-calibrated |
| Voice Activation | 0.015 RMS | Detect speech presence |
| Minimum SNR | 10 dB | Ensure quality capture |

### Distance-Based Capture

- **Maximum Range**: 5 meters (500 cm)
- **Optimal Range**: < 1 meter
- **Attenuation**: Gradual beyond 1m
- **Sensor**: HC-SR04 Ultrasonic
- **Update Rate**: 100ms

### Noise Reduction Features

1. **Bandpass Filtering**: Removes frequencies outside speech range
2. **Adaptive Noise Floor**: Auto-calibrates to ambient noise
3. **Spectral Subtraction**: Reduces constant background noise
4. **SNR Enhancement**: Boosts quiet voice signals
5. **Distance Attenuation**: Ignores distant sounds

---

## 8. Curriculum System (Pearson Edexcel Aligned)

### Age Groups

| Age Group | Age Range | Key Characteristics |
|-----------|-----------|---------------------|
| Early Years | 3-5 | Play-based, basic concepts |
| Primary | 5-11 | Foundation skills, exploratory |
| Lower Secondary | 11-14 | Abstract thinking, specialized |
| Upper Secondary | 14-18 | Advanced, exam preparation |

### Subject Structure

```
CURRICULUM
├── Early Years (3-5)
│   ├── Mathematics: pre_number, shapes, measure
│   ├── Science: exploring, observations
│   ├── English: speaking, listening, reading
│   ├── Global Citizenship: self, environment
│   ├── Computing: digital_literacy
│   └── Programming: unplugged
├── Primary (5-11)
│   ├── Mathematics: number, geometry, measure
│   ├── Science: biology, chemistry, physics
│   ├── English: reading, writing
│   ├── Global Citizenship: world, citizenship
│   ├── Computing: digital_systems
│   └── Programming: block_based (Scratch)
├── Lower Secondary (11-14)
│   ├── Mathematics: number, algebra, geometry
│   ├── Science: biology, chemistry, physics
│   ├── English: literature, language
│   ├── Global Citizenship: global_issues, sustainability
│   ├── Computing: systems, data
│   └── Programming: python, web_dev
└── Upper Secondary (14-18)
    ├── Mathematics: pure, mechanics, statistics
    ├── Science: physics, chemistry, biology
    ├── English: literature, language
    ├── Global Citizenship: politics, economics
    ├── Computing: theory, systems
    └── Programming: software, advanced
```

### Adaptive Learning

The tutor adapts to:
- **Age Group**: Selects appropriate content
- **Performance**: Difficulty adjustment
- **Progress**: Topic recommendations
- **Language**: Multilingual content delivery

---

## 9. System Constraints

- **Raspberry Pi 3 B+**: ARMv8 Cortex-A53, 1GB RAM
- **Max model size**: 1MB per model
- **Target latency**: < 500ms for TFLite inference
- **I2C speed**: 100kHz standard mode
- **Audio sample rate**: 16kHz for speech
- **Camera resolution**: 640x480 for efficiency

---

## 11. Assumptions and Limitations

1. **Offline-first**: System works without internet
2. **Single student**: One student per session
3. **Fixed topics**: Pre-defined curriculum
4. **Indoor use**: Controlled environment
5. **Adult supervision**: Adult present during use
6. **Power**: Battery or mains powered
7. **No network**: No cloud connectivity required

---

## 10. Student Recognition and Management System

### Features

1. **Facial Recognition**
   - Identify multiple students simultaneously
   - Real-time face detection using OpenCV
   - LBPH face recognizer optimized for Pi 3B+
   - Minimum face size: 80x80 pixels
   - Recognition threshold: 0.6 confidence

2. **Student Database**
   - Store student profiles with photos
   - Assign students to classrooms
   - Track session count and last seen time
   - Support multiple photos per student

3. **Mobile Device Access**
   - Web-based UI accessible from any device
   - Upload photos during registration
   - Capture photos using device camera
   - Mobile-responsive interface

4. **WiFi Connectivity**
   - Save credentials persistently
   - Default to offline mode
   - Network scanning support (nmcli with sudo)
   - Live status from system
   - Password stored in passwords.txt

5. **Bluetooth Connectivity**
   - BLE scanning with bleak library
   - Live status via rfkill command
   - Toggle persistence across page navigation
   - Audio output to Bluetooth speakers

6. **Password File (pi/passwords.txt)**
   ```
   sudo=Refugee123@
   ```
   Used for sudo operations (WiFi scanning/connection)

7. **Focused Online Mode**
   - When connected online: AI only listens/answers queries
   - No background processes during focused mode
   - Optimized for learning Q&A

### Architecture

```
Student Recognition Components:
├── WebServer (Flask) - Port 5000
├── FacialRecognition - OpenCV LBPH
├── CameraCapture - picamera2
├── WiFiManager - NetworkManager
└── StudentDatabase - JSON-based storage
```

### UI Endpoints

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/students` | Student list |
| `/student/add` | Add new student |
| `/courses` | Course management |
| `/results` | Student results |
| `/progress` | Progress view |
| `/config` | Configuration |
| `/wifi` | WiFi settings (scanning/connection) |
| `/bluetooth` | Bluetooth settings (BLE scanning) |
| `/devices` | Device diagnostics |
| `/api/status` | API status |
| `/api/bluetooth/scan` | BLE scan endpoint |
| `/api/wifi/scan` | WiFi scan endpoint |

### Data Storage

```
data/
├── students/
│   ├── index.json
│   ├── student_1234567890/
│   │   ├── photo_1.jpg
│   │   ├── photo_2.jpg
│   │   └── ...
├── config.json
├── wifi.json
└── models/
    └── face_model.yml
```

### Optimization for Pi 3B+

- Camera resolution: 640x480
- Face detection: Haar cascades
- Recognition: LBPH (lightweight)
- Web server: Flask with threading
- JSON storage (no SQLite overhead)