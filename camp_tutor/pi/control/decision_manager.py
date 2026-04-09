"""Decision manager - implements LOOK->MEASURE->DECIDE->MOVE with omni support."""

import logging
import time
from typing import Optional

from config import settings
from control import rex_client

logger = logging.getLogger(__name__)


class DecisionManager:
    """Manages robot decision making with safety checks."""

    def __init__(self):
        self.rex = rex_client.get_rex_client()
        self.last_direction = "CENTER"
        self.is_moving = False

    def initialize(self) -> bool:
        """Initialize decision manager."""
        if not self.rex.connect():
            logger.warning("Could not connect to REX - continuing without hardware")
            return True  # Continue without REX - use mock

        status = self.rex.get_status()
        if not status.startswith("STATUS:"):
            logger.warning("REX status check failed")
            return True  # Continue with warning

        logger.info("Decision manager initialized")
        return True

    def look_and_measure(self, direction: str) -> dict:
        """LOOK in direction and MEASURE distance."""
        direction_upper = direction.upper()
        look_result = self.rex.look(direction_upper)

        if not look_result:
            logger.error(f"LOOK:{direction} failed")
            return {
                "safe": False,
                "direction": direction,
                "distance": -1,
                "error": "LOOK_FAILED",
            }

        self.last_direction = direction

        time.sleep(0.2)

        distance = self.rex.get_distance()

        if distance < 0:
            logger.error("Distance measurement failed")
            return {
                "safe": False,
                "direction": direction,
                "distance": -1,
                "error": "DISTANCE_FAILED",
            }

        safe = distance >= settings.REX_MIN_SAFE_DISTANCE

        logger.info(f"LOOK:{direction} -> DIST:{distance}cm -> {'SAFE' if safe else 'BLOCKED'}")

        return {
            "safe": safe,
            "direction": direction,
            "distance": distance,
            "error": None,
        }

    def decide(self, measure_result: dict) -> bool:
        """DECIDE whether path is clear."""
        if measure_result.get("error"):
            logger.warning(f"Decision blocked by error: {measure_result['error']}")
            return False

        safe = measure_result.get("safe", False)
        distance = measure_result.get("distance", 0)

        if not safe:
            logger.warning(f"Path blocked: distance={distance}cm < {settings.REX_MIN_SAFE_DISTANCE}cm")

        return safe

    def move(self, direction: str) -> bool:
        """MOVE in direction after LOOK->MEASURE->DECIDE."""
        measure_result = self.look_and_measure(direction)

        if not self.decide(measure_result):
            logger.warning(f"Cannot move {direction}: path blocked")
            return False

        self.is_moving = True

        move_result = self.rex.move(direction)

        self.is_moving = False

        if not move_result:
            logger.error(f"MOVE:{direction} failed")
            return False

        logger.info(f"Moved {direction}")
        return True

    def omni_move(self, direction: str) -> bool:
        """MOVE with omni-directional wheels after LOOK->MEASURE->DECIDE."""
        direction_upper = direction.upper()
        
        # Skip distance check for rotation commands
        if "ROTATE" not in direction_upper:
            measure_result = self.look_and_measure(self.last_direction)

            if not self.decide(measure_result):
                logger.warning(f"Cannot omni_move {direction}: path blocked")
                return False

        self.is_moving = True

        move_result = self.rex.omni_move(direction_upper)

        self.is_moving = False

        if not move_result:
            logger.error(f"OMNI:{direction} failed")
            return False

        logger.info(f"Omni-moved {direction}")
        return True

    def move_to_target(self, target: str) -> bool:
        """Move to target with full safety check."""
        direction_map = {
            "forward": "FWD",
            "backward": "BACK",
            "left": "LEFT",
            "right": "RIGHT",
            "front": "FWD",
            "back": "BACK",
            "forward_left": "FL",
            "forward_right": "FR",
            "back_left": "BL",
            "back_right": "BR",
            "rotate_left": "RL",
            "rotate_right": "RR",
        }

        direction = direction_map.get(target.lower(), target.upper())
        
        # Use omni_move for directions that start with F, B, R, L (not basic directions)
        if direction in ["FL", "FR", "BL", "BR", "RL", "RR"]:
            return self.omni_move(direction)
        
        return self.move(direction)

    def stop(self) -> bool:
        """Emergency stop."""
        self.is_moving = False
        result = self.rex.stop()
        logger.warning("Emergency stop triggered")
        return result

    def reset(self) -> bool:
        """Reset system after emergency stop."""
        result = self.rex.reset()
        if result:
            logger.info("REX system reset")
        return result

    def home(self) -> bool:
        """Return to home position."""
        result = self.rex.home()
        if result:
            self.last_direction = "CENTER"
            logger.info("REX returned to home")
        return result

    def get_status(self) -> str:
        """Get robot status."""
        return self.rex.get_status()


_decision_manager_instance: Optional[DecisionManager] = None


def get_decision_manager() -> DecisionManager:
    """Get global decision manager instance."""
    global _decision_manager_instance
    if _decision_manager_instance is None:
        _decision_manager_instance = DecisionManager()
    return _decision_manager_instance