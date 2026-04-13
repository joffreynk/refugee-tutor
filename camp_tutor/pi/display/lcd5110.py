"""Nokia LCD 5110 display driver using CircuitPython library."""

import logging
import time
from typing import TYPE_CHECKING, Any, Optional
from pathlib import Path

from config import settings

if TYPE_CHECKING:
    import PIL
    import digitalio
    import busio

logger = logging.getLogger(__name__)

try:
    from adafruit_pcd8544 import PCD8544
    import board
    import busio
    import digitalio
    HAS_NOKIA_LCD = True
except ImportError:
    HAS_NOKIA_LCD = False


class LCD5110:
    """Nokia 5110 LCD display driver using CircuitPython."""

    def __init__(
        self,
        width: int = settings.LCD_WIDTH,
        height: int = settings.LCD_HEIGHT,
    ):
        self.width = width
        self.height = height
        self.disp: Optional[Any] = None
        self._spi = None
        self._dc = None
        self._rst = None
        self._cs = None
        self._initialized = False

    def initialize(self, spi=None, gpio=None) -> bool:
        """Initialize the LCD."""
        if not HAS_NOKIA_LCD:
            logger.warning("CircuitPython Nokia LCD library not available, using mock")
            return False

        try:
            import board
            import digitalio

            self._spi = board.SPI()

            self._dc = digitalio.DigitalInOut(board.D23)
            self._dc.direction = digitalio.Direction.OUTPUT

            self._rst = digitalio.DigitalInOut(board.D24)
            self._rst.direction = digitalio.Direction.OUTPUT

            self._cs = digitalio.DigitalInOut(board.D8)
            self._cs.direction = digitalio.Direction.OUTPUT

            self._led = digitalio.DigitalInOut(board.D18)
            self._led.direction = digitalio.Direction.OUTPUT
            self._led.value = True

            self.disp = PCD8544(
                self._spi,
                self._dc,
                self._rst,
                self._cs,
                baudrate=4000000,
            )

            self.disp.contrast = 60
            self.disp.fill(0)
            self.disp.show()

            self._initialized = True
            self.clear()
            logger.info("LCD initialized (CircuitPython)")
            return True

        except Exception as e:
            logger.error(f"LCD init failed: {e}")
            return False

    def clear(self) -> None:
        """Clear the display."""
        if not self._initialized or self.disp is None:
            return
        self.disp.fill(0)
        self.disp.show()

    def show_text(self, text: str, line: int = 0) -> None:
        """Show text on a specific line."""
        if not self._initialized or self.disp is None:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(img)

            font = ImageFont.load_default()

            text_to_show = text[:16]
            y_pos = line * 8
            draw.text((0, y_pos), text_to_show, font=font, fill=255)

            self.disp.image(img)
            self.disp.show()

        except ImportError:
            logger.warning("PIL not available, using simple text")
            if line == 0:
                self.disp.fill(0)
                self.disp.text(text[:16], 0, 0)
                self.disp.show()
        except Exception as e:
            logger.error(f"Show text failed: {e}")

    def show_status(
        self,
        state: str,
        student: Optional[str] = None,
        topic: Optional[str] = None,
        language: Optional[str] = None,
    ) -> None:
        """Show full status screen."""
        if not self._initialized or self.disp is None:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(img)

            font = ImageFont.load_default()

            draw.text((0, 0), "Camp Tutor", font=font, fill=255)
            draw.text((0, 8), f"State: {state[:11]}", font=font, fill=255)

            if language:
                draw.text((0, 16), f"Lang: {language[:10]}", font=font, fill=255)
            elif student:
                draw.text((0, 16), f"Student: {student[:10]}", font=font, fill=255)

            if topic:
                draw.text((0, 24), f"Topic: {topic[:12]}", font=font, fill=255)

            self.disp.image(img)
            self.disp.show()

        except Exception as e:
            logger.error(f"Show status failed: {e}")

    def show_progress(self, progress: int, total: int) -> None:
        """Show progress bar."""
        if not self._initialized or self.disp is None:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(img)

            font = ImageFont.load_default()

            bar_width = (self.width - 4) * progress // max(total, 1)
            draw.rectangle((2, 30, self.width - 2, 38), outline=255, fill=0)
            draw.rectangle((2, 30, 2 + bar_width, 38), fill=255)

            draw.text((0, 40), f"{progress}/{total}", font=font, fill=255)

            self.disp.image(img)
            self.disp.show()

        except Exception as e:
            logger.error(f"Show progress failed: {e}")

    def close(self) -> None:
        """Close the display."""
        if self.disp:
            self.clear()
            self.disp = None
            self._initialized = False


class MockLCD5110:
    """Mock LCD for testing without hardware."""

    def __init__(self):
        self.last_text: list[str] = [""] * 6

    def initialize(self, spi=None, gpio=None) -> bool:
        """Initialize mock LCD."""
        logger.info("Mock LCD initialized")
        return True

    def clear(self) -> None:
        """Clear mock display."""
        self.last_text = [""] * 6

    def show_text(self, text: str, line: int = 0) -> None:
        """Show text on mock display."""
        if 0 <= line < 6:
            self.last_text[line] = text
            logger.debug(f"LCD[{line}]: {text}")

    def show_status(
        self,
        state: str,
        student: Optional[str] = None,
        topic: Optional[str] = None,
        language: Optional[str] = None,
    ) -> None:
        """Show status on mock display."""
        self.show_text("Camp Tutor", 0)
        self.show_text(f"State: {state}", 1)
        if language:
            self.show_text(f"Lang: {language[:12]}", 2)
        elif student:
            self.show_text(f"Student: {student[:12]}", 2)
        if topic:
            self.show_text(f"Topic: {topic[:12]}", 3)

    def show_progress(self, progress: int, total: int) -> None:
        """Show progress on mock display."""
        self.show_text(f"Progress: {progress}/{total}", 4)

    def close(self) -> None:
        """Close mock display."""
        pass


_lcd_instance: Optional[Any] = None


def get_lcd() -> Any:
    """Get global LCD instance."""
    global _lcd_instance
    if _lcd_instance is None:
        if HAS_NOKIA_LCD:
            _lcd_instance = LCD5110()
        else:
            _lcd_instance = MockLCD5110()
    return _lcd_instance