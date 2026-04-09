"""REX I2C client module."""

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
    """I2C client for REX controller."""

    def __init__(
        self,
        address: int = settings.I2C_ADDRESS,
        bus_number: int = 1,
    ):
        self.address = address
        self.bus_number = bus_number
        self.bus: Optional[Any] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to REX controller."""
        if not HAS_SMBUS:
            logger.warning("SMBus not available - using mock client")
            return False

        try:
            self.bus = smbus.SMBus(self.bus_number)
            self._connected = True
            logger.info(f"Connected to REX at 0x{self.address:02X}")
            return True
        except Exception as e:
            logger.error(f"Could not connect to REX: {e}")
            return False

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

    def send_command(self, command: str, retries: int = 3) -> str:
        """Send command and get response with retry logic."""
        if not self._connected:
            return "ERROR:NOT_CONNECTED"

        for attempt in range(retries):
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
                    logger.debug(f"REX command: {command} -> {response}")
                    return response
                
                if "BLOCKED" in response or "STOP" in response:
                    return response
                    
            except Exception as e:
                logger.warning(f"Command attempt {attempt + 1} failed: {e}")
                time.sleep(0.05)

        logger.error(f"Command failed after {retries} attempts: {command}")
        return "ERROR:COMMUNICATION"

    def look(self, direction: str) -> bool:
        """Point head in direction."""
        direction = direction.upper()
        valid_directions = ["LEFT", "CENTER", "RIGHT", "HOME"]
        if direction not in valid_directions:
            logger.warning(f"Invalid look direction: {direction}")
            return False

        response = self.send_command(f"LOOK:{direction}")
        return response.startswith("OK")

    def get_distance(self) -> int:
        """Get ultrasonic distance in cm."""
        response = self.send_command("DIST?")

        if response.startswith("DIST:"):
            try:
                return int(response.split(":")[1])
            except (ValueError, IndexError):
                return -1

        return -1

    def move(self, direction: str) -> bool:
        """Move in direction (basic movement)."""
        direction = direction.upper()
        valid_directions = ["FWD", "BACK", "LEFT", "RIGHT", "FORWARD", "BACKWARD"]
        if direction not in valid_directions:
            logger.warning(f"Invalid move direction: {direction}")
            return False

        # Normalize to short form
        dir_map = {"FORWARD": "FWD", "BACKWARD": "BACK"}
        direction = dir_map.get(direction, direction)
        
        response = self.send_command(f"MOVE:{direction}")
        return response.startswith("OK")

    def omni_move(self, direction: str) -> bool:
        """Move with omni-directional wheels."""
        direction = direction.upper()
        valid_directions = [
            "FWD", "BACK", "LEFT", "RIGHT",
            "FL", "FR", "BL", "BR",  # Forward-left, Forward-right, Back-left, Back-right
            "RL", "RR",  # Rotate left, Rotate right
            "STOP", "FORWARD", "BACKWARD",
            "FORWARD_LEFT", "FORWARD_RIGHT", "BACK_LEFT", "BACK_RIGHT",
            "ROTATE_LEFT", "ROTATE_RIGHT"
        ]
        if direction not in valid_directions:
            logger.warning(f"Invalid omni direction: {direction}")
            return False

        response = self.send_command(f"OMNI:{direction}")
        return response.startswith("OK")

    def stop(self) -> bool:
        """Emergency stop."""
        response = self.send_command("STOP")
        return response.startswith("OK")

    def reset(self) -> bool:
        """Reset system after emergency stop."""
        response = self.send_command("RESET")
        return response.startswith("RESET") or response.startswith("OK")

    def home(self) -> bool:
        """Return to home position."""
        response = self.send_command("HOME")
        return response.startswith("OK")

    def calibrate(self) -> bool:
        """Run calibration routine."""
        response = self.send_command("CALIBRATE")
        return response.startswith("OK")

    def buzzer(self, pattern: str = "SHORT") -> bool:
        """Control buzzer."""
        pattern = pattern.upper()
        valid_patterns = ["SHORT", "LONG", "1", "3"]
        if pattern not in valid_patterns:
            pattern = "SHORT"
        
        response = self.send_command(f"BUZZER:{pattern}")
        return response.startswith("OK")

    def get_status(self) -> str:
        """Get REX status."""
        response = self.send_command("STATUS?")
        return response

    def ping(self) -> bool:
        """Ping REX to check connection."""
        response = self.send_command("PING", retries=1)
        return response == "PONG"

    def is_connected(self) -> bool:
        """Check if connected to REX."""
        return self._connected


class MockREXClient:
    """Mock REX client for testing without hardware."""

    def __init__(self):
        self._connected = False
        self._head_position = "CENTER"
        self._distance = 50
        self._status = "READY"
        self._emergency_stop = False

    def connect(self) -> bool:
        """Connect (mock)."""
        self._connected = True
        logger.info("Mock REX connected")
        return True

    def disconnect(self) -> None:
        """Disconnect (mock)."""
        self._connected = False

    def send_command(self, command: str) -> str:
        """Send command (mock)."""
        if self._emergency_stop:
            return "BLOCKED"
        
        if command.startswith("LOOK:"):
            self._head_position = command.split(":")[1]
            return "OK"
        elif command == "DIST?":
            return f"DIST:{self._distance}"
        elif command.startswith("MOVE:") or command.startswith("OMNI:"):
            return "OK"
        elif command == "STOP":
            self._emergency_stop = True
            self._status = "STOP"
            return "OK"
        elif command == "RESET":
            self._emergency_stop = False
            self._status = "READY"
            return "RESET"
        elif command == "HOME":
            self._head_position = "CENTER"
            return "OK"
        elif command == "CALIBRATE":
            return "OK"
        elif command.startswith("BUZZER:"):
            return "OK"
        elif command == "STATUS?":
            return f"STATUS:{self._status}"
        elif command == "PING":
            return "PONG"
        else:
            return "OK"

    def look(self, direction: str) -> bool:
        """Look (mock)."""
        if self._emergency_stop:
            return False
        self._head_position = direction.upper()
        return True

    def get_distance(self) -> int:
        """Get distance (mock)."""
        return self._distance

    def move(self, direction: str) -> bool:
        """Move (mock)."""
        if self._emergency_stop:
            return False
        return True

    def omni_move(self, direction: str) -> bool:
        """Omni move (mock)."""
        if self._emergency_stop:
            return False
        return True

    def stop(self) -> bool:
        """Stop (mock)."""
        self._emergency_stop = True
        self._status = "STOP"
        return True

    def reset(self) -> bool:
        """Reset (mock)."""
        self._emergency_stop = False
        self._status = "READY"
        return True

    def home(self) -> bool:
        """Home (mock)."""
        self._head_position = "CENTER"
        return True

    def calibrate(self) -> bool:
        """Calibrate (mock)."""
        return True

    def buzzer(self, pattern: str = "SHORT") -> bool:
        """Buzzer (mock)."""
        return True

    def get_status(self) -> str:
        """Get status (mock)."""
        return f"STATUS:{self._status}"

    def ping(self) -> bool:
        """Ping (mock)."""
        return self._connected

    def is_connected(self) -> bool:
        """Check connection (mock)."""
        return self._connected


_rex_client_instance: Optional["REXClient"] = None


def get_rex_client() -> "REXClient":
    """Get global REX client instance."""
    global _rex_client_instance
    if _rex_client_instance is None:
        if HAS_SMBUS:
            try:
                _rex_client_instance = REXClient()
            except Exception:
                _rex_client_instance = MockREXClient()
        else:
            _rex_client_instance = MockREXClient()
    return _rex_client_instance