"""Visual monitoring for interaction awareness."""

import logging
import time
from pathlib import Path
from typing import Optional

from vision import camera

logger = logging.getLogger(__name__)

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class VisualMonitor:
    """Monitors camera for interaction awareness."""

    def __init__(self):
        self.camera = camera.get_camera()
        self.last_capture_time = 0
        self.capture_interval = 5.0
        self.motion_detected = False
        self.person_present = False

    def initialize(self) -> bool:
        """Initialize visual monitoring."""
        return self.camera.initialize()

    def check_motion(self) -> bool:
        """Check for motion in frame."""
        if not self.camera.is_ready():
            return False

        if time.time() - self.last_capture_time < self.capture_interval:
            return self.motion_detected

        self.last_capture_time = time.time()
        self.motion_detected = False

        return False

    def check_person_present(self) -> bool:
        """Check if person is in frame (simplified)."""
        if not self.camera.is_ready():
            return False

        return True

    def capture_for_analysis(self) -> Optional[Path]:
        """Capture image for analysis."""
        if not self.camera.is_ready():
            return None

        return self.camera.capture_image()

    def close(self) -> None:
        """Close visual monitoring."""
        self.camera.close()


class SimpleVisualMonitor:
    """Fallback visual monitor."""

    def __init__(self):
        self.person_present = False

    def initialize(self) -> bool:
        return True

    def check_motion(self) -> bool:
        return False

    def check_person_present(self) -> bool:
        return self.person_present

    def capture_for_analysis(self) -> Optional[Path]:
        return None

    def close(self) -> None:
        pass


_visual_monitor_instance: Optional[VisualMonitor] = None


def get_visual_monitor() -> VisualMonitor:
    """Get global visual monitor instance."""
    global _visual_monitor_instance
    if _visual_monitor_instance is None:
        _visual_monitor_instance = VisualMonitor()
    return _visual_monitor_instance