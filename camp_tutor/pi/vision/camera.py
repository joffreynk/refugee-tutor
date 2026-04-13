"""Pi Camera interface module."""

import logging
import threading
import time
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    try:
        from picamera import Camera
        HAS_PICAMERA = True
    except ImportError:
        HAS_PICAMERA = False


class Camera:
    """Pi Camera v2 interface."""

    def __init__(
        self,
        width: int = settings.CAMERA_WIDTH,
        height: int = settings.CAMERA_HEIGHT,
    ):
        self.width = width
        self.height = height
        self.camera: Optional[Any] = None
        self.is_streaming = False
        self._stream_thread: Optional[threading.Thread] = None

    def initialize(self) -> bool:
        """Initialize the camera."""
        if not HAS_PICAMERA:
            logger.warning("PiCamera not available")
            return False

        try:
            self.camera = Picamera2()
            config = self.camera.create_still_configuration()
            self.camera.configure(config)
            self.camera.start()
            logger.info("Camera initialized")
            return True
        except Exception as e:
            logger.error(f"Camera init failed: {e}")
            return False

    def capture_image(self, path: Optional[Path] = None) -> Optional[Path]:
        """Capture a single image."""
        if not self.camera:
            return None

        if path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = settings.DATA_DIR / f"capture_{timestamp}.jpg"

        try:
            self.camera.capture(str(path))
            logger.debug(f"Captured image: {path}")
            return path
        except Exception as e:
            logger.error(f"Image capture failed: {e}")
            return None

    def start_stream(self) -> None:
        """Start continuous streaming."""
        if self.is_streaming:
            return

        self.is_streaming = True
        self._stream_thread = threading.Thread(target=self._stream_loop)
        self._stream_thread.daemon = True
        self._stream_thread.start()

    def _stream_loop(self) -> None:
        """Streaming loop."""
        while self.is_streaming:
            try:
                frame = self.camera.capture_array()
            except Exception:
                pass
            time.sleep(1.0 / settings.CAMERA_FRAMERATE)

    def stop_stream(self) -> None:
        """Stop streaming."""
        self.is_streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=2.0)
            self._stream_thread = None

    def close(self) -> None:
        """Close camera."""
        self.stop_stream()
        if self.camera:
            self.camera.close()
            self.camera = None
        logger.info("Camera closed")

    def is_ready(self) -> bool:
        """Check if camera is ready."""
        return self.camera is not None


class SimpleCamera:
    """Fallback camera without Picamera2."""

    def __init__(self):
        self.is_streaming = False

    def initialize(self) -> bool:
        """Initialize (no-op for fallback)."""
        logger.warning("Using simple camera (no actual camera)")
        return True

    def capture_image(self, path: Optional[Path] = None) -> Optional[Path]:
        """Capture (returns None for fallback)."""
        logger.warning("Camera not available")
        return None

    def start_stream(self) -> None:
        """Start streaming (no-op)."""
        pass

    def stop_stream(self) -> None:
        """Stop streaming (no-op)."""
        pass

    def close(self) -> None:
        """Close (no-op)."""
        pass

    def is_ready(self) -> bool:
        """Check if ready."""
        return False


_camera_instance: Optional[Camera] = None


def get_camera() -> Camera:
    """Get global camera instance."""
    global _camera_instance
    if _camera_instance is None:
        if HAS_PICAMERA:
            _camera_instance = Camera()
        else:
            _camera_instance = SimpleCamera()
    return _camera_instance