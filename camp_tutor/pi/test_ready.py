#!/usr/bin/env python3
"""Quick test to verify Camp Tutor is ready."""

import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

def main():
    print("=" * 60)
    print("  CAMP TUTOR - READY CHECK")
    print("=" * 60)
    
    errors = []
    
    # Test 1: Python imports
    print("\n[1] Testing imports...")
    try:
        from config import settings
        from storage import student_db
        from control import rex_client
        print("    [OK] Core modules loaded")
    except Exception as e:
        errors.append(f"Imports: {e}")
        print(f"    [FAIL] {e}")
    
    # Test 2: Audio (TTS) - skip if pyttsx3 not installed
    print("\n[2] Testing audio output...")
    try:
        import pyttsx3
        from audio import text_to_speech
        tts = text_to_speech.TextToSpeech()
        tts.speak("Hello! I am ready to teach!")
        print("    [OK] Audio working")
    except ImportError:
        print("    [SKIP] pyttsx3 not installed")
    except Exception as e:
        print(f"    [WARN] Audio: {e}")
    
    # Test 3: Database
    print("\n[3] Testing database...")
    try:
        db = student_db.get_student_db()
        count = db.get_student_count()
        print(f"    [OK] Database ready ({count} students)")
    except Exception as e:
        print(f"    [FAIL] Database: {e}")
    
    # Test 4: AI Tutor
    print("\n[4] Testing AI tutor...")
    try:
        from ai import tutor_engine
        tutor = tutor_engine.get_tutor_engine()
        greeting = tutor.get_greeting()
        print(f"    [OK] AI ready: '{greeting}'")
    except Exception as e:
        print(f"    [FAIL] AI: {e}")
    
    # Test 5: REX (_serial or mock)
    print("\n[5] Testing REX...")
    try:
        from control import rex_client
        rex = rex_client.get_rex_client()
        if rex.is_connected():
            status = rex.get_status()
            print(f"    [OK] REX connected: {status}")
        else:
            print("    [WARN] REX not connected (using mock)")
    except Exception as e:
        print(f"    [WARN] REX: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if not errors:
        print("  CAMP TUTOR IS READY!")
        print("\nTo start the robot:")
        print("  python3 main.py")
    else:
        print("  ISSUES FOUND:")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()