"""Assessment engine for quizzes and tests."""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


QUIZ_QUESTIONS = {
    "en": {
        "alphabet": [
            {"q": "What letter comes after A?", "a": "B", "options": ["B", "C", "D"]},
            {"q": "What letter is this?", "a": "C", "options": ["A", "B", "C"]},
            {"q": "How many letters are in the alphabet?", "a": "26", "options": ["24", "25", "26"]},
        ],
        "numbers": [
            {"q": "What number comes after 5?", "a": "6", "options": ["5", "6", "7"]},
            {"q": "What is 2 + 2?", "a": "4", "options": ["3", "4", "5"]},
            {"q": "Count: 1, 2, 3...?", "a": "4", "options": ["3", "4", "5"]},
        ],
        "colors": [
            {"q": "What color is the sky?", "a": "blue", "options": ["blue", "green", "red"]},
            {"q": "What color do you get mixing red and blue?", "a": "purple", "options": ["purple", "orange", "green"]},
            {"q": "Is grass green or red?", "a": "green", "options": ["green", "red", "blue"]},
        ],
    },
    "fr": {
        "alphabet": [
            {"q": "Quelle lettre vient après A?", "a": "B", "options": ["B", "C", "D"]},
            {"q": "Combien de lettres dans l'alphabet?", "a": "26", "options": ["24", "25", "26"]},
        ],
        "numbers": [
            {"q": "Quel nombre vient après 5?", "a": "6", "options": ["5", "6", "7"]},
            {"q": "Quanto fait 2 + 2?", "a": "4", "options": ["3", "4", "5"]},
        ],
    },
}


class AssessmentEngine:
    """Manages quizzes and assessments."""

    def __init__(self):
        self.language = "en"
        self.current_assessment: Optional[dict] = None

    def set_language(self, language: str) -> None:
        """Set assessment language."""
        if language in settings.LANGUAGE_CODES:
            self.language = language

    def create_quiz(
        self,
        topic: str,
        num_questions: int = 5,
    ) -> dict:
        """Create a new quiz."""
        if topic not in settings.TOPICS:
            topic = settings.TOPICS[0]

        questions_db = QUIZ_QUESTIONS.get(
            self.language,
            QUIZ_QUESTIONS["en"],
        )

        topic_questions = questions_db.get(topic, [])

        if not topic_questions:
            topic_questions = questions_db["alphabet"]

        questions = topic_questions[: min(num_questions, len(topic_questions))]

        for q in questions:
            q["id"] = f"q_{uuid.uuid4().hex[:6]}"

        assessment = {
            "id": f"assess_{uuid.uuid4().hex[:8]}",
            "topic": topic,
            "questions": questions,
            "started_at": datetime.now().isoformat(),
            "completed": False,
            "answers": {},
            "score": 0,
        }

        self.current_assessment = assessment
        logger.info(f"Created assessment {assessment['id']} for topic {topic}")

        return assessment

    def get_question(self, index: int = 0) -> Optional[dict]:
        """Get question by index."""
        if not self.current_assessment:
            return None

        questions = self.current_assessment.get("questions", [])
        if 0 <= index < len(questions):
            return questions[index]
        return None

    def submit_answer(
        self,
        question_id: str,
        answer: str,
    ) -> bool:
        """Submit answer and check if correct."""
        if not self.current_assessment:
            return False

        questions = self.current_assessment.get("questions", [])

        for q in questions:
            if q.get("id") == question_id:
                correct = q.get("a", "").lower() == answer.lower()

                self.current_assessment["answers"][question_id] = {
                    "answer": answer,
                    "correct": correct,
                }

                if correct:
                    self.current_assessment["score"] = (
                        self.current_assessment.get("score", 0) + 1
                    )

                return correct

        return False

    def complete_assessment(self) -> dict:
        """Complete assessment and get results."""
        if not self.current_assessment:
            return {}

        questions = self.current_assessment.get("questions", [])
        answers = self.current_assessment.get("answers", {})
        score = self.current_assessment.get("score", 0)

        total = len(questions)
        percentage = (score / total * 100) if total > 0 else 0

        results = {
            "assessment_id": self.current_assessment["id"],
            "topic": self.current_assessment["topic"],
            "score": score,
            "total": total,
            "percentage": percentage,
            "completed_at": datetime.now().isoformat(),
            "passed": percentage >= 70,
        }

        self.current_assessment["completed"] = True
        logger.info(f"Assessment complete: {score}/{total} ({percentage:.0f}%)")

        return results

    def get_current_assessment(self) -> Optional[dict]:
        """Get current assessment state."""
        return self.current_assessment

    def reset(self) -> None:
        """Reset current assessment."""
        self.current_assessment = None


class OralAssessment(AssessmentEngine):
    """Assessment using voice responses."""

    def __init__(self):
        super().__init__()

    def create_oral_quiz(
        self,
        topic: str,
        num_questions: int = 5,
    ) -> dict:
        """Create voice-based quiz."""
        quiz = self.create_quiz(topic, num_questions)

        for q in quiz.get("questions", []):
            q["type"] = "oral"

        return quiz


_assessment_engine_instance: Optional[AssessmentEngine] = None


def get_assessment_engine() -> AssessmentEngine:
    """Get global assessment engine instance."""
    global _assessment_engine_instance
    if _assessment_engine_instance is None:
        _assessment_engine_instance = AssessmentEngine()
    return _assessment_engine_instance