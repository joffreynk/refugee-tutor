#!/usr/bin/env python3
"""Camera test - view what camera sees."""

import cv2
import numpy as np

def main():
    print("=" * 60)
    print("  CAMERA TEST")
    print("=" * 60)
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("No camera found!")
        return
    
    print("Camera opened. Press 'q' to quit, 's' to save image")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        # Show info
        height, width = frame.shape[:2]
        print(f"\rViewing: {width}x{height} pixels", end="")
        
        # Simple object detection info
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness
        brightness = gray.mean()
        
        # Detect edges (simple feature)
        edges = cv2.Canny(gray, 50, 150)
        edge_count = np.count_nonzero(edges)
        
        # Show frame (window will open)
        cv2.imshow('Camp Tutor Camera', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('/tmp/cam_capture.jpg', frame)
            print(f"\nImage saved to /tmp/cam_capture.jpg")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera test complete!")


if __name__ == "__main__":
    main()