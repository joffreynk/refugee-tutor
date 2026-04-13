#!/usr/bin/env python3
"""Record audio and play back via headphone jack."""

import pyaudio
import wave
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
OUTPUT_FILE = "/tmp/record.wav"

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
    
    frames = []
    print("Recording...")
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


def play_audio():
    """Play audio via headphone jack."""
    if not os.path.exists(OUTPUT_FILE):
        print("No recording found!")
        return False
    
    # Use aplay with headphone jack (plughw:0)
    result = subprocess.run(
        ["aplay", "-D", "plughw:0", OUTPUT_FILE],
        capture_output=True,
    )
    
    if result.returncode == 0:
        print("Playing via headphone jack!")
        return True
    else:
        print(f"Playback failed: {result.stderr.decode()}")
        return False


if __name__ == "__main__":
    import subprocess
    
    print("=" * 50)
    print("  RECORD & PLAYBACK TEST")
    print("=" * 50)
    
    print("\n1. Recording 3 seconds...")
    if record_audio():
        print("\n2. Playing back...")
        play_audio()
    
    # Cleanup
    try:
        os.remove(OUTPUT_FILE)
    except:
        pass