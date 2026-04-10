"""Wake word detection module using Porcupine."""

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

# Get free API key from environment or use placeholder
# Get your free key at: https://picovoice.ai/porcupine/
PORCUPINE_ACCESS_KEY = os.environ.get("PV_ACCESS_KEY", "")


class WakeWordDetector:
    """Continuously listens for wake word using Porcupine engine."""

    def __init__(
        self,
        wake_word: str = settings.WAKE_WORD,
        sensitivity: float = settings.WAKE_THRESHOLD,
    ):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.is_listening = False
        self.recorder: Optional[PvRecorder] = None
        self.porcupine = None
        self.callback: Optional[Callable[[], None]] = None
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None

    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for wake word."""
        if self.is_listening:
            logger.warning("Wake word detector already running")
            return

        # Use simple detector if Porcupine not available or no access key
        if not HAS_PORCUPINE or not PORCUPINE_ACCESS_KEY:
            logger.warning("Porcupine not available or no access key, using simple detector")
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

            logger.info(f"Wake word detector started, listening for: {self.wake_word}")

        except Exception as e:
            logger.warning(f"Porcupine init failed: {e}, using simple detector")
            self._start_simple(callback)

    def _start_simple(self, callback: Callable[[], None]) -> None:
        """Start simple detector as fallback."""
        self.callback = callback
        self.is_listening = True
        logger.info(f"Simple wake word detector started for: {self.wake_word}")
        
    def _listen_loop(self) -> None:
        """Main listening loop."""
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
                    logger.info(f"Wake word detected: {self.wake_word}")
                    if self.callback:
                        self.callback()

            except Exception as e:
                logger.error(f"Error in wake word detection: {e}")
                time.sleep(0.1)

    def stop(self) -> None:
        """Stop listening for wake word."""
        if not self.is_listening:
            return

        self._stop_event.set()
        self.is_listening = False

        if self.recorder:
            try:
                self.recorder.stop()
            except Exception:
                pass
            self.recorder = None

        if self.porcupine:
            try:
                self.porcupine.delete()
            except Exception:
                pass
            self.porcupine = None

        logger.info("Wake word detector stopped")

    def is_active(self) -> bool:
        """Check if detector is active."""
        return self.is_listening