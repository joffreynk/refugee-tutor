#!/usr/bin/env python3
"""Analyze captured image with object detection."""

import cv2
import numpy as np

img = cv2.imread('/tmp/vision.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = img.shape[:2]

# Resize for faster processing
small = cv2.resize(img, (320, 240))

# Detect colors (objects by color)
def detect_color(img, lower, upper, name):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    ratio = mask.sum() / 255 / (img.shape[0] * img.shape[1])
    return ratio > 0.05, name, ratio * 100

objects = []

# Blue (sky, window, water)
blue, name, _ = detect_color(small, [100, 50, 50], [130, 255, 255], "blue items")
if blue:
    objects.append("blue (window/sky)")

# Green (plants, grass)
green, name, _ = detect_color(small, [25, 40, 40], [85, 255, 255], "green")
if green:
    objects.append("green plants")

# Brown (wood, chair, car)
brown, name, _ = detect_color(small, [10, 20, 20], [30, 150, 150], "brown")
if brown:
    objects.append("brown (chair/wood)")

# Skin (person face/hands)
skin_mask = cv2.inRange(small, np.array([0, 20, 70]), np.array([20, 255, 255]))
skin_ratio = skin_mask.sum() / 255 / (small.shape[0] * small.shape[1])
if skin_ratio > 0.01:
    objects.append("skin/person")

# Dark/Black (car, shadow)
dark, name, _ = detect_color(small, [0, 0, 0], [180, 255, 50], "dark")
if dark:
    objects.append("dark objects")

# White/White (walls, paper)
white, name, _ = detect_color(small, [0, 0, 180], [180, 50, 255], "white")
if white:
    objects.append("white items")

# Basic info
b, g, r = img[:,:,0].mean(), img[:,:,1].mean(), img[:,:,2].mean()
bright = gray.mean()

lighting = "dark" if bright < 50 else "bright" if bright > 200 else "normal"

print("=" * 50)
print("  WHAT I SEE")
print("=" * 50)
print(f"\nImage: {w}x{h}")
print(f"Lighting: {lighting}")

if objects:
    print("I see:")
    for obj in objects:
        print(f"  - {obj}")
else:
    print("No distinct objects detected")

# Check scene busy
edges = cv2.Canny(gray, 50, 150).sum() / (h * w) * 100
print(f"Scene: {'busy' if edges > 2 else 'simple'}")