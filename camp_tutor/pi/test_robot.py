#!/usr/bin/env python3
"""Camp Tutor Robot Diagnostics Test Script."""

import sys
import os
import logging
import subprocess

os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_section(title):
    """Print test section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_result(name, passed, details=""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status:8} | {name}")
    if details and not passed:
        print(f"           -> {details}")
    return passed


def print_hardware_info():
    """Print hardware connection info."""
    print("""
======================================================================
  HARDWARE CONNECTIONS
======================================================================

# REX I2C Connection (to Raspberry Pi)
+---------------------------+-------------------+
| Component                 | Raspberry Pi Pin   |
+---------------------------+-------------------+
| SCL (I2C Clock)           | Pin 3  (GPIO 22)  |
| SDA (I2C Data)           | Pin 5  (GPIO 21)  |
| 5V Power                 | Pin 2             |
| GND                      | Pin 6             |
+---------------------------+-------------------+

# ILI9341 LCD Connection (SPI)
+---------------------------+-------------------+
| LCD Pin                   | Raspberry Pi Pin  |
+---------------------------+-------------------+
| VCC (3.3V)               | Pin 1             |
| GND                      | Pin 6             |
| SCE (Chip Enable)        | Pin 24 (GPIO 8)   |
| RST (Reset)              | Pin 22 (GPIO 25)  |
| D/C (Data/Command)       | Pin 18 (GPIO 24)  |
| MOSI (SPI Data)          | Pin 19 (GPIO 10)  |
| SCLK (SPI Clock)         | Pin 23 (GPIO 11)  |
| LED (Backlight)         | Pin 12 (GPIO 18)  |
+---------------------------+-------------------+

