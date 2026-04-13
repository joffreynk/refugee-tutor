#!/usr/bin/env python3
"""Camp Tutor - Final Ready Check."""

import subprocess
import sys
import os

def check(label, cmd, must_pass=False):
    """Run a check."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        ok = result.returncode == 0
        status = "✓" if ok else "✗"
        print(f"  {status} {label}")
        return ok, result
    except Exception as e:
        print(f"  ✗ {label}: {e}")
        return False, None

def main():
    print("=" * 60)
    print("  CAMP TUTOR - READY CHECK")
    print("=" * 60)
    
    print("\n[1] AUDIO OUTPUT")
    check("espeak TTS", "espeak 'test' 2>/dev/null")
    check("Headphone jack", "aplay -D plughw:0 -l")
    
    print("\n[2] AUDIO INPUT")
    check("USB Microphone", "python3 -c 'import pyaudio; p=pyaudio.PyAudio(); print(p.get_device_count())'")
    
    print("\n[3] CAMERA")
    check("Pi Camera", "ls /dev/video0")
    check("libcamera", "rpicam-still --help 2>&1 | head -1")
    
    print("\n[4] AI/ML")
    check("Speech Recognition", "python3 -c 'import speech_recognition' 2>/dev/null && echo 'OK'")
    check("OpenCV", "python3 -c 'import cv2; print(cv2.__version__)'")
    
    print("\n[5] NETWORK")
    check("WiFi", "iwconfig wlan0 2>/dev/null | grep -q 'ESSID' && echo 'OK'")
    
    print("\n[6] REX ROBOT")
    check("rex_client", "python3 -c 'from control import rex_client; print(\"OK\")'")
    
    print("\n[7] STORAGE")
    check("Database", "python3 -c 'from storage import student_db; print(\"OK\")'")
    
    print("\n" + "=" * 60)
    print("  USAGE COMMANDS")
    print("=" * 60)
    print("""
# Take photo
rpicam-still -o /tmp/vision.jpg -t 2000

# See what camera sees
python3 analyze_camera.py

# Detect students
python3 student_detection.py

# Speech to text (record & transcribe)
python3 speech_test.py

# Test robot (all tests)
python3 test_robot.py

# Start robot
python3 main.py
""")

if __name__ == "__main__":
    main()