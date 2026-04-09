"""Audio device management."""

import logging
import subprocess
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class AudioDevice:
    """Manages audio input and output devices."""

    def __init__(self):
        self.input_device: Optional[str] = None
        self.output_device: Optional[str] = None
        self._detect_devices()

    def _detect_devices(self) -> None:
        """Detect available audio devices."""
        try:
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines and "card" in lines[0]:
                    self.input_device = "default"
                    logger.info(f"Found audio input: {lines[0]}")
        except Exception as e:
            logger.warning(f"Could not detect audio devices: {e}")

        try:
            result = subprocess.run(
                ["aplay", "-l"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines and "card" in lines[0]:
                    self.output_device = "default"
                    logger.info(f"Found audio output: {lines[0]}")
        except Exception as e:
            logger.warning(f"Could not detect audio output: {e}")

    def set_input_device(self, device: str) -> None:
        """Set input device by name or index."""
        self.input_device = device

    def set_output_device(self, device: str) -> None:
        """Set output device by name or index."""
        self.output_device = device

    def test_input(self) -> bool:
        """Test if input device works."""
        if not self.input_device:
            return False
        try:
            result = subprocess.run(
                ["arecord", "-d", "1", "-f", "S16_LE", "-r", "16000", "/tmp/test.wav"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def test_output(self) -> bool:
        """Test if output device works."""
        if not self.output_device:
            return False
        try:
            result = subprocess.run(
                ["speaker-test", "-t", "sine", "-f", "440", "-l", "1"],
                capture_output=True,
                timeout=3,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_info(self) -> dict:
        """Get device information."""
        return {
            "input": self.input_device,
            "output": self.output_device,
        }


_audio_device_instance: Optional[AudioDevice] = None


def get_audio_device() -> AudioDevice:
    """Get global audio device instance."""
    global _audio_device_instance
    if _audio_device_instance is None:
        _audio_device_instance = AudioDevice()
    return _audio_device_instance