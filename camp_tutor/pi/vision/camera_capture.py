"""Camera capture module for student photos and visual monitoring."""

import logging
import time
import io
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV not available - camera features limited")

try:
    from picamera2 import Picamera2
    HAS_PICAMERA2 = True
except ImportError:
    HAS_PICAMERA2 = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL not available - image processing limited")


class CameraCapture:
    """Camera capture for student photos."""

    def __init__(self):
        self._camera = None
        self._initialized = False
        self._resolution = (settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
        self._last_capture_time = 0

    def initialize(self) -> bool:
        """Initialize camera with fallback options."""
        if self._initialized:
            return True

        if HAS_CV2:
            try:
                self._camera = cv2.VideoCapture(0)
                if self._camera.isOpened():
                    self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
                    self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
                    self._camera.set(cv2.CAP_PROP_FPS, settings.CAMERA_FRAMERATE)
                    self._initialized = True
                    logger.info("Camera initialized with OpenCV")
                    return True
            except Exception as e:
                logger.warning(f"OpenCV camera failed: {e}")
        
        if HAS_PICAMERA2:
            try:
                self._picamera = Picamera2()
                self._picamera.configure(self._picamera.create_still_configuration())
                self._picamera.start()
                self._initialized = True
                logger.info("Camera initialized with picamera2")
                return True
            except Exception as e:
                logger.warning(f"picamera2 failed: {e}")
        
        logger.error("No camera library available - install opencv-python or picamera2")
        return False

    def is_ready(self) -> bool:
        """Check if camera is ready."""
        if not self._initialized or self._camera is None:
            return False
        return self._camera.isOpened()

    def capture_frame(self) -> Optional[bytes]:
        """Capture a single frame and return as bytes."""
        if not self.is_ready():
            return None

        try:
            ret, frame = self._camera.read()
            if ret:
                _, buffer = cv2.imencode(".jpg", frame)
                return buffer.tobytes()
        except Exception as e:
            logger.error(f"Capture frame error: {e}")

        return None

    def capture_image(self, filepath: Optional[Path] = None) -> Optional[str]:
        """Capture an image and save to file."""
        if not self.is_ready():
            return None

        if filepath is None:
            timestamp = int(time.time())
            filepath = settings.DATA_DIR / f"capture_{timestamp}.jpg"

        try:
            ret, frame = self._camera.read()
            if ret:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(filepath), frame)
                return str(filepath)
        except Exception as e:
            logger.error(f"Capture image error: {e}")

        return None

    def detect_faces(self) -> list:
        """Detect faces in current frame."""
        if not self.is_ready() or not HAS_CV2:
            return []

        try:
            ret, frame = self._camera.read()
            if not ret:
                return []

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )
            return faces.tolist() if len(faces) > 0 else []

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []

    def capture_for_student(self, student_id: str, filename: Optional[str] = None) -> Optional[str]:
        """Capture photo for a specific student."""
        if not self.is_ready():
            return None

        student_photos_dir = settings.DATA_DIR / "student_photos" / student_id
        student_photos_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = int(time.time() * 1000)
            filename = f"photo_{timestamp}.jpg"

        filepath = student_photos_dir / filename

        try:
            ret, frame = self._camera.read()
            if ret:
                cv2.imwrite(str(filepath), frame)
                logger.info(f"Captured photo for student {student_id}: {filepath}")
                return str(filepath)
        except Exception as e:
            logger.error(f"Student photo capture error: {e}")

        return None

    def capture_batch(self, student_id: str, count: int = 5) -> list:
        """Capture multiple photos for a student."""
        if not self.is_ready():
            return []

        student_photos_dir = settings.DATA_DIR / "student_photos" / student_id
        student_photos_dir.mkdir(parents=True, exist_ok=True)

        student_name = f"student_{student_id}"
        
        filepaths = []
        for i in range(count):
            filepath = student_photos_dir / f"{student_name}_{i+1}.jpg"
            try:
                ret, frame = self._camera.read()
                if ret:
                    cv2.imwrite(str(filepath), frame)
                    filepaths.append(str(filepath))
                    time.sleep(0.3)
            except Exception as e:
                logger.error(f"Batch capture error: {e}")
        
        logger.info(f"Captured {len(filepaths)} photos for student {student_id}")
        return filepaths

    def get_preview_frame(self) -> Optional[bytes]:
        """Get a preview frame for web UI."""
        if not self.is_ready():
            return None

        try:
            ret, frame = self._camera.read()
            if ret:
                _, buffer = cv2.imencode(".jpg", frame)
                return buffer.tobytes()
        except Exception as e:
            logger.error(f"Preview frame error: {e}")

        return None

    def close(self) -> None:
        """Close camera."""
        if self._camera:
            self._camera.release()
            self._camera = None
            self._initialized = False
            logger.info("Camera closed")


class PiCameraCapture:
    """Pi-specific camera capture using picamera2."""

    def __init__(self):
        self._camera = None
        self._initialized = False
        self._resolution = (settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)

    def initialize(self) -> bool:
        """Initialize Pi camera."""
        if self._initialized:
            return True

        try:
            from picamera2 import Picamera2
            self._camera = Picamera2()
            config = self._camera.create_still_configuration()
            self._camera.configure(config)
            self._camera.start()
            self._initialized = True
            logger.info("Pi Camera initialized successfully")
            return True
        except ImportError:
            logger.warning("picamera2 not available")
            return False
        except Exception as e:
            logger.error(f"Pi camera initialization failed: {e}")
            return False

    def is_ready(self) -> bool:
        """Check if camera is ready."""
        return self._initialized and self._camera is not None

    def capture_image(self, filepath: Path) -> bool:
        """Capture image to file."""
        if not self.is_ready():
            return False

        try:
            self._camera.capture_file(str(filepath))
            return True
        except Exception as e:
            logger.error(f"Pi camera capture error: {e}")
            return False

    def close(self) -> None:
        """Close camera."""
        if self._camera:
            self._camera.close()
            self._camera = None
            self._initialized = False


_camera_instance: Optional[CameraCapture] = None


def get_camera() -> CameraCapture:
    """Get global camera instance."""
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = CameraCapture()
    return _camera_instance


_pi_camera_instance: Optional[PiCameraCapture] = None


def get_pi_camera() -> PiCameraCapture:
    """Get Pi-specific camera instance."""
    global _pi_camera_instance
    if _pi_camera_instance is None:
        _pi_camera_instance = PiCameraCapture()
    return _pi_camera_instance