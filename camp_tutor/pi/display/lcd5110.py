"""Nokia LCD 5110 display driver."""

import logging
import time
from typing import TYPE_CHECKING, Any, Optional

from config import settings

if TYPE_CHECKING:
    import Adafruit_Nokia_LCD
    import Adafruit_GPIO
    import PIL

logger = logging.getLogger(__name__)

try:
    import Adafruit_Nokia_LCD as NokiaLCD
    import Adafruit_GPIO as GPIO
    HAS_NOKIA_LCD = True
except ImportError:
    HAS_NOKIA_LCD = False


class LCD5110:
    """Nokia 5110 LCD display driver."""

    def __init__(
        self,
        width: int = settings.LCD_WIDTH,
        height: int = settings.LCD_HEIGHT,
    ):
        self.width = width
        self.height = height
        self.disp: Optional[Any] = None
        self.image: Optional[Any] = None
        self.draw: Optional[Any] = None
        self._initialized = False

    def initialize(self, spi=None, gpio=None) -> bool:
        """Initialize the LCD."""
        if not HAS_NOKIA_LCD:
            logger.warning("Nokia LCD library not available")
            return False

        try:
            if spi is None:
                import Adafruit_GPIO.SPI as SPI
                spi = SPI.SpiDev(0, 0, max_speed_hz=4000000)

            if gpio is None:
                import Adafruit_GPIO.PCF8574 as PCF8574
                gpio = GPIO.GPIO.get_platform_gpio()

            self.disp = NokiaLCD.PCD8544(
                spi,
                gpio,
                dc=23,
                rst=24,
                cs=8,
            )

            self.disp.begin(contrast=settings.LCD_CONTRAST)
            self._initialized = True
            self.clear()
            logger.info("LCD initialized")
            return True

        except Exception as e:
            logger.error(f"LCD init failed: {e}")
            return False

    def clear(self) -> None:
        """Clear the display."""
        if not self._initialized:
            return
        self.disp.clear()

    def show_text(self, text: str, line: int = 0) -> None:
        """Show text on a specific line."""
        if not self._initialized:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont
            self.image = Image.new("1", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            font = ImageFont.load_default()
            self.draw.text((0, line * 8), text, font=font, fill=255)

            self.disp.image(self.image)
            self.disp.display()

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
        if not self._initialized:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont
            self.image = Image.new("1", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            font = ImageFont.load_default()

            self.draw.text((0, 0), f"Camp Tutor", font=font, fill=255)
            self.draw.text((0, 8), f"State: {state}", font=font, fill=255)

            if language:
                self.draw.text((0, 16), f"Lang: {language[:10]}", font=font, fill=255)
            elif student:
                self.draw.text((0, 16), f"Student: {student[:12]}", font=font, fill=255)

            if topic:
                self.draw.text((0, 24), f"Topic: {topic[:12]}", font=font, fill=255)

            self.disp.image(self.image)
            self.disp.display()

        except Exception as e:
            logger.error(f"Show status failed: {e}")

    def show_progress(self, progress: int, total: int) -> None:
        """Show progress bar."""
        if not self._initialized:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont
            self.image = Image.new("1", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            font = ImageFont.load_default()

            bar_width = (self.width - 4) * progress // max(total, 1)
            self.draw.rectangle((2, 30, self.width - 2, 38), outline=255, fill=0)
            self.draw.rectangle((2, 30, 2 + bar_width, 38), fill=255)

            self.draw.text((0, 40), f"{progress}/{total}", font=font, fill=255)

            self.disp.image(self.image)
            self.disp.display()

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


_lcd_instance: Optional[LCD5110] = None


def get_lcd() -> LCD5110:
    """Get global LCD instance."""
    global _lcd_instance
    if _lcd_instance is None:
        if HAS_NOKIA_LCD:
            _lcd_instance = LCD5110()
        else:
            _lcd_instance = MockLCD5110()
    return _lcd_instance