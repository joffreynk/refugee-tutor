"""Wake word detection module using Precise-LEDE."""

import logging
import threading
import time
from typing import Callable, Optional

import numpy as np
import pvporcupine
from pvrecorder import PvRecorder

from config import settings

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Continuously listens for wake word using Precise-LEDE engine."""

    def __init__(
        self,
        wake_word: str = settings.WAKE_WORD,
        sensitivity: float = settings.WAKE_THRESHOLD,
    ):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.is_listening = False
        self.recorder: Optional[PvRecorder] = None
        self.porcupine: Optional[pvporcupine.Porcupine] = None
        self.callback: Optional[Callable[[], None]] = None
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None

    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for wake word."""
        if self.is_listening:
            logger.warning("Wake word detector already running")
            return

        self.callback = callback
        self._stop_event.clear()

        try:
            keywords = [self.wake_word.replace(" ", "_")]
            self.porcupine = pvporcupine.create(
                keywords=keywords,
                sensitivities=[self.sensitivity],
            )
        except pvporcupine.PorcupineException:
            keywords = ["camp_tutor"]
            self.porcupine = pvporcupine.create(
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

    def _listen_loop(self) -> None:
        """Main listening loop."""
        while not self._stop_event.is_set() and self.is_listening:
            try:
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
            self.recorder.stop()
            self.recorder = None

        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None

        if self._listen_thread:
            self._listen_thread.join(timeout=2.0)
            self._listen_thread = None

        logger.info("Wake word detector stopped")

    def is_active(self) -> bool:
        """Check if detector is currently listening."""
        return self.is_listening


class SimpleWakeWordDetector:
    """Simple keyword spotter as fallback without Porcupine."""

    def __init__(
        self,
        wake_word: str = settings.WAKE_WORD,
    ):
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.callback: Optional[Callable[[], None]] = None

    def start(self, callback: Callable[[], None]) -> None:
        """Start the detector."""
        self.callback = callback
        self.is_listening = True
        logger.info(f"Simple wake word detector started for: {self.wake_word}")

    def stop(self) -> None:
        """Stop the detector."""
        self.is_listening = False
        logger.info("Simple wake word detector stopped")

    def is_active(self) -> bool:
        """Check if detector is active."""
        return self.is_listening

    def check_audio(self, audio_data: bytes) -> bool:
        """Check if wake word is in audio (placeholder for real implementation)."""
        return False