#!/usr/bin/env python3
"""Pi Camera test using v4l2."""

import cv2
import subprocess
import time

print("Pi Camera Test")
print("=" * 40)

# Try v4l2 directly
cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)

if not cap.isOpened():
    print("Trying without V4L2...")
    cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("Camera opened!")
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Read frame
    for i in range(5):
        ret, frame = cap.read()
        if ret and frame is not None:
            cv2.imwrite(f"/tmp/cam_{i}.jpg", frame)
            print(f"Saved cam_{i}.jpg")
            break
        time.sleep(0.5)
    
    cap.release()
else:
    print("Camera not available")
    
    # Try using picamera2 with firmware libcamera
    try:
        import os
        os.environ['LIBCAMERA_LOG_LEVELS'] = 'ERROR'
        
        # Try direct python picamera2
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.start_and_capture_file("/tmp/cam.jpg")
        print("Saved via picamera2!")
    except Exception as e:
        print(f"picamera2 error: {e}")