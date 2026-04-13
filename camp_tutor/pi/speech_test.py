#!/usr/bin/env python3
"""Speech to text - record and convert to text."""

import pyaudio
import wave
import subprocess
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
OUTPUT_FILE = "/tmp/speech_input.wav"

def record_audio():
    """Record from microphone."""
    p = pyaudio.PyAudio()
    
    # Find input device (USB mic)
    input_mics = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_mics.append((i, info['name']))
    
    if not input_mics:
        print("No microphone found!")
        p.terminate()
        return False
    
    device_index = input_mics[0][0]
    print(f"Recording from: {input_mics[0][1]}")
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )
    
    print(f"Recording for {RECORD_SECONDS} seconds... Speak now!")
    frames = []
    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"Saved to {OUTPUT_FILE}")
    return True


def transcribe_audio():
    """Convert audio to text with multi-language support."""
    if not os.path.exists(OUTPUT_FILE):
        print("No recording found!")
        return None
    
    print("Converting speech to text...")
    
    # Try using Google Speech Recognition - try multiple languages
    languages = ["en-US", "fr-FR", "es-ES", "de-DE", "it-IT", "pt-PT", "ar-SA", "zh-CN"]
    
    for lang in languages:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(OUTPUT_FILE) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language=lang)
            if text:
                print(f"\n>>> YOU SAID ({lang}): {text}")
                return text
        except Exception:
            continue
    
    # Try English as fallback
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(OUTPUT_FILE) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        print(f"\n>>> YOU SAID: {text}")
        return text
    except Exception as e:
        print(f"STT error: {e}")
    
    # Try Whisper (offline)
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(OUTPUT_FILE)
        text = result["text"].strip()
        print(f"\n>>> YOU SAID: {text}")
        return text
    except ImportError:
        print("Whisper not installed - pip install openai-whisper")
    except Exception as e:
        print(f"Whisper error: {e}")
    
    print("No STT available")
    return None


def main():
    print("=" * 60)
    print("  SPEECH TO TEXT TEST")
    print("=" * 60)
    print("\nRecording... Speak clearly!")
    print("-" * 40)
    
    if record_audio():
        transcribe_audio()
    
    # Cleanup
    try:
        os.remove(OUTPUT_FILE)
    except:
        pass


if __name__ == "__main__":
    main()