#!/usr/bin/env python3
"""Test LCD 5110 on Raspberry Pi."""

import sys

print("=" * 50)
print("LCD 5110 TEST")
print("=" * 50)

try:
    from display.lcd5110 import get_lcd
    
    print("\n[1] Getting LCD...")
    lcd = get_lcd()
    print("    [OK] LCD instance created")
    
    print("\n[2] Initializing LCD...")
    result = lcd.initialize()
    if result:
        print("    [OK] LCD initialized (real)")
    else:
        print("    [WARN] Using mock LCD")
    
    print("\n[3] Testing display...")
    lcd.clear()
    lcd.show_text("Camp Tutor", 0)
    lcd.show_text("LCD Test OK!", 1)
    lcd.show_text("GPIO Pins:", 2)
    lcd.show_text("CS=8 RST=24", 3)
    lcd.show_text("DC=23 LED=18", 4)
    print("    [OK] Text displayed")
    
    print("\n[4] Testing status...")
    lcd.show_status("TEACHING", student="Test", topic="Math", language="EN")
    print("    [OK] Status shown")
    
    print("\n[5] Testing progress...")
    lcd.show_progress(7, 10)
    print("    [OK] Progress shown")
    
    print("\n" + "=" * 50)
    print("LCD TEST PASSED!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
