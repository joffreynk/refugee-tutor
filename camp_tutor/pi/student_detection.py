#!/usr/bin/env python3
"""Face and person detection for students."""

import cv2
import numpy as np

img = cv2.imread('/tmp/vision.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = img.shape[:2]

print("=" * 50)
print("  STUDENT DETECTION")
print("=" * 50)

# 1. Face detection (front)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray, 1.1, 4)

print(f"Faces detected: {len(faces)}")

# 2. Full body detection (for when not facing front)
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
bodies = body_cascade.detectMultiScale(gray, 1.1, 4)

print(f"Bodies detected: {len(bodies)}")

# 3. Upper body (for classroom)
upper_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody')
try:
    upper_bodies = upper_cascade.detectMultiScale(gray, 1.1, 4)
    print(f"Upper bodies: {len(upper_bodies)}")
except:
    upper_bodies = []

# Count unique students
all_detections = []
for x, y, fw, fh in faces:
    all_detections.append((x + fw//2, y + fh//2))
for x, y, bw, bh in bodies:
    all_detections.append((x + bw//2, y + bh//2))

# Group nearby detections
students = len(faces) + len(bodies)
print(f"\nTotal students: {students}")

if students > 0:
    print("\nI see students!")
    if students == 1:
        print("1 student in frame")
    else:
        print(f"{students} students in frame")
else:
    print("\nNo students detected")
    print("- Maybe facing away?")
    print("- Possibly seated?")

# Additional info
bright = gray.mean()
print(f"\nLighting: {'dark' if bright < 50 else 'bright' if bright > 200 else 'normal'}")
print(f"Image size: {w}x{h}")