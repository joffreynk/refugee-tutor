"""Class and timetable management for Camp Tutor."""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class LessonPlan:
    """Individual lesson plan."""
    id: str
    subject: str
    topic: str
    age_group: str
    completed: bool = False
    completed_at: Optional[datetime] = None
    duration_minutes: int = 30


@dataclass
class TimetableEntry:
    """Timetable entry for a class."""
    id: str
    age_group: str
    day_of_week: int
    start_time: str
    subject: str
    topic: str
    duration_minutes: int = 30
    completed: bool = False
    last_taught: Optional[datetime] = None


@dataclass
class ClassSession:
    """A class session being taught."""
    id: str
    age_group: str
    student_count: int
    start_time: datetime
    end_time: Optional[datetime] = None
    lessons_completed: list = field(default_factory=list)
    current_subject: str = "mathematics"
    current_topic: str = ""


class ClassManager:
    """Manages classes - one class at a time."""

    def __init__(self):
        self.current_class: Optional[ClassSession] = None
        self.age_group: str = "primary"
        self.timetable: list[TimetableEntry] = []
        self.lesson_history: list[LessonPlan] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load saved timetable and history."""
        data_path = settings.DATA_DIR / "class_data.json"
        if data_path.exists():
            try:
                with open(data_path, "r") as f:
                    data = json.load(f)
                    self.age_group = data.get("age_group", "primary")
                    self.timetable = [
                        TimetableEntry(**entry) for entry in data.get("timetable", [])
                    ]
                    self.lesson_history = [
                        LessonPlan(**lesson) for lesson in data.get("history", [])
                    ]
                logger.info(f"Loaded class data: {len(self.timetable)} timetable entries")
            except Exception as e:
                logger.warning(f"Could not load class data: {e}")

    def _save_data(self) -> None:
        """Save timetable and history."""
        data_path = settings.DATA_DIR / "class_data.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(data_path, "w") as f:
                json.dump({
                    "age_group": self.age_group,
                    "timetable": [vars(entry) for entry in self.timetable],
                    "history": [vars(lesson) for lesson in self.lesson_history],
                }, f, default=str)
        except Exception as e:
            logger.error(f"Could not save class data: {e}")

    def set_age_group(self, age_group: str) -> bool:
        """Switch to a different age group."""
        if age_group in settings.AGE_GROUP_KEYS:
            self.age_group = age_group
            self._save_data()
            logger.info(f"Switched to age group: {age_group}")
            return True
        return False

    def get_age_group(self) -> str:
        """Get current age group."""
        return self.age_group

    def get_age_group_display(self) -> str:
        """Get display name for current age group."""
        return settings.AGE_GROUP_DISPLAY.get(self.age_group, "Unknown")

    def start_class(self, student_count: int = 1) -> ClassSession:
        """Start a new class session for current age group."""
        if self.current_class:
            logger.warning("Class already in progress")

        self.current_class = ClassSession(
            id=str(uuid.uuid4()),
            age_group=self.age_group,
            student_count=student_count,
            start_time=datetime.now(),
        )
        logger.info(f"Started class for {self.age_group}, {student_count} students")
        return self.current_class

    def end_class(self) -> Optional[ClassSession]:
        """End current class session."""
        if not self.current_class:
            return None

        self.current_class.end_time = datetime.now()

        for lesson_id in self.current_class.lessons_completed:
            for lesson in self.lesson_history:
                if lesson.id == lesson_id:
                    lesson.completed = True
                    lesson.completed_at = datetime.now()

        finished_class = self.current_class
        self.current_class = None
        self._save_data()
        logger.info(f"Ended class session: {finished_class.id}")
        return finished_class

    def is_class_in_progress(self) -> bool:
        """Check if a class is currently in progress."""
        return self.current_class is not None

    def generate_timetable(self, age_group: str) -> list[TimetableEntry]:
        """Generate a timetable for an age group based on daily schedule."""
        schedule_config = settings.DAILY_SCHEDULE.get(age_group, {})
        schedule = schedule_config.get("schedule", [])

        timetable = []
        for slot in schedule:
            subject = slot.get("subject", "")
            if subject == "break":
                continue

            topic = self._get_next_topic(age_group, subject, len(timetable))

            entry = TimetableEntry(
                id=str(uuid.uuid4()),
                age_group=age_group,
                day_of_week=0,
                start_time=slot.get("time", "08:00"),
                subject=subject,
                topic=topic,
                duration_minutes=slot.get("duration", 30),
            )
            timetable.append(entry)

        logger.info(f"Generated daily schedule for {age_group}: {len(timetable)} lessons")
        return timetable

    def get_current_schedule(self) -> list[dict]:
        """Get today's schedule for current age group."""
        schedule_config = settings.DAILY_SCHEDULE.get(self.age_group, {})
        return schedule_config.get("schedule", [])

    def get_next_slot(self) -> Optional[dict]:
        """Get next slot in today's schedule."""
        schedule = self.get_current_schedule()
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        for slot in schedule:
            if slot.get("time", "") > current_time:
                return slot
        return None

    def get_current_slot(self) -> Optional[dict]:
        """Get current time slot in schedule."""
        schedule = self.get_current_schedule()
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        for i, slot in enumerate(schedule):
            slot_time = slot.get("time", "")
            duration = slot.get("duration", 0)
            hour, minute = map(int, slot_time.split(":"))
            end_minute = minute + duration

            if end_minute >= 60:
                end_hour = hour + (end_minute // 60)
                end_minute = end_minute % 60
            else:
                end_hour = hour

            end_time = f"{end_hour:02d}:{end_minute:02d}"

            if slot_time <= current_time <= end_time:
                return slot

        return None

    def _get_next_topic(self, age_group: str, subject: str, week_num: int) -> str:
        """Get next topic based on curriculum and progress."""
        completed_topics = [
            lesson.topic for lesson in self.lesson_history
            if lesson.age_group == age_group
            and lesson.subject == subject
            and lesson.completed
        ]

        curriculum = settings.CURRICULUM.get(age_group, {})
        subject_content = curriculum.get(subject, {})

        available_topics = list(subject_content.keys())
        for topic in available_topics:
            if topic not in completed_topics:
                return topic

        return available_topics[0] if available_topics else "default"

    def get_timetable(self, age_group: Optional[str] = None) -> list[TimetableEntry]:
        """Get timetable for age group."""
        if not self.timetable:
            self.timetable = self.generate_timetable(age_group or self.age_group)
        return [e for e in self.timetable if e.age_group == (age_group or self.age_group)]

    def get_next_lesson(self) -> Optional[TimetableEntry]:
        """Get the next lesson to teach based on timetable."""
        timetable = self.get_timetable()
        now = datetime.now()
        current_day = now.weekday()

        for entry in timetable:
            if not entry.completed:
                if entry.day_of_week <= current_day:
                    last_taught = entry.last_taught
                    if not last_taught or (now - last_taught).days >= 1:
                        return entry
                return entry

        return timetable[0] if timetable else None

    def get_ai_recommendation(self) -> dict:
        """Get AI recommendation for next lesson."""
        next_lesson = self.get_next_lesson()
        if not next_lesson:
            return {"subject": "mathematics", "topic": "default", "reason": "No lesson found"}

        completed_count = sum(1 for l in self.lesson_history if l.age_group == self.age_group and l.completed)
        total_count = len(self.lesson_history)

        weak_areas = self._identify_weak_areas()

        return {
            "subject": next_lesson.subject,
            "topic": next_lesson.topic,
            "reason": f"Next in timetable",
            "completed_lessons": completed_count,
            "progress": f"{completed_count}/{total_count}",
            "suggested_focus": weak_areas[0] if weak_areas else next_lesson.subject,
        }

    def _identify_weak_areas(self) -> list[str]:
        """Identify subjects that need more attention."""
        subject_scores = {}

        for lesson in self.lesson_history:
            if lesson.age_group == self.age_group and lesson.completed:
                if lesson.subject not in subject_scores:
                    subject_scores[lesson.subject] = []
                subject_scores[lesson.subject].append(1)

        weak = []
        for subject, count in subject_scores.items():
            if len(count) < 3:
                weak.append(subject)

        return weak

    def record_lesson(self, subject: str, topic: str, age_group: str) -> LessonPlan:
        """Record a lesson as completed."""
        lesson = LessonPlan(
            id=str(uuid.uuid4()),
            subject=subject,
            topic=topic,
            age_group=age_group,
            completed=True,
            completed_at=datetime.now(),
        )
        self.lesson_history.append(lesson)

        if self.current_class:
            self.current_class.lessons_completed.append(lesson.id)

        self._update_timetable(subject, topic)
        self._save_data()
        logger.info(f"Recorded lesson: {subject} - {topic}")
        return lesson

    def _update_timetable(self, subject: str, topic: str) -> None:
        """Mark timetable entry as completed."""
        for entry in self.timetable:
            if entry.subject == subject and entry.topic == topic and not entry.completed:
                entry.completed = True
                entry.last_taught = datetime.now()
                break

    def get_progress_summary(self) -> dict:
        """Get progress summary for all age groups."""
        summary = {}

        for age_group in settings.AGE_GROUP_KEYS:
            age_lessons = [l for l in self.lesson_history if l.age_group == age_group]
            completed = [l for l in age_lessons if l.completed]
            total = len(age_lessons)

            subjects = settings.CURRICULUM.get(age_group, {})
            total_topics = sum(len(subjects.get(s, {})) for s in subjects)

            summary[age_group] = {
                "display_name": settings.AGE_GROUP_DISPLAY.get(age_group, age_group),
                "completed_lessons": len(completed),
                "total_lessons": total,
                "progress_percent": int((len(completed) / total_topics * 100)) if total_topics > 0 else 0,
                "subjects": list(subjects.keys()),
            }

        return summary

    def get_current_class_info(self) -> Optional[dict]:
        """Get info about current class."""
        if not self.current_class:
            return None

        return {
            "id": self.current_class.id,
            "age_group": self.current_class.age_group,
            "age_group_display": settings.AGE_GROUP_DISPLAY.get(self.current_class.age_group),
            "student_count": self.current_class.student_count,
            "start_time": self.current_class.start_time.strftime("%H:%M"),
            "lessons_completed": len(self.current_class.lessons_completed),
            "current_subject": self.current_class.current_subject,
        }

    def reset_timetable(self, age_group: str) -> None:
        """Reset timetable for an age group."""
        self.timetable = self.generate_timetable(age_group)
        self._save_data()
        logger.info(f"Reset timetable for {age_group}")


_class_manager_instance: Optional[ClassManager] = None


def get_class_manager() -> ClassManager:
    """Get global class manager instance."""
    global _class_manager_instance
    if _class_manager_instance is None:
        _class_manager_instance = ClassManager()
    return _class_manager_instance