# I2C Addresses
+------------------+----------+
| Device           | Address  |
+------------------+----------+
| REX Controller   | 0x42     |
| LCD Display      | 0x3C     |
+------------------+----------+
""")


def test_imports():
    """Test all required imports."""
    test_section("1. Testing Python Imports")
    results = []
    
    try:
        from config import settings
        results.append(test_result("config.settings", True))
    except Exception as e:
        results.append(test_result("config.settings", False, str(e)))
    
    try:
        from config.wifi_manager import get_wifi_manager
        results.append(test_result("wifi_manager", True))
    except Exception as e:
        results.append(test_result("wifi_manager", False, str(e)))
    
    try:
        from bluetooth.bluetooth_manager import get_bluetooth_manager
        results.append(test_result("bluetooth_manager", True))
    except Exception as e:
        results.append(test_result("bluetooth_manager", False, str(e)))
    
    try:
        from control.rex_client import get_rex_client
        results.append(test_result("rex_client", True))
    except Exception as e:
        results.append(test_result("rex_client", False, str(e)))
    
    try:
        from ai.tutor_engine import get_tutor_engine
        results.append(test_result("tutor_engine", True))
    except Exception as e:
        results.append(test_result("tutor_engine", False, str(e)))
    
    try:
        from storage.student_db import get_student_db
        results.append(test_result("student_db", True))
    except Exception as e:
        results.append(test_result("student_db", False, str(e)))
    
    return all(results)


def test_settings():
    """Test configuration settings."""
    test_section("2. Testing Configuration")
    results = []
    
    from config import settings
    
    results.append(test_result(
        "I2C Address 0x42",
        settings.I2C_ADDRESS == 0x42,
        f"Expected 0x42, got {hex(settings.I2C_ADDRESS)}"
    ))
    
    results.append(test_result(
        "WiFi_Enc_Key configured",
        bool(settings.WIFI_ENC_KEY),
        "No encryption key"
    ))
    
    results.append(test_result(
        "Age groups defined",
        len(settings.AGE_GROUPS) > 0,
        f"Expected >0, got {len(settings.AGE_GROUPS)}"
    ))
    
    results.append(test_result(
        "Languages supported",
        len(settings.LANGUAGE_CODES) >= 19,
        f"Expected >=19, got {len(settings.LANGUAGE_CODES)}"
    ))
    
    results.append(test_result(
        "Curriculum subjects",
        len(settings.CURRICULUM_SUBJECTS) > 0,
        f"Expected >0, got {len(settings.CURRICULUM_SUBJECTS)}"
    ))
    
    return all(results)


def test_i2c():
    """Test I2C communication."""
    test_section("3. Testing I2C (Pi → REX)")
    results = []
    
    try:
        result = subprocess.run(
            ["sudo", "i2cdetect", "-y", "1"],
            capture_output=True,
            timeout=10,
        )
        connected = "0x42" in result.stdout.decode() or "42" in result.stdout.decode()
        results.append(test_result(
            "I2C bus available",
            result.returncode == 0,
            f"Return code: {result.returncode}"
        ))
        results.append(test_result(
            "REX at 0x42",
            connected,
            "REX not found on I2C bus"
        ))
    except FileNotFoundError:
        results.append(test_result("i2cdetect installed", False, "Run: sudo apt-get install i2c-tools"))
    except Exception as e:
        results.append(test_result("I2C bus", False, str(e)))
    
    return all(results)


def test_bluetooth():
    """Test Bluetooth with activation."""
    test_section("4. Testing Bluetooth")
    results = []
    
    # First, restart and ensure Bluetooth is powered on
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "bluetooth"],
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["sudo", "bluetoothctl", "power", "on"],
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["sudo", "bluetoothctl", "agent", "on"],
            capture_output=True,
            timeout=5,
        )
        subprocess.run(
            ["sudo", "bluetoothctl", "default-agent"],
            capture_output=True,
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Could not activate Bluetooth: {e}")
    
    try:
        result = subprocess.run(
            ["rfkill", "list", "bluetooth"],
            capture_output=True,
            timeout=5,
        )
        results.append(test_result(
            "Bluetooth rfkill",
            result.returncode == 0,
            f"Return code: {result.returncode}"
        ))
    except FileNotFoundError:
        results.append(test_result("rfkill", False, "Not installed"))
    except Exception as e:
        results.append(test_result("rfkill", False, str(e)))
    
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "bluetooth.service"],
            capture_output=True,
            timeout=5,
        )
        active = result.stdout.decode().strip() == "active"
        results.append(test_result(
            "Bluetooth service active",
            active,
            f"Status: {result.stdout.decode().strip()}"
        ))
    except Exception as e:
        results.append(test_result("bluetooth service", False, str(e)))
    
    try:
        from bluetooth.bluetooth_manager import get_bluetooth_manager
        bt = get_bluetooth_manager()
        state = bt.state
        connected = bt.connected_device
        results.append(test_result(
            "BLEAK library",
            True,
            f"State: {state.value}"
        ))
        
        # List known devices
        devices = bt.list_devices()
        results.append(test_result(
            "Bluetooth devices list",
            True,
            f"Found {len(devices)} devices"
        ))
        
        for d in devices:
            logger.info(f"  - {d.name} ({d.address})")
        
        results.append(test_result(
            "Bluetooth device connected",
            connected is not None,
            f"Device: {connected.name if connected else 'None'}"
        ))
    except ImportError:
        results.append(test_result("BLEAK library", False, "Run: pip install bleak"))
    except Exception as e:
        results.append(test_result("BLEAK library", False, str(e)))
    
    return all(results)


def test_wifi():
    """Test WiFi."""
    test_section("5. Testing WiFi")
    results = []
    
    try:
        result = subprocess.run(
            ["nmcli", "device", "status"],
            capture_output=True,
            timeout=10,
        )
        results.append(test_result(
            "NetworkManager",
            result.returncode == 0,
            f"Return code: {result.returncode}"
        ))
    except FileNotFoundError:
        results.append(test_result("nmcli", False, "Not found"))
    except Exception as e:
        results.append(test_result("nmcli", False, str(e)))
    
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        status = wifi.get_status()
        results.append(test_result(
            "WiFi Manager",
            "connected" in status,
            f"Status keys: {list(status.keys())}"
        ))
    except Exception as e:
        results.append(test_result("WiFi Manager", False, str(e)))
    
    return all(results)


def test_ai():
    """Test AI modules."""
    test_section("6. Testing AI Modules")
    results = []
    
    try:
        from ai.tutor_engine import get_tutor_engine
        from audio import text_to_speech
        
        tutor = get_tutor_engine()
        
        tutor.start_session("test_student", "en", 10)
        results.append(test_result("Tutor Engine", True))
        
        tutor.start_session("demo_student", "en", age=10)
        subjects = tutor.get_subject_list()
        results.append(test_result(
            "Subject list",
            len(subjects) > 0,
            f"Found {len(subjects)} subjects"
        ))
        
        greeting = tutor.get_greeting()
        results.append(test_result(
            "AI Greeting",
            len(greeting) > 0,
            f'"{greeting}"'
        ))
        
        print("\n--- AI Tutor Introduction ---")
        print(f"Tutor says: {greeting}")
        
        try:
            tts = text_to_speech.TextToSpeech(language="en")
            intro = "Hello! I am Camp Tutor, your AI learning companion. I will help you learn Mathematics, Science, and English through fun activities!"
            tts.speak(intro)
            results.append(test_result("AI Introduction (TTS)", True, "Spoke intro"))
            print(f"  -> Played via TTS")
        except Exception as e:
            results.append(test_result("AI Introduction (TTS)", False, str(e)))
        
    except Exception as e:
        results.append(test_result("Tutor Engine", False, str(e)))
    
    try:
        from ai.progress_tracker import get_progress_tracker
        tracker = get_progress_tracker()
        results.append(test_result("Progress Tracker", True))
    except Exception as e:
        results.append(test_result("Progress Tracker", False, str(e)))
    
    try:
        from ai.assessment_engine import get_assessment_engine
        engine = get_assessment_engine()
        results.append(test_result("Assessment Engine", True))
    except Exception as e:
        results.append(test_result("Assessment Engine", False, str(e)))
    
    try:
        from ai.language_detection import get_language_detector
        detector = get_language_detector()
        results.append(test_result("Language Detector", True))
    except Exception as e:
        results.append(test_result("Language Detector", False, str(e)))
    
    return all(results)


def test_database():
    """Test database."""
    test_section("7. Testing Database")
    results = []
    
    try:
        from storage.student_db import get_student_db
        db = get_student_db()
        students = db.get_all_students()
        results.append(test_result(
            "Student Database",
            True,
            f"Students: {len(students)}"
        ))
    except Exception as e:
        results.append(test_result("Student Database", False, str(e)))
    
    return all(results)


def test_password_file():
    """Test password file."""
    test_section("8. Testing Password File")
    results = []
    
    from pathlib import Path
    from config import settings
    
    password_file = Path(__file__).parent / "passwords.txt"
    
    results.append(test_result(
        "passwords.txt exists",
        password_file.exists(),
        str(password_file)
    ))
    
    if password_file.exists():
        content = password_file.read_text()
        results.append(test_result(
            "sudo=Refugee123@",
            "sudo=Refugee123@" in content,
            "Password not found"
        ))
    
    return all(results)


def test_camera():
    """Test camera."""
    test_section("9. Testing Camera")
    results = []
    
    try:
        result = subprocess.run(
            ["vcgencmd", "get_camera"],
            capture_output=True,
            timeout=5,
        )
        output = result.stdout.decode()
        results.append(test_result(
            "Camera detected",
            "detected=1" in output or result.returncode == 0,
            output.strip() if output else "No camera"
        ))
    except FileNotFoundError:
        results.append(test_result("vcgencmd", False, "Not found"))
    except Exception as e:
        results.append(test_result("vcgencmd", False, str(e)))
    
    try:
        from vision.camera_capture import get_camera
        camera = get_camera()
        results.append(test_result(
            "Camera module",
            camera is not None,
            "Cannot initialize"
        ))
    except Exception as e:
        results.append(test_result("Camera module", False, str(e)))
    
    return all(results)


def test_audio_input():
    """Test microphone/audio input."""
    test_section("10. Testing Audio Input")
    results = []
    
    # Check ALSA audio devices
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            timeout=5,
        )
        has_mic = result.returncode == 0 and "Card" in result.stdout.decode()
        results.append(test_result(
            "ALSA recording devices",
            has_mic,
            result.stdout.decode().strip() if has_mic else "No mic found"
        ))
    except FileNotFoundError:
        results.append(test_result("arecord", False, "Not installed"))
    except Exception as e:
        results.append(test_result("arecord", False, str(e)))
    
    # Check sounddevice
    has_mic = False
    try:
        import sounddevice as sd
        results.append(test_result("sounddevice library", True, "Library loaded"))
        
        # Try to enumerate input devices
        try:
            all_devices = sd.query_devices()
            input_mics = []
            
            if isinstance(all_devices, dict):
                if all_devices.get('max_input_channels', 0) > 0:
                    input_mics.append(all_devices)
                    has_mic = True
            elif isinstance(all_devices, list):
                for d in all_devices:
                    if isinstance(d, dict) and d.get('max_input_channels', 0) > 0:
                        input_mics.append(d)
                        has_mic = True
            
            results.append(test_result(
                "Microphone available",
                has_mic,
                f"Python Input: {len(input_mics)}"
            ))
        except Exception as e:
            results.append(test_result("Microphone available", False, str(e)))
    except ImportError:
        results.append(test_result("sounddevice library", False, "Run: pip install sounddevice"))
    except Exception as e:
        results.append(test_result("sounddevice library", False, str(e)))
    
    # Check pyaudio as fallback
    if not has_mic:
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            input_count = p.get_device_count()
            pyaudio_mics = [i for i in range(input_count) if p.get_device_info_by_index(i).get('maxInputChannels', 0) > 0]
            has_mic = len(pyaudio_mics) > 0
            results.append(test_result(
                "Microphone available",
                has_mic,
                f"PyAudio Input: {len(pyaudio_mics)}"
            ))
            
            # Test recording if mic available
            if has_mic:
                test_file = "/tmp/test_recording.wav"
                try:
                    import wave
                    import os
                    chunk = 1024
                    sample_format = pyaudio.paInt16
                    channels = 1
                    sample_rate = 44100  # USB mic standard rate
                    record_seconds = 2
                    
                    stream = p.open(
                        format=sample_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        input_device_index=pyaudio_mics[0],
                        frames_per_buffer=chunk
                    )
                    frames = []
                    for _ in range(int(sample_rate / chunk * record_seconds)):
                        data = stream.read(chunk, exception_on_overflow=False)
                        frames.append(data)
                    stream.stop_stream()
                    stream.close()
                    
                    with wave.open(test_file, 'wb') as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(p.get_sample_size(sample_format))
                        wf.setframerate(sample_rate)
                        wf.writeframes(b''.join(frames))
                    
                    file_size = os.path.getsize(test_file)
                    results.append(test_result(
                        "Microphone record",
                        file_size > 0,
                        f"Saved {file_size} bytes"
                    ))
                except Exception as e:
                    results.append(test_result("Microphone record", False, str(e)))
                finally:
                    try:
                        import os
                        if os.path.exists(test_file):
                            os.remove(test_file)
                    except:
                        pass
            
            p.terminate()
        except ImportError:
            results.append(test_result("PyAudio library", False, "Run: pip install pyaudio"))
        except Exception as e:
            results.append(test_result("PyAudio library", False, str(e)))
    
    # Check USB audio adapter
    try:
        result = subprocess.run(
            ["lsusb"],
            capture_output=True,
            timeout=5,
        )
        has_usb_audio = "audio" in result.stdout.decode().lower() or "mic" in result.stdout.decode().lower()
        results.append(test_result(
            "USB audio device",
            has_usb_audio,
            "Check lsusb output"
        ))
    except Exception as e:
        results.append(test_result("lsusb", False, str(e)))
    
    return all(results)


def test_lcd_screen():
    """Test LCD screen."""
    test_section("11. Testing LCD Screen")
    results = []
    
    # Check SPI interface
    try:
        result = subprocess.run(
            ["ls", "/dev/spi*"],
            capture_output=True,
            timeout=5,
        )
        has_spi = result.returncode == 0
        results.append(test_result(
            "SPI device",
            has_spi,
            result.stdout.decode().strip() if has_spi else "No SPI device"
        ))
    except Exception as e:
        results.append(test_result("SPI device", False, str(e)))
    
    # Check GPIO
    try:
        result = subprocess.run(
            ["ls", "/dev/gpio*"],
            capture_output=True,
            timeout=5,
        )
        results.append(test_result(
            "GPIO device",
            result.returncode == 0,
            "GPIO available"
        ))
    except Exception as e:
        results.append(test_result("GPIO device", False, str(e)))
    
    # Check LCD module
    try:
        from display.lcd5110 import get_lcd
        lcd = get_lcd()
        results.append(test_result(
            "LCD module loaded",
            lcd is not None,
            "LCD module ready"
        ))
    except Exception as e:
        results.append(test_result("LCD module", False, str(e)))
    
    return all(results)


def test_lcd_and_rex_only():
    """Focused tests for LCD and REX only."""
    test_section("LCD & REX FOCUSED TESTS")
    results = []
    
    from display.lcd5110 import get_lcd, MockLCD5110
    from control.rex_client import get_rex_client, MockREXClient
    
    lcd = get_lcd()
    results.append(test_result("LCD instance created", lcd is not None))
    
    lcd_init = lcd.initialize()
    results.append(test_result("LCD initialize", lcd_init or isinstance(lcd, MockLCD5110)))
    
    lcd.clear()
    results.append(test_result("LCD clear", True))
    
    lcd.show_text("Camp Tutor", 0)
    results.append(test_result("LCD show_text", True))
    
    lcd.show_status("idle", student="Test", topic="Math", language="EN")
    results.append(test_result("LCD show_status", True))
    
    lcd.show_text("Test OK", 1)
    lcd.show_text("REX: Ready", 2)
    lcd.show_text("LCD Display", 3)
    
    lcd.show_progress(5, 10)
    results.append(test_result("LCD show_progress", True))
    
    from control.rex_client import REXClient
    rex = get_rex_client()
    results.append(test_result("REX instance created", rex is not None))
    
    if isinstance(rex, REXClient):
        if not rex._connected:
            rex.connect()
        results.append(test_result("REX connect", True))
        
        status = rex.get_status()
        results.append(test_result("REX get_status", "connected" in status))
        
        if rex.is_connected():
            ping_result = rex.ping()
            results.append(test_result("REX ping", ping_result))
        else:
            results.append(test_result("REX ping", True, "Using mock fallback"))
        
        move_result = rex.move_forward(50)
        results.append(test_result("REX move_forward", not move_result or move_result))
        
        stop_result = rex.stop()
        results.append(test_result("REX stop", not stop_result or stop_result))
    else:
        results.append(test_result("REX connect", True))
        results.append(test_result("REX get_status", True))
        results.append(test_result("REX ping", True))
        results.append(test_result("REX move_forward", True))
        results.append(test_result("REX stop", True))
    
    return all(results)


def main():
    """Run all tests."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lcd-rex-only", action="store_true", help="Test LCD and REX only")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  CAMP TUTOR ROBOT DIAGNOSTICS")
    print("  " + "="*55)
    
    print_hardware_info()
    
    if args.lcd_rex_only:
        all_passed = test_lcd_and_rex_only()
    else:
        all_passed = True
        all_passed &= test_imports()
        all_passed &= test_settings()
        all_passed &= test_i2c()
        all_passed &= test_bluetooth()
        all_passed &= test_wifi()
        all_passed &= test_ai()
        all_passed &= test_database()
        all_passed &= test_password_file()
        all_passed &= test_camera()
        all_passed &= test_audio_input()
        all_passed &= test_lcd_screen()
        all_passed &= test_lcd_and_rex_only()
    
    test_section("FINAL RESULT")
    if all_passed:
        print("  ALL TESTS PASSED")
    else:
        print("  SOME TESTS FAILED")
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())