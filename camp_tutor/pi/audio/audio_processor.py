"""Audio processing module with noise filtering and distance-based capture."""

import logging
import math
import threading
import time
from typing import Callable, Optional

import numpy as np

from config import settings

logger = logging.getLogger(__name__)


class NoiseFilter:
    """Active noise cancellation and filtering for noisy environments."""

    def __init__(
        self,
        high_pass_hz: int = settings.AUDIO_HIGH_PASS_FILTER_HZ,
        low_pass_hz: int = settings.AUDIO_LOW_PASS_FILTER_HZ,
        noise_threshold: float = settings.AUDIO_NOISE_THRESHOLD,
    ):
        self.high_pass_hz = high_pass_hz
        self.low_pass_hz = low_pass_hz
        self.noise_threshold = noise_threshold
        self.noise_floor: float = 0.0
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.is_adapting = True
        self.adaptation_samples = 0
        self._noise_profile: list[float] = []
        self._lock = threading.Lock()

    def _apply_bandpass_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply bandpass filter to audio data."""
        if len(audio_data) < 3:
            return audio_data

        filtered = np.zeros_like(audio_data)
        rc = 1.0 / (2 * math.pi * self.high_pass_hz)
        dt = 1.0 / self.sample_rate
        alpha = rc / (rc + dt)

        filtered[0] = audio_data[0]
        for i in range(1, len(audio_data)):
            filtered[i] = alpha * (filtered[i - 1] + audio_data[i] - audio_data[i - 1])

        if self.low_pass_hz < self.sample_rate / 2:
            rc_lp = 1.0 / (2 * math.pi * self.low_pass_hz)
            alpha_lp = rc_lp / (rc_lp + dt)
            smoothed = filtered[0]
            for i in range(1, len(filtered)):
                smoothed = smoothed + alpha_lp * (filtered[i] - smoothed)
                filtered[i] = smoothed

        return filtered

    def _calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculate RMS (Root Mean Square) of audio data."""
        if len(audio_data) == 0:
            return 0.0
        return np.sqrt(np.mean(audio_data ** 2))

    def _estimate_noise_floor(self, audio_data: np.ndarray) -> None:
        """Estimate noise floor from quiet portions of audio."""
        if not self.is_adapting:
            return

        rms = self._calculate_rms(audio_data)
        if rms < self.noise_threshold * 2:
            self._noise_profile.append(rms)
            if len(self._noise_profile) > 100:
                self._noise_profile.pop(0)

            if self.adaptation_samples > 500:
                if self._noise_profile:
                    self.noise_floor = np.percentile(self._noise_profile, 20)
                self.is_adapting = False
                logger.info(f"Noise floor calibrated: {self.noise_floor:.6f}")

        self.adaptation_samples += 1

    def _apply_spectral_subtraction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply simple spectral subtraction for noise reduction."""
        if self.noise_floor <= 0:
            return audio_data

        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        power = magnitude ** 2

        noise_estimate = self.noise_floor ** 2 * len(audio_data)
        power_clean = np.maximum(power - noise_estimate * 0.5, power * 0.1)

        magnitude_clean = np.sqrt(power_clean)
        fft_clean = magnitude_clean * np.exp(1j * np.angle(fft))

        return np.fft.irfft(fft_clean, n=len(audio_data))

    def filter(self, audio_data: bytes) -> bytes:
        """Apply noise filtering to audio data."""
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767.0

        self._estimate_noise_floor(audio_array)

        filtered = self._apply_bandpass_filter(audio_array)

        if self.noise_floor > 0:
            filtered = self._apply_spectral_subtraction(filtered)

        rms = self._calculate_rms(filtered)
        if rms < self.noise_threshold:
            return b""

        snr = 20 * math.log10(rms / max(self.noise_floor, 0.0001))
        if snr < settings.AUDIO_MIN_SNR_DB:
            gain = math.pow(10, (settings.AUDIO_MIN_SNR_DB - snr) / 20)
            filtered = filtered * min(gain, 10.0)

        filtered_int = np.clip(filtered * 32767, -32768, 32767).astype(np.int16)
        return filtered_int.tobytes()

    def calibrate(self, duration_seconds: float = 2.0) -> float:
        """Calibrate noise floor with ambient noise."""
        self.is_adapting = True
        self.adaptation_samples = 0
        self._noise_profile = []
        self.noise_floor = 0.0
        logger.info(f"Calibrating noise filter for {duration_seconds}s...")
        return self.noise_floor

    def reset(self) -> None:
        """Reset noise filter adaptation."""
        with self._lock:
            self.is_adapting = True
            self.adaptation_samples = 0
            self._noise_profile = []
            self.noise_floor = 0.0


class DistanceFilter:
    """Filter audio based on distance (only capture within range)."""

    def __init__(
        self,
        max_distance_cm: int = settings.AUDIO_MAX_DISTANCE,
        min_distance_cm: int = 0,
    ):
        self.max_distance_cm = max_distance_cm
        self.min_distance_cm = min_distance_cm
        self.attenuation_factor = 0.0

    def update_distance(self, distance_cm: int) -> bool:
        """Update current distance and return if within range."""
        if distance_cm > self.max_distance_cm:
            self.attenuation_factor = 0.0
            return False
        if distance_cm < self.min_distance_cm:
            self.attenuation_factor = 0.0
            return False

        optimal_distance = 100
        if distance_cm <= optimal_distance:
            self.attenuation_factor = 1.0
        else:
            distance_ratio = distance_cm / optimal_distance
            self.attenuation_factor = max(0.0, 1.0 - (distance_ratio - 1) * 0.5)

        return True

    def apply_attenuation(self, audio_data: bytes) -> bytes:
        """Apply distance-based attenuation to audio."""
        if self.attenuation_factor <= 0:
            return b""

        if self.attenuation_factor >= 1.0:
            return audio_data

        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767.0
        audio_array = audio_array * self.attenuation_factor
        audio_array = np.clip(audio_array * 32767, -32768, 32767).astype(np.int16)
        return audio_array.tobytes()

    def is_within_range(self, distance_cm: int) -> bool:
        """Check if distance is within capture range."""
        return self.min_distance_cm <= distance_cm <= self.max_distance_cm


class AudioProcessor:
    """Combined audio processor with noise filtering and distance control."""

    def __init__(self):
        self.noise_filter = NoiseFilter()
        self.distance_filter = DistanceFilter()
        self.is_processing = False

    def process(self, audio_data: bytes, distance_cm: int = 100) -> bytes:
        """Process audio with noise filtering and distance control."""
        if not self.distance_filter.update_distance(distance_cm):
            logger.debug(f"Distance {distance_cm}cm outside capture range")
            return b""

        filtered = self.noise_filter.filter(audio_data)
        if not filtered:
            return b""

        return self.distance_filter.apply_attenuation(filtered)

    def calibrate(self, duration: float = 2.0) -> None:
        """Calibrate noise filter."""
        self.noise_filter.calibrate(duration)

    def reset(self) -> None:
        """Reset all filters."""
        self.noise_filter.reset()
        self.distance_filter = DistanceFilter()


class VoiceActivationDetector:
    """Detect voice activation above threshold."""

    def __init__(
        self,
        threshold: float = settings.AUDIO_VOICE_ACTIVATION_THRESHOLD,
        min_duration_ms: int = 100,
    ):
        self.threshold = threshold
        self.min_duration_ms = min_duration_ms
        self.is_voiced = False
        self.voice_start_time: float = 0
        self.sample_rate = settings.AUDIO_SAMPLE_RATE

    def detect(self, audio_data: bytes) -> bool:
        """Detect if voice is present in audio."""
        if not audio_data:
            return False

        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767.0
        rms = np.sqrt(np.mean(audio_array ** 2))

        current_time = time.time()

        if rms > self.threshold:
            if not self.is_voiced:
                self.is_voiced = True
                self.voice_start_time = current_time

            voiced_duration = (current_time - self.voice_start_time) * 1000
            return voiced_duration >= self.min_duration_ms
        else:
            self.is_voiced = False
            return False


_audio_processor_instance: Optional[AudioProcessor] = None


def get_audio_processor() -> AudioProcessor:
    """Get global audio processor instance."""
    global _audio_processor_instance
    if _audio_processor_instance is None:
        _audio_processor_instance = AudioProcessor()
    return _audio_processor_instance