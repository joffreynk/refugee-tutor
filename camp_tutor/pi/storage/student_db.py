"""Student database module with photo support."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


class StudentDB:
    """Student profile database with photo support."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.STUDENT_DB_PATH
        self.students: dict = {}
        self._photos_dir = settings.DATA_DIR / "student_photos"
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
        classroom: Optional[str] = None,
        age: Optional[int] = None,
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
            "classroom": classroom,
            "age": age,
            "photo_count": 0,
            "last_seen": None,
            "subjects": {},
            "progress": {},
        }

        self._save()
        self._init_student_photos_dir(student_id)
        logger.info(f"Created student: {student_id}")
        return student_id

    def _init_student_photos_dir(self, student_id: str) -> Path:
        """Create directory for student photos."""
        student_photos = self._photos_dir / student_id
        student_photos.mkdir(parents=True, exist_ok=True)
        return student_photos

    def add_photo(self, student_id: str, photo_data: bytes, filename: Optional[str] = None) -> Optional[str]:
        """Add a photo for a student."""
        if student_id not in self.students:
            return None

        if filename is None:
            count = self.students[student_id].get("photo_count", 0)
            filename = f"photo_{count + 1}.jpg"

        student_photos = self._photos_dir / student_id
        student_photos.mkdir(parents=True, exist_ok=True)
        
        filepath = student_photos / filename
        try:
            with open(filepath, "wb") as f:
                f.write(photo_data)

            self.students[student_id]["photo_count"] = self.students[student_id].get("photo_count", 0) + 1
            self._save()
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save photo: {e}")
            return None

    def get_photo_path(self, student_id: str, photo_index: int = 1) -> Optional[str]:
        """Get path to a student's photo."""
        if student_id not in self.students:
            return None

        student_photos = self._photos_dir / student_id
        photo_path = student_photos / f"photo_{photo_index}.jpg"
        
        if photo_path.exists():
            return str(photo_path)
        
        for f in sorted(student_photos.glob("*.jpg")):
            return str(f)
        
        return None

    def get_photos_dir(self, student_id: str) -> Optional[Path]:
        """Get the photos directory for a student."""
        if student_id not in self.students:
            return None
        return self._photos_dir / student_id

    def update_subject_progress(self, student_id: str, subject: str, topic: str, score: float) -> bool:
        """Update progress for a specific subject/topic."""
        if student_id not in self.students:
            return False

        if "subjects" not in self.students[student_id]:
            self.students[student_id]["subjects"] = {}

        if subject not in self.students[student_id]["subjects"]:
            self.students[student_id]["subjects"][subject] = {"topics": {}, "average_score": 0}

        if topic not in self.students[student_id]["subjects"][subject]["topics"]:
            self.students[student_id]["subjects"][subject]["topics"][topic] = {"attempts": 0, "total_score": 0, "last_score": 0}

        topic_data = self.students[student_id]["subjects"][subject]["topics"][topic]
        topic_data["attempts"] += 1
        topic_data["total_score"] += score
        topic_data["last_score"] = score
        topic_data["average_score"] = topic_data["total_score"] / topic_data["attempts"]

        self._recalculate_subject_average(student_id, subject)
        self._save()
        return True

    def _recalculate_subject_average(self, student_id: str, subject: str) -> None:
        """Recalculate average score for a subject."""
        if subject not in self.students[student_id].get("subjects", {}):
            return

        topics = self.students[student_id]["subjects"][subject].get("topics", {})
        if topics:
            total = sum(t.get("average_score", 0) for t in topics.values())
            self.students[student_id]["subjects"][subject]["average_score"] = total / len(topics)

    def get_subject_progress(self, student_id: str, subject: str) -> Optional[dict]:
        """Get progress for a specific subject."""
        if student_id not in self.students:
            return None
        return self.students[student_id].get("subjects", {}).get(subject)

    def get_all_subjects_progress(self, student_id: str) -> dict:
        """Get progress for all subjects."""
        if student_id not in self.students:
            return {}
        return self.students[student_id].get("subjects", {})

    def get_weak_topics(self, student_id: str, subject: Optional[str] = None) -> list:
        """Get topics where student is struggling (score < 60%)."""
        if student_id not in self.students:
            return []

        weak_topics = []
        subjects = self.students[student_id].get("subjects", {})

        for subj, data in subjects.items():
            if subject and subj != subject:
                continue

            for topic, topic_data in data.get("topics", {}).items():
                avg = topic_data.get("average_score", 0)
                if avg < 0.6:
                    weak_topics.append({
                        "subject": subj,
                        "topic": topic,
                        "score": avg,
                        "attempts": topic_data.get("attempts", 0),
                    })

        weak_topics.sort(key=lambda x: x["score"])
        return weak_topics

    def set_classroom(self, student_id: str, classroom: Optional[str]) -> bool:
        """Set classroom for a student."""
        if student_id not in self.students:
            return False
        self.students[student_id]["classroom"] = classroom
        self._save()
        return True

    def get_classroom_students(self, classroom: str) -> list:
        """Get all students in a classroom."""
        return [
            s for s in self.students.values()
            if s.get("classroom") == classroom
        ]

    def record_attendance(self, student_id: str) -> bool:
        """Record student attendance."""
        if student_id not in self.students:
            return False
        self.students[student_id]["last_seen"] = datetime.now().isoformat()
        self._save()
        return True

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

    def set_classroom(self, student_id: str, classroom: Optional[str]) -> bool:
        """Set classroom for a student."""
        if student_id not in self.students:
            return False
        self.students[student_id]["classroom"] = classroom
        self._save()
        return True

    def get_classroom_students(self, classroom: str) -> list:
        """Get all students in a classroom."""
        return [
            s for s in self.students.values()
            if s.get("classroom") == classroom
        ]

    def record_attendance(self, student_id: str) -> bool:
        """Record student attendance."""
        if student_id not in self.students:
            return False
        self.students[student_id]["last_seen"] = datetime.now().isoformat()
        self._save()
        return True


_student_db_instance: Optional[StudentDB] = None


def get_student_db() -> StudentDB:
    """Get global student database instance."""
    global _student_db_instance
    if _student_db_instance is None:
        _student_db_instance = StudentDB()
    return _student_db_instance