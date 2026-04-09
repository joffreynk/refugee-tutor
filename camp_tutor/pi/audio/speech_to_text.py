"""Speech-to-text module."""

import logging
import threading
import time
from typing import Optional

import speech_recognition as sr

from config import settings

logger = logging.getLogger(__name__)


class SpeechToText:
    """Converts speech audio to text."""

    def __init__(self, language: str = "en-US"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.is_listening = False
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None
        self._use_noise_filter = True
        self._max_distance_cm = 500

    def set_distance_limit(self, max_distance_cm: int) -> None:
        """Set maximum distance for voice capture (in centimeters)."""
        self._max_distance_cm = max_distance_cm
        logger.info(f"Voice capture distance limit set to {max_distance_cm}cm")

    def enable_noise_filter(self, enabled: bool) -> None:
        """Enable or disable noise filtering."""
        self._use_noise_filter = enabled
        logger.info(f"Noise filtering {'enabled' if enabled else 'disabled'}")

    def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Listen and convert speech to text."""
        with sr.Microphone(
            sample_rate=settings.AUDIO_SAMPLE_RATE,
            chunk_size=settings.AUDIO_CHUNK_SIZE,
        ) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logger.info(f"Listening in {self.language}...")

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10.0,
                )
            except sr.WaitTimeoutError:
                logger.debug("No speech detected within timeout")
                return None

        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
            )
            logger.info(f"Recognized: {text}")
            return text

        except sr.UnknownValueError:
            logger.debug("Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None

    def listen_for_choice(
        self,
        choices: list[str],
        timeout: float = 10.0,
    ) -> Optional[str]:
        """Listen and match against choices."""
        text = self.listen(timeout=timeout)
        if not text:
            return None

        text_lower = text.lower()
        for choice in choices:
            if choice.lower() in text_lower:
                return choice

        return None


class OfflineSpeechToText:
    """Fallback STT using CMU Sphinx."""

    def __init__(self, language: str = "en-US"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 400

    def listen(self, timeout: float = 5.0) -> Optional[str]:
        """Convert speech to text using offline recognizer."""
        with sr.Microphone(
            sample_rate=settings.AUDIO_SAMPLE_RATE,
            chunk_size=settings.AUDIO_CHUNK_SIZE,
        ) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10.0,
                )
            except sr.WaitTimeoutError:
                return None

        try:
            text = self.recognizer.recognize_sphinx(
                audio,
                language=self.language,
            )
            logger.info(f"Offline recognized: {text}")
            return text

        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Offline recognition error: {e}")
            return None