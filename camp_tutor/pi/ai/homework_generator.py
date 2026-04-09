"""Homework generator module."""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


HOMEWORK_TEMPLATES = {
    "en": {
        "alphabet": [
            {"question": "Write the letter A 5 times", "type": "practice"},
            {"question": "Circle all the A's in the text", "type": "practice"},
            {"question": "Match the letter to the picture", "type": "match"},
        ],
        "numbers": [
            {"question": "Count from 1 to 10", "type": "practice"},
            {"question": "Write numbers 1-5", "type": "practice"},
            {"question": "Count the objects", "type": "count"},
        ],
        "colors": [
            {"question": "Color the apple red", "type": "color"},
            {"question": "Match the color to the object", "type": "match"},
            {"question": "Name 3 colors you see", "type": "recall"},
        ],
    },
    "fr": {
        "alphabet": [
            {"question": "Écrivez la lettre A 5 fois", "type": "practice"},
            {"question": "Entourez tous les A", "type": "practice"},
        ],
        "numbers": [
            {"question": "Comptez de 1 à 10", "type": "practice"},
            {"question": "Écrivez les chiffres 1-5", "type": "practice"},
        ],
    },
}


class HomeworkGenerator:
    """Generates homework assignments."""

    def __init__(self):
        self.language = "en"

    def set_language(self, language: str) -> None:
        """Set homework language."""
        if language in settings.LANGUAGE_CODES:
            self.language = language

    def generate(
        self,
        student_id: str,
        topic: str,
        num_exercises: int = 5,
    ) -> dict:
        """Generate homework assignment."""
        if topic not in settings.TOPICS:
            topic = settings.TOPICS[0]

        templates = HOMEWORK_TEMPLATES.get(
            self.language,
            HOMEWORK_TEMPLATES["en"],
        )

        topic_templates = templates.get(topic, templates["alphabet"])
        exercises = []

        for i in range(min(num_exercises, len(topic_templates))):
            ex = topic_templates[i].copy()
            ex["id"] = f"ex_{i + 1}"
            exercises.append(ex)

        homework = {
            "id": f"hw_{uuid.uuid4().hex[:8]}",
            "student_id": student_id,
            "topic": topic,
            "exercises": exercises,
            "assigned_at": datetime.now().isoformat(),
            "due_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "completed": False,
        }

        logger.info(f"Generated homework {homework['id']} for {student_id}")
        return homework

    def generate_from_performance(
        self,
        student_id: str,
        performance: dict,
    ) -> dict:
        """Generate homework based on student performance."""
        weak_areas = [
            topic
            for topic, data in performance.items()
            if isinstance(data, dict) and data.get("score", 1.0) < 0.6
        ]

        topics = settings.TOPICS
        if weak_areas:
            focus_topic = weak_areas[0]
        elif performance:
            focus_topic = list(performance.keys())[0]
        else:
            focus_topic = topics[0]

        num_exercises = 5
        if weak_areas:
            num_exercises = min(8, 3 * len(weak_areas))

        return self.generate(student_id, focus_topic, num_exercises)

    def get_homework_preview(self, homework: dict) -> str:
        """Get text preview of homework."""
        topic = homework.get("topic", "General")
        num = len(homework.get("exercises", []))
        due = homework.get("due_at", "")

        preview = f"Your homework on {topic}: {num} exercises. Due: {due}"
        return preview


class SimpleHomeworkGenerator(HomeworkGenerator):
    """Enhanced homework generator with templates."""

    def __init__(self):
        super().__init__()
        self.template_dir = settings.DATA_DIR / "homework_templates"

    def _load_custom_templates(self, topic: str) -> list[dict]:
        """Load custom templates for topic."""
        template_file = self.template_dir / f"{topic}_{self.language}.json"

        if template_file.exists():
            try:
                with open(template_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load custom templates: {e}")

        return []


_homework_generator_instance: Optional[HomeworkGenerator] = None


def get_homework_generator() -> HomeworkGenerator:
    """Get global homework generator instance."""
    global _homework_generator_instance
    if _homework_generator_instance is None:
        _homework_generator_instance = HomeworkGenerator()
    return _homework_generator_instance