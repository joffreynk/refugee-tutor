"""Camp Tutor - Main entry point."""

import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional

from config import settings as config_settings
from config.wifi_manager import get_wifi_manager
from web import web_ui

from audio import wake_word, speech_to_text, text_to_speech, audio_device
from ai import (
    language_detection,
    tutor_engine,
    homework_generator,
    assessment_engine,
    progress_tracker,
    tflite_models,
)
from vision import camera, visual_monitor
from vision.camera_capture import get_camera
from vision.facial_recognition import get_facial_recognition
from display import lcd5110
from storage import student_db, session_logger
from storage.student_db import get_student_db
from control import rex_client, decision_manager

logger = logging.getLogger(__name__)


class CampTutorRobot:
    """Main robot controller."""

    def __init__(self):
        self.state = "IDLE"
        self.wake_detector: Optional[wake_word.WakeWordDetector] = None
        self.stt: Optional[speech_to_text.SpeechToText] = None
        self.tts: Optional[text_to_speech.TextToSpeech] = None
        self.lang_detector: Optional[language_detection.LanguageDetector] = None
        self.tutor: Optional[tutor_engine.TutorEngine] = None
        self.homework_gen: Optional[homework_generator.HomeworkGenerator] = None
        self.assessment: Optional[assessment_engine.AssessmentEngine] = None
        self.progress: Optional[progress_tracker.ProgressTracker] = None
        self.db: Optional[student_db.StudentDB] = None
        self.session: Optional[session_logger.SessionLogger] = None
        self.lcd: Optional[lcd5110.LCD5110] = None
        self.vision: Optional[visual_monitor.VisualMonitor] = None
        self.camera_capture = None
        self.facial_rec = None
        self.wifi = None
        self.rex: Optional[rex_client.REXClient] = None
        self.decision: Optional[decision_manager.DecisionManager] = None
        
        self.current_student_id: Optional[str] = None
        self.current_language: str = "en"
        self.session_active = False
        self.last_activity_time = 0
        
        self._running = False
        self._shutdown_requested = False

    def initialize(self) -> bool:
        """Initialize all subsystems."""
        logging.basicConfig(
            level=config_settings.LOG_LEVEL,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        logger.info("Initializing Camp Tutor...")

        config_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Track device initialization status
        self.device_status = {
            "lcd": {"ok": False, "error": None},
            "rex": {"ok": False, "error": None},
            "camera": {"ok": False, "error": None},
            "audio": {"ok": False, "error": None},
        }

        # Initialize LCD (continue even if fails)
        try:
            self.lcd = lcd5110.get_lcd()
            self.lcd.initialize()
            self.lcd.show_text("Camp Tutor", 0)
            self.lcd.show_text("Initializing...", 1)
            self.device_status["lcd"]["ok"] = True
        except Exception as e:
            self.device_status["lcd"]["error"] = str(e)
            logger.warning(f"LCD init failed: {e}")
            self.lcd = None

        # Initialize audio (continue even if fails)
        try:
            self.wake_detector = wake_word.WakeWordDetector()
            self.stt = speech_to_text.SpeechToText()
            self.tts = text_to_speech.TextToSpeech()
            self.device_status["audio"]["ok"] = True
        except Exception as e:
            self.device_status["audio"]["error"] = str(e)
            logger.warning(f"Audio init failed: {e}")
            self.wake_detector = None
            self.stt = None
            self.tts = None

        self.lang_detector = language_detection.get_language_detector()
        self.tutor = tutor_engine.get_tutor_engine()
        self.homework_gen = homework_generator.get_homework_generator()
        self.assessment = assessment_engine.get_assessment_engine()
        self.progress = progress_tracker.get_progress_tracker()
        self.db = student_db.get_student_db()
        self.session = session_logger.get_session_logger()
        self.vision = visual_monitor.get_visual_monitor()

        # Initialize camera (continue even if fails)
        try:
            self.camera_capture = get_camera()
            self.facial_rec = get_facial_recognition()
            self.facial_rec.initialize()
            self.device_status["camera"]["ok"] = True
        except Exception as e:
            self.device_status["camera"]["error"] = str(e)
            logger.warning(f"Camera init failed: {e}")
            self.camera_capture = None
            self.facial_rec = None

        # Initialize WiFi (continue even if fails)
        try:
            self.wifi = get_wifi_manager()
        except Exception as e:
            logger.warning(f"WiFi init failed: {e}")
            self.wifi = None

        # Initialize REX (continue even if fails)
        try:
            self.rex = rex_client.get_rex_client()
            self.rex.connect()
            if self.rex.is_connected():
                self.device_status["rex"]["ok"] = True
                logger.info("REX connected")
            else:
                self.device_status["rex"]["error"] = "REX not responding"
                logger.warning("REX not responding")
        except Exception as e:
            self.device_status["rex"]["error"] = str(e)
            logger.warning(f"REX init failed: {e}")
            self.rex = None

        self.decision = decision_manager.get_decision_manager()

        self.tutor.set_language("en")
        self.homework_gen.set_language("en")
        self.assessment.set_language("en")

        self.decision.initialize()

        # Show status on LCD if available
        wifi_status = self.wifi.get_status() if self.wifi else {}
        if self.lcd and self.device_status["lcd"]["ok"]:
            if wifi_status.get("connected"):
                logger.info(f"WiFi connected: {wifi_status.get('ssid')}")
                self.lcd.show_text(f"WiFi: {wifi_status.get('ssid')}", 1)
            elif self.wifi.is_offline_mode():
                logger.info("Running in offline mode")
                self.lcd.show_text("Offline Mode", 1)
            else:
                self.lcd.show_text("Say 'Camp Tutor'", 1)

            self.lcd.show_text("Camp Tutor", 0)

        logger.info(f"Device status: {self.device_status}")
        logger.info("Camp Tutor initialized")
        
        from config import settings as config_settings
        web_ui.start_server_thread(host="0.0.0.0", port=config_settings.WEB_PORT)
        logger.info(f"Web server started at {config_settings.WEB_URL}")

        # Update web UI with device status
        web_ui._app_state["device_status"] = self.device_status
        
        return True

    def start(self) -> None:
        """Start the robot."""
        self._running = True
        self.state = "IDLE"

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        if self.wake_detector:
            self.wake_detector.start(self._on_wake_detected)

        while self._running and not self._shutdown_requested:
            self._check_inactivity()
            time.sleep(1)

    def _on_wake_detected(self) -> None:
        """Handle wake word detection."""
        logger.info("Wake word detected!")
        self.state = "LISTENING"
        self.last_activity_time = time.time()

        if self.tts and self.tutor:
            greeting = self.tutor.get_greeting()
            self.tts.speak(greeting)

        if self.lcd:
            self.lcd.show_status("LISTENING", topic="Language?")

        self._detect_language()

    def _detect_language(self) -> None:
        """Detect or confirm language."""
        if not self.stt:
            return

        if self.tts:
            self.tts.speak("What language would you like to learn?")

        text = self.stt.listen(timeout=8.0)

        if text and self.lang_detector:
            detected = self.lang_detector.detect(text)
            self.current_language = detected

            if self.tutor:
                self.tutor.set_language(detected)
            if self.homework_gen:
                self.homework_gen.set_language(detected)
            if self.assessment:
                self.assessment.set_language(detected)

            lang_name = config_settings.LANGUAGE_NAMES.get(detected, detected)
            if self.tts:
                self.tts.speak(f"Okay, let's learn in {lang_name}")
        else:
            self.current_language = "en"
            if self.tutor:
                self.tutor.set_language("en")

        if self.lcd:
            self.lcd.show_status("TEACHING", language=self.current_language)
        self.state = "TEACHING"
        self.session_active = True

    def start_session(self) -> bool:
        """Start a tutoring session."""
        if not self.session_active:
            return False

        if self.db:
            self.current_student_id = self.db.create_student("Learner", self.current_language)

        student_id = self.current_student_id
        if not student_id:
            logger.error("No student ID created")
            return False

        if self.session:
            self.session.start_session(student_id, self.current_language)

        if self.tutor:
            self.tutor.start_session(student_id, self.current_language)

        logger.info(f"Session started: {student_id}")
        return True

    def end_session(self) -> None:
        """End the current session."""
        if self.session_active and self.current_student_id:
            if self.session:
                self.session.end_session(completed=True)
            if self.tutor:
                self.tutor.end_session()

            if self.db:
                self.db.increment_session(self.current_student_id, 30)

        self.session_active = False
        self.state = "IDLE"
        if self.lcd:
            self.lcd.show_text("Camp Tutor", 0)
            self.lcd.show_text("Say 'Camp Tutor'", 1)

        if self.wake_detector:
            self.wake_detector.start(self._on_wake_detected)

    def _check_inactivity(self) -> None:
        """Check for inactivity timeout."""
        if not self.session_active:
            return

        if time.time() - self.last_activity_time > config_settings.INACTIVITY_TIMEOUT:
            logger.info("Inactivity timeout, ending session")
            self.end_session()

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True
        self._running = False
        self.shutdown()

    def shutdown(self) -> None:
        """Clean shutdown."""
        logger.info("Shutting down Camp Tutor...")

        if self.wake_detector:
            self.wake_detector.stop()

        if self.rex:
            self.rex.disconnect()

        if self.lcd:
            self.lcd.close()

        if self.vision:
            self.vision.close()

        logger.info("Camp Tutor shutdown complete")

    def run_interactive(self) -> None:
        """Run interactive teaching session."""
        if not self.initialize():
            logger.error("Initialization failed")
            return

        self.start_session()

        if not self.tutor:
            logger.error("Tutor engine not initialized")
            return
            
        topic = self.tutor.get_topic_list()[0]
        self.tutor.teach_topic(topic)

        while self.session_active:
            phrase = self.tutor.get_next_phrase()
            if not phrase:
                break

            if self.tts:
                self.tts.speak(phrase)

            time.sleep(2)

            if self.stt:
                answer = self.stt.listen(timeout=5.0)
            else:
                answer = None
                
            if answer:
                correct = self._validate_answer(answer, phrase)

                if self.current_student_id and self.tutor and self.tutor.current_topic:
                    if self.progress:
                        self.progress.record_answer(
                            self.current_student_id,
                            self.tutor.current_topic,
                            correct,
                        )

                if self.tts:
                    if correct:
                        self.tts.speak("Great job!")
                    else:
                        self.tts.speak("Let's try again.")

        self.last_activity_time = time.time()
        
    def _validate_answer(self, answer: str, expected: str) -> bool:
        """Validate student answer against expected response."""
        if not answer or not expected:
            return False
        
        answer_lower = answer.lower().strip()
        expected_lower = expected.lower().strip()
        
        if answer_lower == expected_lower:
            return True
        
        if len(answer_lower) > 2 and expected_lower in answer_lower:
            return True
        
        words = answer_lower.split()
        expected_words = expected_lower.split()
        matches = sum(1 for w in expected_words if w in words)
        return matches >= len(expected_words) * 0.5

    def record_student_progress(self, subject: str, topic: str, correct: bool, score: float = 1.0) -> None:
        """Record student progress for a subject/topic."""
        if not self.current_student_id or not self.db:
            return
        
        if not correct:
            score = 0.0
        
        self.db.update_subject_progress(
            self.current_student_id,
            subject,
            topic,
            score
        )
        logger.info(f"Progress recorded: {subject}/{topic} - {'correct' if correct else 'incorrect'}")


def main():
    """Main entry point."""
    robot = CampTutorRobot()

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        robot.run_interactive()
    else:
        robot.initialize()
        robot.start()


if __name__ == "__main__":
    main()
