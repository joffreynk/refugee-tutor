"""Student database module with photo support."""

import json
import logging
import os
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

    def _get_unique_name(self, base_name: str) -> str:
        """Generate unique student name by incrementing if duplicate exists."""
        if not any(s.get("name") == base_name for s in self.students.values()):
            return base_name

        counter = 1
        while True:
            new_name = f"{base_name}{counter}"
            if not any(s.get("name") == new_name for s in self.students.values()):
                return new_name
            counter += 1

    def create_student(
        self,
        name: str,
        preferred_language: str = "en",
        classroom: Optional[str] = None,
        age: Optional[int] = None,
    ) -> str:
        """Create a new student profile."""
        student_id = f"student_{uuid.uuid4().hex}"
        unique_name = self._get_unique_name(name.strip())

        self.students[student_id] = {
            "id": student_id,
            "name": unique_name,
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

        student_name = self.students[student_id].get("name", "student")
        base_name = student_name.replace(" ", "_").lower()

        if filename is None:
            count = self.students[student_id].get("photo_count", 0)
            filename = f"{base_name}_{count + 1}.jpg"

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

    def get_all_photos(self, student_id: str) -> list:
        """Get all photo paths for a student."""
        if student_id not in self.students:
            return []

        student_photos = self._photos_dir / student_id
        if not student_photos.exists():
            return []

        photos = sorted(student_photos.glob("*.jpg"))
        return [str(p) for p in photos]

    def delete_photo(self, student_id: str, photo_index: int) -> bool:
        """Delete a photo by index (1-based)."""
        if student_id not in self.students:
            return False

        photos = self.get_all_photos(student_id)
        if photo_index < 1 or photo_index > len(photos):
            return False

        try:
            os.remove(photos[photo_index - 1])
            self.students[student_id]["photo_count"] = max(0, self.students[student_id].get("photo_count", 1) - 1)
            self._save()
            return True
        except Exception as e:
            logger.error(f"Failed to delete photo: {e}")
            return False

    def update_student_name(self, student_id: str, new_name: str) -> bool:
        """Update student name and rename photo files."""
        if student_id not in self.students:
            return False

        old_name = self.students[student_id].get("name", "student")
        if old_name == new_name:
            return True

        unique_name = self._get_unique_name(new_name.strip())
        self.students[student_id]["name"] = unique_name

        old_base = old_name.replace(" ", "_").lower()
        new_base = unique_name.replace(" ", "_").lower()

        student_photos = self._photos_dir / student_id
        if student_photos.exists():
            for photo_file in student_photos.glob("*.jpg"):
                if old_base in photo_file.name:
                    new_name_file = photo_file.name.replace(old_base, new_base)
                    photo_file.rename(student_photos / new_name_file)

        self._save()
        return True

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

    def update_computing_progress(self, student_id: str, lesson_number: int, completed: bool, score: float = 0) -> bool:
        """Update Year 7 Computing lesson progress."""
        if student_id not in self.students:
            return False

        if "computing_progress" not in self.students[student_id]:
            self.students[student_id]["computing_progress"] = {
                "current_lesson": 1,
                "completed_lessons": [],
                "total_time_minutes": 0,
                "last_lesson_date": None
            }

        cp = self.students[student_id]["computing_progress"]

        if completed and lesson_number not in cp["completed_lessons"]:
            cp["completed_lessons"].append(lesson_number)
            cp["current_lesson"] = lesson_number + 1 if lesson_number < 60 else lesson_number

        if score > 0:
            if "lesson_scores" not in cp:
                cp["lesson_scores"] = {}
            cp["lesson_scores"][str(lesson_number)] = score

        cp["last_lesson_date"] = datetime.now().isoformat()
        self._save()
        return True

    def get_computing_progress(self, student_id: str) -> dict:
        """Get Year 7 Computing progress."""
        if student_id not in self.students:
            return {"current_lesson": 1, "completed_lessons": [], "total_time_minutes": 0}

        return self.students[student_id].get("computing_progress", {
            "current_lesson": 1,
            "completed_lessons": [],
            "total_time_minutes": 0
        })

    def set_computing_lesson(self, student_id: str, lesson_number: int) -> bool:
        """Set which lesson to teach next."""
        if student_id not in self.students:
            return False

        if "computing_progress" not in self.students[student_id]:
            self.students[student_id]["computing_progress"] = {
                "current_lesson": 1,
                "completed_lessons": [],
                "total_time_minutes": 0,
                "last_lesson_date": None
            }

        self.students[student_id]["computing_progress"]["current_lesson"] = lesson_number
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
                if avg < settings.SCORE_THRESHOLD:
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


_student_db_instance: Optional[StudentDB] = None


def get_student_db() -> StudentDB:
    """Get global student database instance."""
    global _student_db_instance
    if _student_db_instance is None:
        _student_db_instance = StudentDB()
    return _student_db_instance