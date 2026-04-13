#!/usr/bin/env python3
"""Camp Tutor - Complete System Test."""

import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"


def test_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)


def test_result(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status:8} | {name}")
    if details and not passed:
        print(f"           -> {details}")
    return passed


def main():
    print("=" * 50)
    print("  CAMP TUTOR - COMPLETE SYSTEM TEST")
    print("=" * 50)

    results = []

    # 1. Test Imports
    test_section("1. IMPORT MODULES")
    try:
        from config import settings
        results.append(test_result("config.settings", True))
    except Exception as e:
        results.append(test_result("config.settings", False, str(e)))

    try:
        from storage.student_db import get_student_db
        results.append(test_result("student_db", True))
    except Exception as e:
        results.append(test_result("student_db", False, str(e)))

    try:
        from control.rex_client import get_rex_client
        results.append(test_result("rex_client", True))
    except Exception as e:
        results.append(test_result("rex_client", False, str(e)))

    try:
        from display.lcd5110 import get_lcd
        results.append(test_result("lcd5110", True))
    except Exception as e:
        results.append(test_result("lcd5110", False, str(e)))

    try:
        from ai.tutor_engine import get_tutor_engine
        results.append(test_result("tutor_engine", True))
    except Exception as e:
        results.append(test_result("tutor_engine", False, str(e)))

    # 2. Test LCD
    test_section("2. LCD DISPLAY")
    try:
        from display.lcd5110 import get_lcd
        lcd = get_lcd()
        lcd.initialize()
        lcd.clear()
        lcd.show_text("Camp Tutor", 0)
        lcd.show_text("System Test", 1)
        results.append(test_result("LCD display", True))
    except Exception as e:
        results.append(test_result("LCD display", False, str(e)))

    # 3. Test REX
    test_section("3. REX ROBOT")
    try:
        from control.rex_client import get_rex_client
        rex = get_rex_client()
        
        if rex.is_connected():
            results.append(test_result("REX connected", True))
            status = rex.get_status()
            print(f"           -> {status}")
            
            ping = rex.ping()
            results.append(test_result("REX ping", ping))
            
            dist = rex.get_distance()
            results.append(test_result("REX distance", dist >= 0))
            print(f"           -> Distance: {dist}cm")
        else:
            results.append(test_result("REX connected", False, "Not connected to /dev/ttyUSB0"))
            print("           -> Using mock REX")
    except Exception as e:
        results.append(test_result("REX", False, str(e)))

    # 4. Test Audio
    test_section("4. AUDIO SYSTEM")
    
    # TTS
    try:
        import pyttsx3
        tts = pyttsx3.init()
        results.append(test_result("TTS (pyttsx3)", True))
    except ImportError:
        try:
            from audio.text_to_speech import TextToSpeech
            tts = TextToSpeech()
            results.append(test_result("TTS (fallback)", True))
        except Exception as e:
            results.append(test_result("TTS", False, str(e)))
    except Exception as e:
        results.append(test_result("TTS", False, str(e)))

    # STT
    try:
        import speech_recognition
        results.append(test_result("STT (speech_rec)", True))
    except ImportError:
        results.append(test_result("STT", False, "Not installed"))

    # 5. Test Database
    test_section("5. DATABASE")
    try:
        from storage.student_db import get_student_db
        db = get_student_db()
        count = db.get_student_count()
        results.append(test_result("Student DB", True, f"{count} students"))
    except Exception as e:
        results.append(test_result("Student DB", False, str(e)))

    # 6. Test AI
    test_section("6. AI TUTOR")
    try:
        from ai.tutor_engine import get_tutor_engine
        tutor = get_tutor_engine()
        greeting = tutor.get_greeting()
        results.append(test_result("AI Tutor", True, greeting))
    except Exception as e:
        results.append(test_result("AI Tutor", False, str(e)))

    # 7. Test Camera
    test_section("7. CAMERA")
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        if cam:
            results.append(test_result("Camera", True))
        else:
            results.append(test_result("Camera", False, "Not available"))
    except Exception as e:
        results.append(test_result("Camera", False, str(e)))

    # 8. Test WiFi
    test_section("8. WIFI")
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        status = wifi.get_status()
        connected = status.get("connected", False)
        results.append(test_result("WiFi", connected, str(status)))
    except Exception as e:
        results.append(test_result("WiFi", False, str(e)))

    # Final Summary
    test_section("FINAL RESULT")
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if all(results):
        print("  ALL TESTS PASSED!")
        print(f"\n  Robot is ready to run:")
        print("    python main.py")
    else:
        print(f"  {passed}/{total} tests passed")
        print("\n  To install missing dependencies:")
        print("    pip install pyttsx3 pyserial numpy")
        print("    pip install speechrecognition opencv-python")
    
    print("=" * 50)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
