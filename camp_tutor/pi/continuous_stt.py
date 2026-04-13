#!/usr/bin/env python3
"""Real-time speech to text for Pi 3 B+."""

import pyaudio
import threading
import queue
import speech_recognition as sr
from datetime import datetime

# Audio settings - optimized for Pi 3 B+
CHUNK = 2048  # Larger chunk for efficiency
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Lower rate for faster processing
SILENCE_THRESHOLD = 500  # Volume threshold
SILENCE_DURATION = 2  # Seconds of silence to stop

class RealTimeSTT:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.running = False
        self.text_queue = queue.Queue()
        self.stream = None
        
        # Find USB microphone
        self.mic_index = self._find_mic()
        
    def _find_mic(self):
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"Found mic: {info['name']}")
                return i
        return 0
    
    def start_listening(self):
        """Start listening in background."""
        self.running = True
        
        def listen_loop():
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.pause_threshold = 1
            
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.mic_index,
                frames_per_buffer=CHUNK
            )
            
            print("Listening... Speak now!")
            
            while self.running:
                try:
                    # Read audio
                    frame = self.stream.read(CHUNK, exception_on_overflow=False)
                    
                    # Check volume
                    import numpy as np
                    data = np.frombuffer(frame, dtype=np.int16)
                    volume = np.abs(data).mean()
                    
                    if volume > SILENCE_THRESHOLD:
                        # Convert to AudioData
                        audio_data = sr.AudioData(frame, RATE, 2)
                        
                        # Quick Google STT
                        try:
                            text = recognizer.recognize_google(audio_data, language="en")
                            if text.strip():
                                print(f">>> YOU SAID: {text}")
                                self.text_queue.put(text.strip())
                        except sr.UnknownValueError:
                            pass
                        except Exception as e:
                            pass
                            
                except Exception as e:
                    print(f"Error: {e}")
                    break
        
        self.thread = threading.Thread(target=listen_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_listening(self):
        """Stop listening."""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def get_text(self, timeout=0.1):
        """Get recognized text (non-blocking)."""
        try:
            return self.text_queue.get_nowait()
        except queue.Empty:
            return None


def main():
    print("=" * 60)
    print("  REAL-TIME SPEECH TO TEXT")
    print("=" * 60)
    print("Say words and see them appear instantly!")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    stt = RealTimeSTT()
    stt.start_listening()
    
    try:
        while True:
            text = stt.get_text()
            if text:
                print(f">{text}")
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        stt.stop_listening()


if __name__ == "__main__":
    main()