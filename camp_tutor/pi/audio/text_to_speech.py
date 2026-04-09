"""Text-to-speech module."""

import logging
from typing import Optional

import pyttsx3

try:
    import gtts
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

from config import settings

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Converts text to speech audio output."""

    def __init__(self, language: str = "en"):
        self.language = language
        self.engine: Optional[pyttsx3.Engine] = None
        self._volume = settings.DEFAULT_VOLUME
        self._rate = settings.DEFAULT_SPEECH_RATE
        self._init_engine()

    def _init_engine(self) -> None:
        """Initialize pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self._rate)
            self.engine.setProperty("volume", self._volume)

            voices = self.engine.getProperty("voices")
            for voice in voices:
                if self.language in voice.languages:
                    self.engine.setProperty("voice", voice.id)
                    break

            logger.info(f"TTS initialized: lang={self.language}, vol={self._volume*100}%, rate={self._rate}")
        except Exception as e:
            logger.warning(f"pyttsx3 init failed, will use gTTS: {e}")
            self.engine = None

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        if 0.0 <= volume <= 1.0:
            self._volume = volume
            if self.engine:
                self.engine.setProperty("volume", volume)
            logger.info(f"TTS volume set to {int(volume * 100)}%")

    def set_volume_percent(self, percent: int) -> None:
        """Set volume by percentage (0-100)."""
        self.set_volume(percent / 100.0)

    def set_rate(self, rate: int) -> None:
        """Set speech rate (100-300 wpm)."""
        if 100 <= rate <= 300:
            self._rate = rate
            if self.engine:
                self.engine.setProperty("rate", rate)
            logger.info(f"TTS rate set to {rate} wpm")

    def speak(self, text: str) -> None:
        """Speak the given text."""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                logger.warning(f"pyttsx3 speak failed: {e}")

        self._speak_gtts(text)

    def _speak_gtts(self, text: str) -> None:
        """Fallback TTS using gTTS."""
        if not HAS_GTTS:
            logger.warning("gTTS not available")
            return
        try:
            tts = gtts.gTTS(text, lang=self.language)
            tts.save("/tmp/camp_tutor_speak.mp3")

            import subprocess
            subprocess.run(
                ["mpg123", "-q", "-g", "200", "/tmp/camp_tutor_speak.mp3"],
                check=False,
            )
        except Exception as e:
            logger.error(f"gTTS speak failed: {e}")

    def set_language(self, language: str) -> None:
        """Change TTS language."""
        self.language = language
        if self.engine:
            self._init_engine()

    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None


class OfflineTextToSpeech:
    """Offline TTS using espeak."""

    def __init__(self, language: str = "en"):
        self.language = language

    def speak(self, text: str) -> None:
        """Speak using espeak."""
        import subprocess

        lang_code = self.language
        if lang_code == "zh":
            lang_code = "zh"

        try:
            subprocess.run(
                [
                    "espeak",
                    "-v",
                    lang_code,
                    "-s",
                    "140",
                    text,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"espeak failed: {e}")

    def set_language(self, language: str) -> None:
        """Change language."""
        self.language = language