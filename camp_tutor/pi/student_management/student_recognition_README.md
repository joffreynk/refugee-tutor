# Student Recognition System - Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip3 install -r student_recognition_requirements.txt
```

### 2. Start the System
```bash
python3 student_recognition.py
```

### 3. Access the UI
- On Raspberry Pi: Open `http://localhost:5000`
- From mobile device: Use Raspberry Pi's IP address `http://<pi-ip>:5000`

## Features

### Adding Students
1. Navigate to "Add Student" in the web UI
2. Enter student name
3. Select or create a classroom
4. Upload a photo OR use the capture button

### WiFi Setup
1. Go to "WiFi" section
2. Enter network name (SSID) and password
3. Click "Save & Connect"
4. The system will automatically connect on future restarts

### Focused Online Mode
When WiFi is connected and offline mode is unchecked:
- AI operates in focused mode
- Only listens for questions
- Answers queries without background processes
- Optimized for Q&A interaction

## Facial Recognition

### Training
The system will automatically train when you have at least 2 students with photos.
You can manually retrain from Settings > Train Face Model.

### Recognition Threshold
Default: 0.6 (60% confidence)
Adjust in `config.json` if needed.

## Mobile Capture

To use mobile camera for photo capture:
1. Navigate to "Add Student" on your mobile device
2. Grant camera permission when prompted
3. Click "Capture Photo" button
4. The photo is sent directly to the Raspberry Pi

## Classrooms

Create and manage classrooms from the Settings page.
Students can be assigned to specific classrooms for organized learning sessions.

## Offline Mode

Default: OFFLINE MODE enabled
- WiFi credentials are saved but not used
- All AI and learning features work locally
- Best for teaching sessions

## Troubleshooting

### Camera not detected
```bash
# Check camera
vcgencmd get_camera

# Enable camera if disabled
sudo raspi-config
# Interface Options -> Camera -> Enable
```

### WiFi connection fails
```bash
# Check available networks
nmcli device wifi list

# Manual connection test
nmcli device wifi connect "SSID" password "PASSWORD"
```

### Facial recognition not working
1. Add at least 2 photos per student
2. Ensure good lighting in photos
3. Face should be clearly visible
4. Retrain model from Settings

## System Requirements

- Raspberry Pi 3B+ or 4
- Python 3.7+
- Camera module (optional for capture)
- Network connection for mobile access