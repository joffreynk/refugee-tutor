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
        self._use_offline = False
        self._espeak_available = False
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
            logger.warning(f"pyttsx3 init failed: {e}")
            self.engine = None
            
        if not self.engine:
            self._try_espeak()

    def _try_espeak(self) -> None:
        """Try espeak as fallback."""
        import subprocess
        try:
            result = subprocess.run(["which", "espeak"], capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("Using espeak for TTS")
                self._use_offline = True
                self._espeak_available = True
        except Exception:
            pass

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

    @property
    def volume_percent(self) -> int:
        """Get volume as percentage (0-100)."""
        return int(self._volume * 100)

    def set_rate(self, rate: int) -> None:
        """Set speech rate (100-300 wpm)."""
        if 100 <= rate <= 300:
            self._rate = rate
            if self.engine:
                self.engine.setProperty("rate", rate)
            logger.info(f"TTS rate set to {rate} wpm")

    def speak(self, text: str) -> None:
        """Speak the given text."""
        if self.engine and not self._use_offline:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                logger.warning(f"pyttsx3 speak failed: {e}")
                self._use_offline = True

        if hasattr(self, '_espeak_available') and self._espeak_available:
            self._speak_espeak(text)
            return
        
        if self._speak_gtts(text):
            return
        
        self._speak_espeak(text)

    def _speak_gtts(self, text: str) -> bool:
        """Fallback TTS using gTTS. Returns True if successful."""
        if not HAS_GTTS:
            logger.warning("gTTS not available")
            return False
        test_file = "/tmp/camp_tutor_speak.mp3"
        try:
            tts = gtts.gTTS(text, lang=self.language)
            tts.save(test_file)

            import subprocess
            try:
                import sounddevice as sd
                import numpy as np
                import wave
                
                with wave.open(test_file, 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    data = np.frombuffer(frames, dtype=np.int16)
                
                sd.play(data, 44100, device=1)
                sd.wait()
            except Exception as e2:
                subprocess.run(
                    ["play", test_file],
                    capture_output=True,
                    timeout=30,
                )
            logger.info(f"TTS output via gTTS")
            return True
        except Exception as e:
            logger.error(f"gTTS speak failed: {e}")
            return False
        finally:
            try:
                import os
                if os.path.exists(test_file):
                    os.remove(test_file)
            except:
                pass

    def _speak_espeak(self, text: str) -> None:
        """Final fallback using espeak."""
        import subprocess
        try:
            lang = self.language if self.language in ["en", "fr", "de", "es", "it"] else "en"
            subprocess.run(
                ["espeak", "-v", f"{lang}+f3", "-s", "130", text],
                capture_output=True,
                timeout=30,
            )
            logger.info(f"TTS output via espeak")
        except Exception as e:
            logger.error(f"espeak failed: {e}")

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
                    "en+f3",  # Female voice
                    "-s",
                    "225",  # Speed ~1.5x (225 wpm)
                    text,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"espeak failed: {e}")

    def set_language(self, language: str) -> None:
        """Change language."""
        self.language = language


_tts_instance = None


def get_tts_engine():
    """Get global TTS engine instance."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance