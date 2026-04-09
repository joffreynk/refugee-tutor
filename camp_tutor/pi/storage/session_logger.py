"""Session logging module."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


class SessionLogger:
    """Logs tutoring sessions."""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or settings.SESSION_LOG_PATH
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[dict] = None

    def start_session(
        self,
        student_id: str,
        language: str = "en",
    ) -> str:
        """Start a new session."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        self.current_session = {
            "id": session_id,
            "student_id": student_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "language": language,
            "topic": None,
            "completed": False,
            "events": [],
        }

        logger.info(f"Started session: {session_id}")
        return session_id

    def set_topic(self, topic: str) -> None:
        """Set current topic."""
        if self.current_session:
            self.current_session["topic"] = topic

    def log_event(self, event_type: str, data: dict) -> None:
        """Log an event."""
        if not self.current_session:
            return

        self.current_session["events"].append({
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        })

    def end_session(self, completed: bool = True) -> Optional[dict]:
        """End current session."""
        if not self.current_session:
            return None

        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["completed"] = completed

        session = self.current_session

        self._save_session(session)

        logger.info(f"Ended session: {session['id']}")
        self.current_session = None
        return session

    def _save_session(self, session: dict) -> None:
        """Save session to file."""
        filename = f"{session['id']}.json"
        filepath = self.log_dir / filename

        try:
            with open(filepath, "w") as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save session: {e}")

    def get_session(self, session_id: str) -> Optional[dict]:
        """Load a session."""
        filepath = self.log_dir / f"{session_id}.json"

        if not filepath.exists():
            return None

        try:
            with open(filepath) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load session: {e}")
            return None

    def get_student_sessions(self, student_id: str) -> list[dict]:
        """Get all sessions for a student."""
        sessions = []

        for filepath in self.log_dir.glob(f"session_*.json"):
            try:
                with open(filepath) as f:
                    session = json.load(f)
                    if session.get("student_id") == student_id:
                        sessions.append(session)
            except Exception:
                continue

        return sorted(
            sessions,
            key=lambda s: s.get("start_time", ""),
            reverse=True,
        )

    def get_recent_sessions(self, limit: int = 10) -> list[dict]:
        """Get recent sessions."""
        all_sessions = list(self.log_dir.glob("session_*.json"))
        all_sessions.sort(reverse=True)

        sessions = []
        for filepath in all_sessions[:limit]:
            try:
                with open(filepath) as f:
                    sessions.append(json.load(f))
            except Exception:
                continue

        return sessions


_session_logger_instance: Optional[SessionLogger] = None


def get_session_logger() -> SessionLogger:
    """Get global session logger instance."""
    global _session_logger_instance
    if _session_logger_instance is None:
        _session_logger_instance = SessionLogger()
    return _session_logger_instance