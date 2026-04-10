"""REX I2C client module - resilient to hardware failures."""

import logging
import time
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    import smbus2 as smbus
    HAS_SMBUS = True
except ImportError:
    try:
        import smbus
        HAS_SMBUS = True
    except ImportError:
        HAS_SMBUS = False


class REXClient:
    """I2C client for REX controller - resilient to connection failures."""

    def __init__(
        self,
        address: int = settings.I2C_ADDRESS,
        bus_number: int = 1,
    ):
        self.address = address
        self.bus_number = bus_number
        self.bus: Optional[Any] = None
        self._connected = False
        self._last_error: Optional[str] = None
        self._consecutive_failures = 0
        self._max_failures = 5

    def connect(self) -> bool:
        """Connect to REX controller."""
        if not HAS_SMBUS:
            self._last_error = "SMBus not available"
            logger.warning("SMBus not available")
            return False

        try:
            self.bus = smbus.SMBus(self.bus_number)
            self._connected = True
            self._consecutive_failures = 0
            logger.info(f"Connected to REX at 0x{self.address:02X}")
            return True
        except Exception as e:
            self._last_error = str(e)
            logger.warning(f"Could not connect to REX: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if REX is connected and responding."""
        return self._connected and self._consecutive_failures < self._max_failures

    def get_status(self) -> dict:
        """Get REX status for device monitoring."""
        return {
            "connected": self._connected,
            "responding": self._consecutive_failures < self._max_failures,
            "last_error": self._last_error,
            "consecutive_failures": self._consecutive_failures,
        }

    def disconnect(self) -> None:
        """Disconnect from REX."""
        self._connected = False
        if self.bus:
            try:
                self.bus.close()
            except Exception:
                pass
            self.bus = None
        logger.info("Disconnected from REX")

    def send_command(self, command: str, retries: int = 1) -> str:
        """Send command with minimal retries - fail fast."""
        if not self.is_connected():
            self._consecutive_failures += 1
            return f"ERROR:REX_NOT_AVAILABLE"

        try:
            command_bytes = command.encode("ascii")[:31]
            self.bus.write_i2c_block_data(
                self.address,
                0x00,
                list(command_bytes) + [0] * (32 - len(command_bytes)),
            )

            time.sleep(0.02)

            response_bytes = self.bus.read_i2c_block_data(self.address, 0x00, 32)
            response = bytes(response_bytes).decode("ascii").strip("\x00")

            if response and not response.startswith("ERROR"):
                self._consecutive_failures = 0
                return response

            self._consecutive_failures += 1
            self._last_error = response
            return response

        except Exception as e:
            self._consecutive_failures += 1
            self._last_error = str(e)
            logger.debug(f"REX command error: {e}")
            return f"ERROR:{type(e).__name__}"

    def ping(self) -> bool:
        """Ping REX to check if alive."""
        response = self.send_command("STATUS?", retries=1)
        return response == "OK" and self._consecutive_failures < self._max_failures

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
        """Move servo to direction (LEFT, CENTER, RIGHT)."""
        response = self.send_command(f"LOOK:{direction}")
        return not response.startswith("ERROR")

    def set_servo_angle(self, servo: str, angle: int) -> bool:
        """Set servo angle."""
        response = self.send_command(f"SERVO:{servo}:{angle}")
        return not response.startswith("ERROR")


class MockREXClient:
    """Mock REX for testing or when hardware unavailable."""

    def __init__(self):
        self._connected = False
        self._last_error = "Using mock REX"

    def connect(self) -> bool:
        self._connected = True
        logger.info("Mock REX connected")
        return True

    def is_connected(self) -> bool:
        return True

    def get_status(self) -> dict:
        return {
            "connected": True,
            "responding": True,
            "last_error": "Using mock",
            "consecutive_failures": 0,
        }

    def ping(self) -> bool:
        return True

    def send_command(self, command: str, retries: int = 1) -> str:
        logger.debug(f"Mock REX: {command}")
        return "OK"

    def get_distance(self) -> float:
        return 50.0

    def move_forward(self, speed: int = 100) -> bool:
        logger.debug(f"Mock forward: {speed}")
        return True

    def move_backward(self, speed: int = 100) -> bool:
        logger.debug(f"Mock backward: {speed}")
        return True

    def move_left(self, speed: int = 100) -> bool:
        logger.debug(f"Mock left: {speed}")
        return True

    def move_right(self, speed: int = 100) -> bool:
        logger.debug(f"Mock right: {speed}")
        return True

    def move(self, direction: str, distance: int = 30) -> bool:
        logger.debug(f"Mock move: {direction} {distance}")
        return True

    def stop(self) -> bool:
        logger.debug("Mock stop")
        return True

    def look(self, direction: str) -> bool:
        logger.debug(f"Mock look: {direction}")
        return True

    def set_servo_angle(self, servo: str, angle: int) -> bool:
        logger.debug(f"Mock servo: {servo} {angle}")
        return True

    def disconnect(self) -> None:
        pass


def get_rex_client() -> REXClient:
    """Get REX client instance."""
    return REXClient()