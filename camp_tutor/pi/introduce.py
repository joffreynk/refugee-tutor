#!/usr/bin/env python3
"""Camp Tutor introduction via TTS - direct approach."""

import subprocess
import os

def speak(text):
    """Speak text using espeak (offline, works)."""
    # Use espeak directly - offline and reliable
    result = subprocess.run(
        ["espeak", "-ven", "-k20", "-s140", text],
        capture_output=True,
    )
    return result.returncode == 0

def speak_google(text):
    """Speak using gTTS."""
    try:
        from gtts import gTTS
        
        test_file = "/tmp/camp_tutor_speak.mp3"
        tts = gTTS(text, lang="en")
        tts.save(test_file)
        
        # Try sox play command first
        result = subprocess.run(
            ["play", "-q", test_file],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            os.remove(test_file)
            return True
        
        # Fallback to aplay with headphone jack (plughw:0) - Pi built-in
        result = subprocess.run(
            ["aplay", "-D", "plughw:0", test_file],
            capture_output=True,
        )
        
        os.remove(test_file)
        return result.returncode == 0
    except Exception as e:
        print(f"gTTS error: {e}")
        return False

def main():
    intro = """Hello! I am Camp Tutor, your AI learning companion!
    I am here to help you learn Mathematics, Science, and English through fun activities and games.
    Let's start learning together!
    """
    
    print("=" * 50)
    print("  CAMP TUTOR INTRODUCTION")
    print("=" * 50)
    print(f"\nTutor says:\n{intro}")
    print("\nPlaying...")
    
    # Try espeak first (offline, works)
    print("Trying espeak...")
    if speak(intro):
        print("Played via espeak!")
        return
    
    # Try gTTS
    print("Trying gTTS...")
    if speak_google(intro):
        print("Played via gTTS!")
        return
    
    print("Failed to play sound")

if __name__ == "__main__":
    main()