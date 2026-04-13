"""REX Serial USB client module."""

import glob
import logging
import os
import time
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    logger.warning("Serial library not available")


def _find_rex_serial_port() -> str:
    """Auto-detect REX serial port."""
    if os.path.exists(settings.REX_SERIAL_PORT):
        return settings.REX_SERIAL_PORT
    
    patterns = [
        "/dev/ttyUSB*",
        "/dev/ttyACM*",
        "/dev/cu.usbserial-*",
        "/dev/cu.usbmodem*",
    ]
    
    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            ports.sort()
            return ports[0]
    
    return settings.REX_SERIAL_PORT


class REXClient:
    """Serial USB client for REX robot controller."""

    def __init__(self, port: str = None, baudrate: int = None):
        self.port = port or _find_rex_serial_port()
        self.baudrate = baudrate or settings.REX_SERIAL_BAUDRATE
        self.serial: Optional[serial.Serial] = None
        self._connected = False
        self._last_error: Optional[str] = None

    def connect(self) -> bool:
        """Connect to REX via Serial USB."""
        if not HAS_SERIAL:
            self._last_error = "PySerial not available"
            logger.warning("PySerial not available")
            return False

        try:
            import serial
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)
            self._connected = True
            logger.info(f"Connected to REX on {self.port}")
            return True
        except Exception as e:
            self._last_error = str(e)
            logger.warning(f"Could not connect to REX: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if REX is connected."""
        return self._connected and self.serial is not None

    def disconnect(self) -> None:
        """Disconnect from REX."""
        self._connected = False
        if self.serial:
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
        logger.info("Disconnected from REX")

    def _write_command(self, command: str) -> bool:
        """Write command to REX."""
        if not self.is_connected():
            return False
        try:
            self.serial.write(f"{command}\n".encode())
            self.serial.flush()
            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def _read_response(self, timeout: float = 1.0) -> str:
        """Read response from REX."""
        if not self.is_connected():
            return "ERROR:NOT_CONNECTED"
        try:
            self.serial.timeout = timeout
            response = self.serial.readline()
            return response.decode().strip() if response else ""
        except Exception as e:
            self._last_error = str(e)
            return f"ERROR:{e}"

    def send_command(self, command: str, retries: int = 1) -> str:
        """Send command and get response."""
        if not self.is_connected():
            if retries > 0:
                self.connect()
            if not self.is_connected():
                return "ERROR:REX_NOT_AVAILABLE"

        for attempt in range(retries + 1):
            if self._write_command(command):
                response = self._read_response()
                if response and not response.startswith("ERROR"):
                    return response
            time.sleep(0.1)
        
        return self._last_error or "ERROR:NO_RESPONSE"

    def ping(self) -> bool:
        """Ping REX to check if alive."""
        response = self.send_command("STATUS?")
        logger.info(f"REX ping: '{response}'")
        return not response.startswith("ERROR") and response != ""

    def get_distance(self) -> float:
        """Get distance from ultrasonic sensor."""
        response = self.send_command("DISTANCE?")
        if response.startswith("ERROR"):
            return -1
        try:
            return float(response.strip())
        except ValueError:
            return -1

    def move_forward(self, speed: int = 100) -> bool:
        """Move forward."""
        response = self.send_command(f"MOVE:FWD:{speed}")
        return not response.startswith("ERROR")

    def move_backward(self, speed: int = 100) -> bool:
        """Move backward."""
        response = self.send_command(f"MOVE:BACK:{speed}")
        return not response.startswith("ERROR")

    def move_left(self, speed: int = 100) -> bool:
        """Move left."""
        response = self.send_command(f"MOVE:LEFT:{speed}")
        return not response.startswith("ERROR")

    def move_right(self, speed: int = 100) -> bool:
        """Move right."""
        response = self.send_command(f"MOVE:RIGHT:{speed}")
        return not response.startswith("ERROR")

    def move(self, direction: str, distance: int = 30) -> bool:
        """Move in direction."""
        response = self.send_command(f"MOVE:{direction}:{distance}")
        return not response.startswith("ERROR")

    def stop(self) -> bool:
        """Stop all movement."""
        response = self.send_command("STOP")
        return not response.startswith("ERROR")

    def look(self, direction: str) -> bool:
        """Move camera head (LEFT, CENTER, RIGHT)."""
        response = self.send_command(f"LOOK:{direction}")
        return not response.startswith("ERROR")

    def set_servo_angle(self, servo: str, angle: int) -> bool:
        """Set servo angle."""
        response = self.send_command(f"SERVO:{servo}:{angle}")
        return not response.startswith("ERROR")

    def get_status(self) -> dict:
        """Get REX status."""
        return {
            "connected": self._connected,
            "port": self.port,
            "last_error": self._last_error,
        }


class MockREXClient:
    """Mock REX client for testing without hardware."""

    def __init__(self, port: str = None, baudrate: int = None):
        self.port = port or "/dev/ttyUSB0"
        self.baudrate = baudrate or 9600
        self._connected = False

    def connect(self) -> bool:
        self._connected = True
        return True

    def is_connected(self) -> bool:
        return False

    def disconnect(self) -> None:
        self._connected = False

    def ping(self) -> bool:
        return True

    def get_distance(self) -> float:
        return 50.0

    def move_forward(self, speed: int = 100) -> bool:
        return True

    def move_backward(self, speed: int = 100) -> bool:
        return True

    def move_left(self, speed: int = 100) -> bool:
        return True

    def move_right(self, speed: int = 100) -> bool:
        return True

    def move(self, direction: str, distance: int = 30) -> bool:
        return True

    def stop(self) -> bool:
        return True

    def look(self, direction: str) -> bool:
        return True

    def set_servo_angle(self, servo: str, angle: int) -> bool:
        return True

    def get_status(self) -> dict:
        return {"connected": False, "port": self.port, "last_error": None}


_rex_client: Optional[REXClient] = None


def get_rex_client(serial_port: str = None) -> REXClient:
    """Get global REX client instance."""
    global _rex_client
    if _rex_client is None:
        _rex_client = REXClient(port=serial_port)
    return _rex_client