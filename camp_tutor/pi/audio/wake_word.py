"""Wake word detection module."""

import logging
import os
import threading
import time
from typing import Callable, Optional

import numpy as np

try:
    import pvporcupine
    from pvrecorder import PvRecorder
    HAS_PORCUPINE = True
except ImportError:
    HAS_PORCUPINE = False

from config import settings

logger = logging.getLogger(__name__)

PORCUPINE_ACCESS_KEY = os.environ.get("PV_ACCESS_KEY", "")


class WakeWordDetector:
    def __init__(
        self,
        wake_word: str = settings.WAKE_WORD,
        sensitivity: float = settings.WAKE_THRESHOLD,
    ):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.is_listening = False
        self.recorder = None
        self.porcupine = None
        self.callback = None
        self._stop_event = threading.Event()
        self._listen_thread = None

    def start(self, callback: Callable[[], None]) -> None:
        if self.is_listening:
            return

        if not HAS_PORCUPINE or not PORCUPINE_ACCESS_KEY:
            logger.warning("Using simple detector (no Porcupine key)")
            self._start_simple(callback)
            return

        self.callback = callback
        self._stop_event.clear()

        try:
            keywords = [self.wake_word.replace(" ", "_")]
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=keywords,
                sensitivities=[self.sensitivity],
            )
            self.recorder = PvRecorder(
                frame_length=self.porcupine.frame_length,
                buffer_size_ms=500,
            )
            self.is_listening = True
            self.recorder.start()
            self._listen_thread = threading.Thread(target=self._listen_loop)
            self._listen_thread.daemon = True
            self._listen_thread.start()
            logger.info(f"Wake word detector started: {self.wake_word}")
        except Exception as e:
            logger.warning(f"Porcupine failed: {e}, using simple detector")
            self._start_simple(callback)

    def _start_simple(self, callback):
        self.callback = callback
        self.is_listening = True
        logger.info(f"Simple detector for: {self.wake_word}")
        
    def _listen_loop(self):
        while not self._stop_event.is_set() and self.is_listening:
            try:
                if not self.recorder or not self.porcupine:
                    break
                pcm = self.recorder.read()
                if pcm is None:
                    continue
                pcm_array = np.frombuffer(pcm, dtype=np.int16)
                pcm_float = pcm_array.astype(np.float32) / 32767.0
                result = self.porcupine.process(pcm_float)
                if result >= 0:
                    logger.info("Wake word detected!")
                    if self.callback:
                        self.callback()
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(0.1)

    def stop(self):
        self._stop_event.set()
        self.is_listening = False
        if self.recorder:
            try:
                self.recorder.stop()
            except:
                pass
            self.recorder = None
        if self.porcupine:
            try:
                self.porcupine.delete()
            except:
                pass
            self.porcupine = None
        logger.info("Wake word detector stopped")

    def is_active(self):
        return self.is_listening


class SimpleWakeWordDetector:
    def __init__(self, wake_word: str = settings.WAKE_WORD):
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.callback = None

    def start(self, callback: Callable[[], None]) -> None:
        self.callback = callback
        self.is_listening = True
        logger.info(f"Simple detector for: {self.wake_word}")

    def stop(self) -> None:
        self.is_listening = False

    def is_active(self) -> bool:
        return self.is_listening

    def check_audio(self, audio_data: bytes) -> bool:
        return False