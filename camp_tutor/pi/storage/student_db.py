"""Student database module."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


class StudentDB:
    """Student profile database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.STUDENT_DB_PATH
        self.students: dict = {}
        self._load()

    def _load(self) -> None:
        """Load database from file."""
        if self.db_path.exists():
            try:
                with open(self.db_path) as f:
                    self.students = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load student DB: {e}")
                self.students = {}

    def _save(self) -> None:
        """Save database to file."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(self.students, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save student DB: {e}")

    def create_student(
        self,
        name: str,
        preferred_language: str = "en",
    ) -> str:
        """Create a new student profile."""
        student_id = f"student_{uuid.uuid4().hex[:8]}"

        self.students[student_id] = {
            "id": student_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "preferred_language": preferred_language,
            "current_level": 1,
            "total_sessions": 0,
            "total_time_minutes": 0,
        }

        self._save()
        logger.info(f"Created student: {student_id}")
        return student_id

    def get_student(self, student_id: str) -> Optional[dict]:
        """Get student by ID."""
        return self.students.get(student_id)

    def get_all_students(self) -> list[dict]:
        """Get all students."""
        return list(self.students.values())

    def get_student_count(self) -> int:
        """Get total number of students."""
        return len(self.students)

    def update_student(self, student_id: str, data: dict) -> bool:
        """Update student information."""
        if student_id not in self.students:
            return False

        self.students[student_id].update(data)
        self._save()
        return True

    def increment_session(self, student_id: str, duration_minutes: int) -> bool:
        """Increment session count and time."""
        if student_id not in self.students:
            return False

        self.students[student_id]["total_sessions"] = (
            self.students[student_id].get("total_sessions", 0) + 1
        )
        self.students[student_id]["total_time_minutes"] = (
            self.students[student_id].get("total_time_minutes", 0) + duration_minutes
        )

        self._save()
        return True

    def set_level(self, student_id: str, level: int) -> bool:
        """Set student level."""
        if student_id not in self.students:
            return False

        self.students[student_id]["current_level"] = max(1, min(10, level))
        self._save()
        return True

    def delete_student(self, student_id: str) -> bool:
        """Delete a student."""
        if student_id not in self.students:
            return False

        del self.students[student_id]
        self._save()
        return True

    def search_students(self, query: str) -> list[dict]:
        """Search students by name."""
        query_lower = query.lower()
        return [
            s for s in self.students.values()
            if query_lower in s.get("name", "").lower()
        ]


_student_db_instance: Optional[StudentDB] = None


def get_student_db() -> StudentDB:
    """Get global student database instance."""
    global _student_db_instance
    if _student_db_instance is None:
        _student_db_instance = StudentDB()
    return _student_db_instance