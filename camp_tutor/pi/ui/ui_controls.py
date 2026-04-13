"""UI controls for Camp Tutor robot."""

import logging
import time
from typing import Optional, Callable, Dict, List, Any

from config import settings

logger = logging.getLogger(__name__)


class SystemStatus:
    """System device status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


class DeviceInfo:
    """Information about a connected device."""
    def __init__(
        self,
        name: str,
        status: str,
        pin: Optional[str] = None,
        details: Optional[str] = None,
        last_check: Optional[float] = None,
    ):
        self.name = name
        self.status = status
        self.pin = pin
        self.details = details
        self.last_check = last_check or time.time()


class SystemMonitor:
    """Monitor and display status of all connected devices."""

    # GPIO Pin mappings for all components
    GPIO_MAP = {
        # I2C Communication
        "I2C_SDA": {"pin": 21, "function": "I2C Data"},
        "I2C_SCL": {"pin": 22, "function": "I2C Clock"},
        
        # Servos (Pan/Tilt)
        "SERVO1": {"pin": 2, "function": "Servo Right/Left"},
        "SERVO2": {"pin": 26, "function": "Servo Up/Down"},
        
        # Ultrasonic Sensor
        "ULTRASONIC_TRIG": {"pin": 17, "function": "HC-SR04 Trigger"},
        "ULTRASONIC_ECHO": {"pin": 16, "function": "HC-SR04 Echo"},
        
        # 4 Omni Motors (controlled by REX via I2C)
        "REX_MOTORS": {"pin": "I2C 0x42", "function": "All motors via REX Arduino"},
        
        # Buzzer
        "BUZZER": {"pin": 25, "function": "Audio feedback"},
        
        # Emergency Stop
        "EMERGENCY_STOP": {"pin": 34, "function": "Emergency stop button"},
        
        # LCD Display (Nokia 5110 - SPI)
        "LCD_RST": {"pin": 4, "function": "LCD Reset"},
        "LCD_DC": {"pin": 0, "function": "LCD Data/Command"},
        "LCD_MOSI": {"pin": 23, "function": "LCD SPI MOSI"},
        "LCD_CLK": {"pin": 18, "function": "LCD SPI Clock"},
        "LCD_CS": {"pin": 5, "function": "LCD Chip Select"},
    }

    def __init__(self):
        self.devices: Dict[str, DeviceInfo] = {}
        self._rex_client = None
        self._rex_status = SystemStatus.UNKNOWN

    def check_all_devices(self) -> Dict[str, DeviceInfo]:
        """Check status of all connected devices."""
        self.devices = {}
        
        # Check REX (I2C)
        self._check_rex()
        
        # Check LCD
        self._check_lcd()
        
        # Check Audio
        self._check_audio()
        
        # Check Camera
        self._check_camera()
        
        # Check Database
        self._check_database()
        
        return self.devices

    def _check_rex(self) -> None:
        """Check REX controller status via I2C."""
        try:
            from control import rex_client
            if self._rex_client is None:
                self._rex_client = rex_client.get_rex_client()
            
            if self._rex_client.is_connected():
                if self._rex_client.ping():
                    status = self._rex_client.get_status()
                    self.devices["REX"] = DeviceInfo(
                        name="REX Controller",
                        status=SystemStatus.CONNECTED,
                        pin="I2C 0x42",
                        details=status.get("status", "OK"),
                    )
                    self._rex_status = SystemStatus.CONNECTED
                else:
                    self.devices["REX"] = DeviceInfo(
                        name="REX Controller",
                        status=SystemStatus.DISCONNECTED,
                        pin="I2C 0x42",
                        details="Not responding to ping",
                    )
                    self._rex_status = SystemStatus.DISCONNECTED
            else:
                self.devices["REX"] = DeviceInfo(
                    name="REX Controller",
                    status=SystemStatus.DISCONNECTED,
                    pin="I2C 0x42",
                    details="Not connected",
                )
                self._rex_status = SystemStatus.DISCONNECTED
        except Exception as e:
            self.devices["REX"] = DeviceInfo(
                name="REX Controller",
                status=SystemStatus.ERROR,
                pin="I2C 0x42",
                details=str(e),
            )
            self._rex_status = SystemStatus.ERROR

    def _check_lcd(self) -> None:
        """Check LCD display status."""
        try:
            from display import lcd5110
            lcd = lcd5110.get_lcd()
            if lcd and hasattr(lcd, 'disp'):
                self.devices["LCD"] = DeviceInfo(
                    name="Nokia LCD 5110",
                    status=SystemStatus.CONNECTED,
                    pin="SPI (GPIO 4,0,23,18,5)",
                    details="Display ready",
                )
            else:
                self.devices["LCD"] = DeviceInfo(
                    name="Nokia LCD 5110",
                    status=SystemStatus.DISCONNECTED,
                    pin="SPI (GPIO 4,0,23,18,5)",
                    details="No display",
                )
        except Exception as e:
            self.devices["LCD"] = DeviceInfo(
                name="Nokia LCD 5110",
                status=SystemStatus.ERROR,
                pin="SPI (GPIO 4,0,23,18,5)",
                details=str(e),
            )

    def _check_audio(self) -> None:
        """Check audio devices status."""
        try:
            from audio import audio_device
            audio = audio_device.get_audio_device()
            
            bt_connected = False
            bt_device_name = None
            try:
                from bluetooth import bluetooth_manager
                bt = bluetooth_manager.get_bluetooth_manager()
                if bt.connected_device:
                    bt_connected = True
                    bt_device_name = bt.connected_device.name
            except Exception:
                pass
            
            if audio:
                self.devices["AUDIO_IN"] = DeviceInfo(
                    name="USB Microphone",
                    status=SystemStatus.CONNECTED,
                    pin="USB Adapter",
                    details="USB audio input ready",
                )
            else:
                self.devices["AUDIO_IN"] = DeviceInfo(
                    name="USB Microphone",
                    status=SystemStatus.DISCONNECTED,
                    pin="USB Adapter",
                    details="No audio device detected",
                )
            
            if bt_connected:
                self.devices["AUDIO_OUT"] = DeviceInfo(
                    name="Bluetooth Speaker",
                    status=SystemStatus.CONNECTED,
                    pin="Pi Bluetooth",
                    details=f"Connected to {bt_device_name}",
                )
            else:
                self.devices["AUDIO_OUT"] = DeviceInfo(
                    name="Bluetooth Speaker",
                    status=SystemStatus.DISCONNECTED,
                    pin="Pi Bluetooth",
                    details="No Bluetooth device connected",
                )
                
        except Exception as e:
            self.devices["AUDIO_IN"] = DeviceInfo(
                name="USB Microphone",
                status=SystemStatus.ERROR,
                pin="USB Adapter",
                details=str(e),
            )

    def _check_camera(self) -> None:
        """Check camera status."""
        try:
            from vision import camera
            cam = camera.get_camera()
            if cam and cam.is_ready():
                self.devices["CAMERA"] = DeviceInfo(
                    name="Pi Camera v2",
                    status=SystemStatus.CONNECTED,
                    pin="CSI Interface",
                    details="Camera ready",
                )
            else:
                self.devices["CAMERA"] = DeviceInfo(
                    name="Pi Camera v2",
                    status=SystemStatus.DISCONNECTED,
                    pin="CSI Interface",
                    details="Not initialized",
                )
        except Exception as e:
            self.devices["CAMERA"] = DeviceInfo(
                name="Pi Camera v2",
                status=SystemStatus.ERROR,
                pin="CSI Interface",
                details=str(e),
            )

    def _check_database(self) -> None:
        """Check database status."""
        try:
            from storage import student_db
            db = student_db.get_student_db()
            if db:
                self.devices["DATABASE"] = DeviceInfo(
                    name="Student Database",
                    status=SystemStatus.CONNECTED,
                    pin="SD Card",
                    details="Database ready",
                )
            else:
                self.devices["DATABASE"] = DeviceInfo(
                    name="Student Database",
                    status=SystemStatus.DISCONNECTED,
                    pin="SD Card",
                    details="No database",
                )
        except Exception as e:
            self.devices["DATABASE"] = DeviceInfo(
                name="Student Database",
                status=SystemStatus.ERROR,
                pin="SD Card",
                details=str(e),
            )

    def get_rex_distance(self) -> Optional[int]:
        """Get distance from REX ultrasonic sensor."""
        if self._rex_client and self._rex_status == SystemStatus.CONNECTED:
            try:
                return self._rex_client.get_distance()
            except Exception:
                return None
        return None

    def test_rex_movement(self, direction: str = "FWD") -> bool:
        """Test REX movement in a direction."""
        if self._rex_client and self._rex_status == SystemStatus.CONNECTED:
            try:
                return self._rex_client.move(direction)
            except Exception:
                return False
        return False

    def get_status_summary(self) -> dict:
        """Get summary of all device statuses."""
        summary = {
            "total": len(self.devices),
            "connected": 0,
            "disconnected": 0,
            "error": 0,
            "devices": [],
        }
        
        for device in self.devices.values():
            if device.status == SystemStatus.CONNECTED:
                summary["connected"] += 1
            elif device.status == SystemStatus.DISCONNECTED:
                summary["disconnected"] += 1
            elif device.status == SystemStatus.ERROR:
                summary["error"] += 1
            
            summary["devices"].append({
                "name": device.name,
                "status": device.status,
                "pin": device.pin,
                "details": device.details,
            })
        
        return summary

    def print_status_report(self) -> None:
        """Print formatted status report to console."""
        print("\n" + "=" * 60)
        print("CAMP TUTOR - SYSTEM STATUS REPORT")
        print("=" * 60)
        
        summary = self.get_status_summary()
        print(f"\nDevices: {summary['connected']} connected, "
              f"{summary['disconnected']} disconnected, "
              f"{summary['error']} errors\n")
        
        print("-" * 60)
        print(f"{'Device':<25} {'Status':<15} {'Pin':<20}")
        print("-" * 60)
        
        for device in summary["devices"]:
            status_symbol = {
                SystemStatus.CONNECTED: "✓",
                SystemStatus.DISCONNECTED: "✗",
                SystemStatus.ERROR: "⚠",
                SystemStatus.UNKNOWN: "?",
            }.get(device["status"], "?")
            
            print(f"{status_symbol} {device['name']:<23} "
                  f"{device['status']:<15} {device['pin']:<20}")
        
        # Print GPIO mapping
        print("\n" + "=" * 60)
        print("GPIO PIN MAPPING (Nokia 5110 LCD Connection)")
        print("=" * 60)
        print("\nSPI Connection Diagram:")
        print("┌─────────────────┐    ┌─────────────────┐")
        print("│   Raspberry Pi  │    │   Nokia 5110   │")
        print("├─────────────────┤    ├─────────────────┤")
        print("│ GPIO 4  (RST)   │───►│ RST            │")
        print("│ GPIO 0  (DC)    │───►│ DC             │")
        print("│ GPIO 23 (MOSI)  │───►│ MOSI           │")
        print("│ GPIO 18 (CLK)   │───►│ CLK            │")
        print("│ GPIO 5  (CS)    │───►│ CS             │")
        print("│ 3.3V            │───►│ VCC            │")
        print("│ GND             │───►│ GND            │")
        print("└─────────────────┘    └─────────────────┘")
        
        print("\nDetailed Pinout:")
        print("-" * 60)
        for name, info in self.GPIO_MAP.items():
            print(f"  {name:<20} -> GPIO {info['pin']:<2} ({info['function']})")
        
        print("\n" + "=" * 60)

    def get_gpio_table(self) -> List[Dict[str, Any]]:
        """Get GPIO mapping as list of dictionaries."""
        return [
            {
                "name": name,
                "gpio": info["pin"],
                "function": info["function"],
            }
            for name, info in self.GPIO_MAP.items()
        ]


class VolumeControl:
    """Volume control with UI slider support."""

    def __init__(
        self,
        initial_volume: float = settings.DEFAULT_VOLUME,
        initial_rate: int = settings.DEFAULT_SPEECH_RATE,
    ):
        self._volume = initial_volume
        self._rate = initial_rate
        self._muted = False
        self._on_change_callback: Optional[Callable[[float], None]] = None
        self._sync_with_system_volume()

    @property
    def volume(self) -> float:
        """Get current volume (0.0 to 1.0)."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        """Set volume (0.0 to 1.0). Clamped to valid range."""
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._volume = value
        logger.info(f"Volume set to {int(self._volume * 100)}%")
        if self._on_change_callback:
            self._on_change_callback(self._volume)

    @property
    def volume_percent(self) -> int:
        """Get volume as percentage (0-100)."""
        return int(self._volume * 100)

    def set_volume_percent(self, percent: int) -> None:
        """Set volume by percentage (0-100)."""
        self.volume = percent / 100.0
        self._apply_system_volume(percent)

    def _apply_system_volume(self, percent: int) -> None:
        """Apply volume to system mixer."""
        import subprocess
        try:
            subprocess.run(
                ["amixer", "-q", "-M", "sset", "Master", f"{percent}%"],
                capture_output=True, timeout=2
            )
            logger.info(f"System volume set to {percent}%")
        except Exception as e:
            logger.warning(f"Could not set system volume: {e}")

    def _sync_with_system_volume(self) -> None:
        """Sync with system volume on startup."""
        import subprocess
        try:
            result = subprocess.run(
                ["amixer", "get", "Master"],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split("\n"):
                if "[" in line and "%]" in line:
                    start = line.find("[") + 1
                    end = line.find("%]")
                    vol = int(line[start:end])
                    self._volume = vol / 100.0
                    logger.info(f"Synced with system volume: {vol}%")
                    break
        except Exception as e:
            logger.warning(f"Could not sync system volume: {e}")

    @property
    def rate(self) -> int:
        """Get speech rate (words per minute)."""
        return self._rate

    @rate.setter
    def rate(self, value: int) -> None:
        """Set speech rate. Clamped to 100-300."""
        if value < 100:
            value = 100
        elif value > 300:
            value = 300
        self._rate = value
        logger.info(f"Speech rate set to {self._rate} wpm")

    @property
    def is_muted(self) -> bool:
        """Check if muted."""
        return self._muted

    def mute(self) -> None:
        """Mute audio output."""
        self._muted = True
        logger.info("Audio muted")

    def unmute(self) -> None:
        """Unmute audio output."""
        self._muted = False
        logger.info("Audio unmuted")

    def toggle_mute(self) -> None:
        """Toggle mute state."""
        self._muted = not self._muted
        logger.info(f"Audio {'muted' if self._muted else 'unmuted'}")

    def get_effective_volume(self) -> float:
        """Get effective volume (considering mute)."""
        return 0.0 if self._muted else self._volume

    def on_change(self, callback: Callable[[float], None]) -> None:
        """Register callback for volume changes."""
        self._on_change_callback = callback

    def get_info(self) -> dict:
        """Get current settings as dict."""
        return {
            "volume": self._volume,
            "volume_percent": self.volume_percent,
            "rate": self._rate,
            "muted": self._muted,
        }


class AgeGroupSelector:
    """Age group selection and class management UI."""

    def __init__(self, class_manager=None):
        self.class_manager = class_manager
        self._current_index = 1

    @property
    def current_age_group(self) -> str:
        """Get current age group key."""
        return settings.AGE_GROUP_KEYS[self._current_index]

    @property
    def current_age_group_display(self) -> str:
        """Get current age group display name."""
        return settings.AGE_GROUP_DISPLAY[self.current_age_group]

    def select_age_group(self, index: int) -> bool:
        """Select age group by index (0-3)."""
        if 0 <= index < len(settings.AGE_GROUP_KEYS):
            self._current_index = index
            if self.class_manager:
                self.class_manager.set_age_group(self.current_age_group)
            logger.info(f"Selected age group: {self.current_age_group}")
            return True
        return False

    def select_age_group_by_key(self, key: str) -> bool:
        """Select age group by key (e.g., 'primary')."""
        if key in settings.AGE_GROUP_KEYS:
            self._current_index = settings.AGE_GROUP_KEYS.index(key)
            if self.class_manager:
                self.class_manager.set_age_group(key)
            return True
        return False

    def next_age_group(self) -> str:
        """Move to next age group."""
        self._current_index = (self._current_index + 1) % len(settings.AGE_GROUP_KEYS)
        if self.class_manager:
            self.class_manager.set_age_group(self.current_age_group)
        return self.current_age_group_display

    def previous_age_group(self) -> str:
        """Move to previous age group."""
        self._current_index = (self._current_index - 1) % len(settings.AGE_GROUP_KEYS)
        if self.class_manager:
            self.class_manager.set_age_group(self.current_age_group)
        return self.current_age_group_display

    def get_age_groups(self) -> list[dict]:
        """Get list of all age groups."""
        return [
            {"key": key, "display": settings.AGE_GROUP_DISPLAY[key], "index": i}
            for i, key in enumerate(settings.AGE_GROUP_KEYS)
        ]

    def get_info(self) -> dict:
        """Get current selection info."""
        return {
            "current_age_group": self.current_age_group,
            "current_age_group_display": self.current_age_group_display,
            "available_age_groups": self.get_age_groups(),
        }


class TimetableDisplay:
    """Display and manage timetable."""

    def __init__(self, class_manager=None):
        self.class_manager = class_manager

    def get_timetable(self, age_group: Optional[str] = None) -> list[dict]:
        """Get timetable entries."""
        if not self.class_manager:
            return []
        entries = self.class_manager.get_timetable(age_group)
        return [
            {
                "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][e.day_of_week],
                "time": e.start_time,
                "subject": e.subject,
                "topic": e.topic,
                "duration": e.duration_minutes,
                "completed": e.completed,
            }
            for e in entries
        ]

    def get_next_lesson(self) -> Optional[dict]:
        """Get next lesson to teach."""
        if not self.class_manager:
            return None
        lesson = self.class_manager.get_next_lesson()
        if not lesson:
            return None
        return {
            "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][lesson.day_of_week],
            "time": lesson.start_time,
            "subject": lesson.subject,
            "topic": lesson.topic,
            "duration": lesson.duration_minutes,
        }

    def get_ai_recommendation(self) -> dict:
        """Get AI recommendation."""
        if not self.class_manager:
            return {}
        return self.class_manager.get_ai_recommendation()

    def get_progress_summary(self) -> dict:
        """Get progress for all age groups."""
        if not self.class_manager:
            return {}
        return self.class_manager.get_progress_summary()


class SimpleConsoleUI:
    """Simple console-based UI for testing."""

    def __init__(self):
        self.volume_control = VolumeControl()
        from storage.class_manager import get_class_manager
        self.class_manager = get_class_manager()
        self.age_selector = AgeGroupSelector(self.class_manager)
        self.timetable_display = TimetableDisplay(self.class_manager)
        self._running = False

    def show_menu(self) -> None:
        """Display main menu."""
        print("\n" + "=" * 50)
        print("CAMP TUTOR CONTROL PANEL")
        print("=" * 50)
        print(f"Current Age Group: {self.age_selector.current_age_group_display}")
        print(f"Class in Progress: {self.class_manager.is_class_in_progress()}")
        print(f"Volume: {self.volume_control.volume_percent}%")
        print("-" * 50)
        print("[V] Volume Control")
        print("[A] Age Group Selection")
        print("[T] Timetable & Progress")
        print("[C] Start/End Class")
        print("[R] AI Recommendation")
        print("[I] AI Control Panel")
        print("[M] Toggle AI Auto Mode")
        print("[Q] Quit")
        print("=" * 50)

    def show_age_group_menu(self) -> None:
        """Show age group selection."""
        print("\n--- AGE GROUP SELECTION ---")
        for ag in self.age_selector.get_age_groups():
            marker = " *" if ag["index"] == self.age_selector._current_index else " "
            print(f"[{ag['index']}]{marker} {ag['display']}")
        print("[N] Next | [P] Previous | [B] Back")

    def show_timetable(self) -> None:
        """Show timetable."""
        print("\n--- TIMETABLE ---")
        timetable = self.timetable_display.get_timetable()
        for i, entry in enumerate(timetable):
            status = "✓" if entry["completed"] else "○"
            print(f"{status} {entry['day']} {entry['time']} - {entry['subject']}: {entry['topic']}")

    def show_progress(self) -> None:
        """Show progress summary."""
        print("\n--- PROGRESS SUMMARY ---")
        summary = self.timetable_display.get_progress_summary()
        for age_group, info in summary.items():
            print(f"\n{info['display_name']}:")
            print(f"  Completed: {info['completed_lessons']} lessons")
            print(f"  Progress: {info['progress_percent']}%")
            print(f"  Subjects: {', '.join(info['subjects'])}")

    def show_ai_recommendation(self) -> None:
        """Show AI recommendation."""
        print("\n--- AI RECOMMENDATION ---")
        rec = self.timetable_display.get_ai_recommendation()
        print(f"Subject: {rec.get('subject', 'N/A')}")
        print(f"Topic: {rec.get('topic', 'N/A')}")
        print(f"Reason: {rec.get('reason', 'N/A')}")
        print(f"Progress: {rec.get('progress', 'N/A')}")
        if rec.get("suggested_focus"):
            print(f"Suggested Focus: {rec['suggested_focus']}")

    def show_ai_control(self) -> None:
        """Show AI control panel."""
        from ai.ai_controller import get_ai_controller, get_user_control_panel
        panel = get_user_control_panel()
        panel.show_ai_status()
        decisions = panel.show_pending_decisions()
        if not decisions:
            print("No pending decisions")

    def enable_auto_mode(self) -> None:
        """Enable AI auto mode."""
        from ai.ai_controller import get_ai_controller
        get_ai_controller().set_auto_mode(True)
        print("AI Auto Mode: ON")

    def disable_auto_mode(self) -> None:
        """Disable AI auto mode."""
        from ai.ai_controller import get_ai_controller
        get_ai_controller().set_auto_mode(False)
        print("AI Auto Mode: OFF - User controls enabled")

    def run(self) -> None:
        """Run console UI loop."""
        self._running = True
        print("Camp Tutor Console UI")
        print("Type 'help' for commands")

        while self._running:
            self.show_menu()
            try:
                cmd = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break

            if cmd == "help":
                print("Commands: v, a, t, c, r, i, m, q")
            elif cmd == "v":
                vol = input("Volume (0-100): ")
                if vol.isdigit():
                    self.volume_control.set_volume_percent(int(vol))
            elif cmd == "a":
                self.show_age_group_menu()
                sub = input("Selection: ").strip().lower()
                if sub.isdigit() and 0 <= int(sub) <= 3:
                    self.age_selector.select_age_group(int(sub))
                elif sub == "n":
                    self.age_selector.next_age_group()
                elif sub == "p":
                    self.age_selector.previous_age_group()
            elif cmd == "t":
                self.show_timetable()
                self.show_progress()
                input("\nPress Enter to continue...")
            elif cmd == "c":
                if self.class_manager.is_class_in_progress():
                    self.class_manager.end_class()
                    print("Class ended")
                else:
                    self.class_manager.start_class()
                    print("Class started")
            elif cmd == "r":
                self.show_ai_recommendation()
                input("\nPress Enter to continue...")
            elif cmd == "i":
                self.show_ai_control()
                input("\nPress Enter to continue...")
            elif cmd == "m":
                from ai.ai_controller import get_ai_controller
                ai = get_ai_controller()
                if ai.is_auto_mode():
                    self.disable_auto_mode()
                else:
                    self.enable_auto_mode()
            elif cmd in ("quit", "q"):
                self._running = False
            else:
                print("Unknown command")

        print("Console UI closed")


_volume_control_instance: Optional[VolumeControl] = None
_age_selector_instance: Optional[AgeGroupSelector] = None
_timetable_display_instance: Optional[TimetableDisplay] = None


def get_volume_control() -> VolumeControl:
    """Get global volume control instance."""
    global _volume_control_instance
    if _volume_control_instance is None:
        _volume_control_instance = VolumeControl()
    return _volume_control_instance


def get_age_selector(class_manager=None) -> AgeGroupSelector:
    """Get global age group selector instance."""
    global _age_selector_instance
    if _age_selector_instance is None:
        _age_selector_instance = AgeGroupSelector(class_manager)
    return _age_selector_instance


def get_timetable_display(class_manager=None) -> TimetableDisplay:
    """Get global timetable display instance."""
    global _timetable_display_instance
    if _timetable_display_instance is None:
        _timetable_display_instance = TimetableDisplay(class_manager)
    return _timetable_display_instance


def get_console_ui() -> SimpleConsoleUI:
    """Get console UI instance."""
    return SimpleConsoleUI()


def get_system_monitor() -> SystemMonitor:
    """Get system monitor instance."""
    return SystemMonitor()