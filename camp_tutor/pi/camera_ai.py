#!/usr/bin/env python3
"""Capture image and describe."""

import cv2
import numpy as np

def capture():
    cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    
    ret, frame = cap.read()
    cap.release()
    
    if ret and frame is not None:
        cv2.imwrite("/tmp/vision.jpg", frame)
        return True
    return False


def analyze():
    img = cv2.imread("/tmp/vision.jpg")
    if img is None:
        return "No image"
    
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    brightness = gray.mean()
    b, g, r = img[:,:,0].mean(), img[:,:,1].mean(), img[:,:,2].mean()
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = edges.sum() / (h * w) * 100
    
    # Analyze
    if brightness < 50:
        lighting = "dark"
    elif brightness > 200:
        lighting = "bright"
    else:
        lighting = "normal"
    
    if r > b + 20:
        color = "warm (red/orange)"
    elif b > r + 20:
        color = "cool (blue)"
    else:
        color = "balanced"
    
    if edge_ratio > 5:
        detail = "busy"
    else:
        detail = "simple"
    
    # Check for skin tones
    skin = np.sum((r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b)) / (h * w) * 100
    if skin > 5:
        subject = "face/person detected"
    else:
        subject = "no face"
    
    return f"I see: {lighting} scene, {color} tones, {detail} background. {subject}."


print("=" * 50)
print("  CAMERA VISION")
print("=" * 50)

if capture():
    print("Captured!")
    result = analyze()
    print(f"\n>>> {result}")
else:
    print("Failed")