"""System diagnostic and monitoring UI for Camp Tutor."""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from config import settings
from ui.ui_controls import SystemStatus, DeviceInfo

logger = logging.getLogger(__name__)


class DiagnosticLevel(Enum):
    """Diagnostic severity levels."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticResult:
    """Result of a diagnostic check."""
    def __init__(
        self,
        test_name: str,
        level: DiagnosticLevel,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None,
    ):
        self.test_name = test_name
        self.level = level
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "test": self.test_name,
            "level": self.level.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "time_str": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
        }


class DiagnosticTool:
    """Base class for diagnostic tools."""
    def __init__(self, name: str):
        self.name = name
        self.last_result: Optional[DiagnosticResult] = None

    def run(self) -> DiagnosticResult:
        """Run diagnostic check. Override in subclass."""
        raise NotImplementedError

    def is_critical(self) -> bool:
        """Check if this tool failure is critical."""
        return False


class I2CDiagnostic(DiagnosticTool):
    """Diagnostic for I2C communication."""

    def __init__(self):
        super().__init__("I2C Communication")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()
            
            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "I2C bus not connected",
                    {"address": hex(settings.I2C_ADDRESS)},
                )

            status = rex.get_status()
            if "ERROR" in status:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    f"REX returned error status: {status}",
                    {"status": status},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "I2C communication working",
                {"address": hex(settings.I2C_ADDRESS), "status": status},
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"I2C check failed: {str(e)}",
                {"error": str(e)},
            )

    def is_critical(self) -> bool:
        return True


class REXDiagnostic(DiagnosticTool):
    """Diagnostic for REX controller."""

    def __init__(self):
        super().__init__("REX Controller")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex.ping():
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not responding to ping",
                    {"address": hex(settings.I2C_ADDRESS)},
                )

            distance = rex.get_distance()
            if distance < 0:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    "REX responding but distance sensor error",
                    {"distance": distance},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "REX controller operational",
                {
                    "distance_cm": distance,
                    "safe_distance": settings.REX_MIN_SAFE_DISTANCE,
                    "path_clear": distance >= settings.REX_MIN_SAFE_DISTANCE,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.CRITICAL,
                f"REX check failed: {str(e)}",
                {"error": str(e)},
            )

    def is_critical(self) -> bool:
        return True


class AudioDiagnostic(DiagnosticTool):
    """Diagnostic for audio system."""

    def __init__(self):
        super().__init__("Audio System")

    def run(self) -> DiagnosticResult:
        issues = []
        details = {}

        # Check microphone
        try:
            from audio import speech_to_text
            stt = speech_to_text.SpeechToText()
            details["microphone"] = "ok"
        except Exception as e:
            issues.append(f"STT error: {str(e)}")

        # Check TTS
        try:
            from audio import text_to_speech
            tts = text_to_speech.TextToSpeech()
            details["tts_available"] = tts.is_available()
        except Exception as e:
            issues.append(f"TTS error: {str(e)}")

        if issues:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                "; ".join(issues),
                details,
            )

        return DiagnosticResult(
            self.name,
            DiagnosticLevel.OK,
            "Audio system operational",
            details,
        )


class DisplayDiagnostic(DiagnosticTool):
    """Diagnostic for display system."""

    def __init__(self):
        super().__init__("LCD Display")

    def run(self) -> DiagnosticResult:
        try:
            from display import lcd5110
            lcd = lcd5110.get_lcd()
            
            if lcd is None:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "LCD not initialized",
                    {},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "LCD display operational",
                {"width": settings.LCD_WIDTH, "height": settings.LCD_HEIGHT},
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"LCD check failed: {str(e)}",
                {"error": str(e)},
            )


class DatabaseDiagnostic(DiagnosticTool):
    """Diagnostic for database system."""

    def __init__(self):
        super().__init__("Database")

    def run(self) -> DiagnosticResult:
        try:
            from storage import student_db
            db = student_db.get_student_db()
            
            if db is None:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "Database not initialized",
                    {},
                )

            student_count = db.get_student_count()

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Database operational",
                {"student_count": student_count, "path": str(settings.STUDENT_DB_PATH)},
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.CRITICAL,
                f"Database check failed: {str(e)}",
                {"error": str(e)},
            )

    def is_critical(self) -> bool:
        return True


class WakeWordDiagnostic(DiagnosticTool):
    """Diagnostic for wake word detection."""

    def __init__(self):
        super().__init__("Wake Word")

    def run(self) -> DiagnosticResult:
        try:
            from audio import wake_word
            detector = wake_word.WakeWordDetector()
            
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Wake word detector ready",
                {"wake_word": settings.WAKE_WORD, "sensitivity": settings.WAKE_THRESHOLD},
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                f"Wake word check failed: {str(e)}",
                {"error": str(e)},
            )


class CameraDiagnostic(DiagnosticTool):
    """Diagnostic for camera system."""

    def __init__(self):
        super().__init__("Camera")

    def run(self) -> DiagnosticResult:
        try:
            from vision import camera
            cam = camera.get_camera()
            
            if cam is None:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    "Camera not initialized",
                    {},
                )

            if cam.is_ready():
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.OK,
                    "Camera operational",
                    {"resolution": f"{cam.width}x{cam.height}"},
                )
            else:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    "Camera not ready",
                    {},
                )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                f"Camera check failed: {str(e)}",
                {"error": str(e)},
            )


class UltrasonicDiagnostic(DiagnosticTool):
    """Diagnostic for HC-SR04 ultrasonic sensor."""

    def __init__(self):
        super().__init__("HC-SR04 Ultrasonic")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not connected - cannot read ultrasonic",
                    {"trig_pin": 17, "echo_pin": 16},
                )

            distance = rex.get_distance()

            if distance < 0:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "Ultrasonic sensor error",
                    {"trig_pin": 17, "echo_pin": 16},
                )

            if distance < settings.REX_MIN_SAFE_DISTANCE:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    f"Obstacle detected at {distance}cm",
                    {
                        "distance_cm": distance,
                        "trig_pin": 17,
                        "echo_pin": 16,
                        "min_safe": settings.REX_MIN_SAFE_DISTANCE,
                    },
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                f"Path clear - {distance}cm",
                {
                    "distance_cm": distance,
                    "trig_pin": 17,
                    "echo_pin": 16,
                    "max_range": settings.REX_MAX_DISTANCE,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"Ultrasonic check failed: {str(e)}",
                {"error": str(e)},
            )

    def is_critical(self) -> bool:
        return False


class ServoDiagnostic(DiagnosticTool):
    """Diagnostic for servo (pan/tilt) system."""

    def __init__(self):
        super().__init__("Servo (Pan/Tilt)")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not connected - cannot check servos",
                    {"servo1_pin": 2, "servo2_pin": 26},
                )

            status = rex.get_status()

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Servo system ready",
                {
                    "servo1": {"pin": 2, "function": "Right/Left"},
                    "servo2": {"pin": 26, "function": "Up/Down"},
                    "pulse_range": "600-2500μs",
                    "frequency": "50Hz",
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"Servo check failed: {str(e)}",
                {"error": str(e)},
            )


class MotorDiagnostic(DiagnosticTool):
    """Diagnostic for motor/omni-wheel system."""

    def __init__(self):
        super().__init__("Motors (4-Omni)")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not connected - cannot check motors",
                    {},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Motor system ready",
                {
                    "motor_a": {"fwd": 15, "back": 23, "function": "Front-Left"},
                    "motor_b": {"fwd": 32, "back": 33, "function": "Front-Right"},
                    "motor_c": {"fwd": 5, "back": 4, "function": "Back-Left"},
                    "motor_d": {"fwd": 27, "back": 14, "function": "Back-Right"},
                    "pwm_frequency": "50Hz",
                    "default_speed": settings.DEFAULT_MOTOR_SPEED,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"Motor check failed: {str(e)}",
                {"error": str(e)},
            )

    def is_critical(self) -> bool:
        return True


class EmergencyStopDiagnostic(DiagnosticTool):
    """Diagnostic for emergency stop button."""

    def __init__(self):
        super().__init__("Emergency Stop")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not connected",
                    {"pin": 34, "active_level": "LOW"},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Emergency stop button ready",
                {
                    "pin": 34,
                    "active_level": "LOW (pressed = LOW)",
                    "function": "Stops all motors immediately",
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                f"Emergency stop check: {str(e)}",
                {"error": str(e)},
            )


class BuzzerDiagnostic(DiagnosticTool):
    """Diagnostic for buzzer system."""

    def __init__(self):
        super().__init__("Buzzer")

    def run(self) -> DiagnosticResult:
        try:
            from control import rex_client
            rex = rex_client.get_rex_client()

            if not rex._connected:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.ERROR,
                    "REX not connected",
                    {"pin": 25},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Buzzer ready",
                {"pin": 25, "function": "Audio feedback"},
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                f"Buzzer check: {str(e)}",
                {"error": str(e)},
            )


class LCDDiagnostic(DiagnosticTool):
    """Diagnostic for Nokia LCD 5110 display."""

    def __init__(self):
        super().__init__("LCD Display (Nokia 5110)")

    def run(self) -> DiagnosticResult:
        try:
            from display import lcd5110
            lcd = lcd5110.get_lcd()

            if lcd is None:
                return DiagnosticResult(
                    self.name,
                    DiagnosticLevel.WARNING,
                    "LCD not initialized",
                    {},
                )

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "LCD display operational",
                {
                    "width": settings.LCD_WIDTH,
                    "height": settings.LCD_HEIGHT,
                    "pins": {
                        "RST": 4,
                        "DC": 0,
                        "MOSI": 23,
                        "CLK": 18,
                        "CS": 5,
                    },
                    "interface": "SPI",
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.ERROR,
                f"LCD check failed: {str(e)}",
                {"error": str(e)},
            )


class LanguageDetectorDiagnostic(DiagnosticTool):
    """Diagnostic for language detection."""

    def __init__(self):
        super().__init__("Language Detection")

    def run(self) -> DiagnosticResult:
        try:
            from ai import language_detection
            detector = language_detection.get_language_detector()

            return DiagnosticResult(
                self.name,
                DiagnosticLevel.OK,
                "Language detector ready",
                {
                    "supported_languages": len(settings.LANGUAGE_CODES),
                    "languages": ", ".join(settings.LANGUAGE_CODES[:5]) + "...",
                },
            )
        except Exception as e:
            return DiagnosticResult(
                self.name,
                DiagnosticLevel.WARNING,
                f"Language detection: {str(e)}",
                {"error": str(e)},
            )


class SystemDiagnostics:
    """Main diagnostic runner for all system components."""

    def __init__(self):
        self.tools: List[DiagnosticTool] = [
            I2CDiagnostic(),
            REXDiagnostic(),
            UltrasonicDiagnostic(),
            ServoDiagnostic(),
            MotorDiagnostic(),
            EmergencyStopDiagnostic(),
            BuzzerDiagnostic(),
            LCDDiagnostic(),
            AudioDiagnostic(),
            DatabaseDiagnostic(),
            WakeWordDiagnostic(),
            CameraDiagnostic(),
            LanguageDetectorDiagnostic(),
        ]
        self.last_run: Optional[float] = None
        self.results: List[DiagnosticResult] = []

    def run_all(self) -> List[DiagnosticResult]:
        """Run all diagnostic checks."""
        self.results = []
        self.last_run = time.time()

        for tool in self.tools:
            result = tool.run()
            self.results.append(result)
            logger.info(f"[DIAG] {tool.name}: {result.level.value} - {result.message}")

        return self.results

    def get_summary(self) -> dict:
        """Get diagnostic summary."""
        if not self.results:
            self.run_all()

        counts = {level: 0 for level in DiagnosticLevel}
        for result in self.results:
            counts[result.level] += 1

        critical_tools = [r.test_name for r in self.results if r.level == DiagnosticLevel.CRITICAL]
        error_tools = [r.test_name for r in self.results if r.level == DiagnosticLevel.ERROR]
        warning_tools = [r.test_name for r in self.results if r.level == DiagnosticLevel.WARNING]

        return {
            "total": len(self.results),
            "ok": counts[DiagnosticLevel.OK],
            "warnings": counts[DiagnosticLevel.WARNING],
            "errors": counts[DiagnosticLevel.ERROR],
            "critical": counts[DiagnosticLevel.CRITICAL],
            "critical_tools": critical_tools,
            "error_tools": error_tools,
            "warning_tools": warning_tools,
            "last_run": self.last_run,
            "timestamp": datetime.fromtimestamp(self.last_run).strftime("%Y-%m-%d %H:%M:%S") if self.last_run else None,
        }

    def print_diagnostic_report(self) -> None:
        """Print formatted diagnostic report."""
        if not self.results:
            self.run_all()

        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("CAMP TUTOR - DIAGNOSTIC REPORT")
        print("=" * 70)
        print(f"Run at: {summary['timestamp']}")
        print(f"\nSummary: {summary['ok']} OK, {summary['warnings']} Warnings, "
              f"{summary['errors']} Errors, {summary['critical']} Critical")
        
        if summary['critical_tools']:
            print(f"\n🚨 CRITICAL FAILURES: {', '.join(summary['critical_tools'])}")
        if summary['error_tools']:
            print(f"\n❌ ERRORS: {', '.join(summary['error_tools'])}")
        if summary['warning_tools']:
            print(f"\n⚠️  WARNINGS: {', '.join(summary['warning_tools'])}")

        print("\n" + "-" * 70)
        print(f"{'Component':<25} {'Status':<12} {'Details'}")
        print("-" * 70)

        for result in self.results:
            icon = {
                DiagnosticLevel.OK: "✓",
                DiagnosticLevel.WARNING: "⚠",
                DiagnosticLevel.ERROR: "❌",
                DiagnosticLevel.CRITICAL: "🚨",
            }.get(result.level, "?")

            details_str = ""
            if result.details:
                if "distance_cm" in result.details:
                    details_str = f"Distance: {result.details['distance_cm']}cm"
                elif "student_count" in result.details:
                    details_str = f"Students: {result.details['student_count']}"
                elif "error" in result.details:
                    details_str = result.details["error"][:30]
                else:
                    details_list = list(result.details.items())[:2]
                    details_str = ", ".join(f"{k}={v}" for k, v in details_list)

            print(f"{icon} {result.test_name:<23} {result.level.value:<12} {details_str}")

        print("\n" + "=" * 70)


_diagnostics_instance: Optional[SystemDiagnostics] = None


def get_diagnostics() -> SystemDiagnostics:
    """Get global diagnostics instance."""
    global _diagnostics_instance
    if _diagnostics_instance is None:
        _diagnostics_instance = SystemDiagnostics()
    return _diagnostics_instance