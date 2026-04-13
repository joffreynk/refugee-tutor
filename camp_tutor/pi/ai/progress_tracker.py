"""Progress tracker module."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks student learning progress over time."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATA_DIR / "progress.json"
        self.progress_data: dict = {}
        self._load()

    def _load(self) -> None:
        """Load progress data from file."""
        if self.db_path.exists():
            try:
                with open(self.db_path) as f:
                    self.progress_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress data: {e}")
                self.progress_data = {}

    def _save(self) -> None:
        """Save progress data to file."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress data: {e}")

    def record_answer(
        self,
        student_id: str,
        topic: str,
        correct: bool,
    ) -> None:
        """Record a student's answer."""
        if student_id not in self.progress_data:
            self.progress_data[student_id] = {
                "topics": {},
                "total_correct": 0,
                "total_answers": 0,
            }

        student_data = self.progress_data[student_id]

        if topic not in student_data["topics"]:
            student_data["topics"][topic] = {
                "correct": 0,
                "total": 0,
                "history": [],
            }

        topic_data = student_data["topics"][topic]
        topic_data["total"] += 1

        if correct:
            topic_data["correct"] += 1
            student_data["total_correct"] += 1

        topic_data["history"].append({
            "correct": correct,
            "timestamp": datetime.now().isoformat(),
        })
        
        if len(topic_data["history"]) > settings.MAX_HISTORY:
            topic_data["history"] = topic_data["history"][-settings.MAX_HISTORY:]

        student_data["total_answers"] += 1

        self._save()
        logger.debug(f"Recorded answer: {student_id}/{topic} = {correct}")

    def get_topic_score(self, student_id: str, topic: str) -> float:
        """Get score for a topic."""
        if student_id not in self.progress_data:
            return 0.5

        topics = self.progress_data[student_id].get("topics", {})
        if topic not in topics:
            return 0.5

        topic_data = topics[topic]
        total = topic_data.get("total", 0)

        if total == 0:
            return 0.5

        correct = topic_data.get("correct", 0)
        return correct / total

    def get_overall_score(self, student_id: str) -> float:
        """Get overall score."""
        if student_id not in self.progress_data:
            return 0.5

        student_data = self.progress_data[student_id]
        total = student_data.get("total_answers", 0)

        if total == 0:
            return 0.5

        correct = student_data.get("total_correct", 0)
        return correct / total

    def get_topic_history(self, student_id: str) -> dict:
        """Get topic scores for recommendation."""
        if student_id not in self.progress_data:
            return {}

        topics = self.progress_data[student_id].get("topics", {})
        return {
            topic: {"score": self.get_topic_score(student_id, topic)}
            for topic in topics
        }

    def get_recent_performance(self, student_id: str, num_recent: int = 10) -> dict:
        """Get recent performance metrics."""
        if student_id not in self.progress_data:
            return {}

        topics = self.progress_data[student_id].get("topics", {})

        recent_correct = 0
        recent_total = 0

        for topic, topic_data in topics.items():
            history = topic_data.get("history", [])
            for entry in history[-num_recent:]:
                recent_total += 1
                if entry.get("correct"):
                    recent_correct += 1

        return {
            "correct": recent_correct,
            "total": recent_total,
            "accuracy": recent_correct / recent_total if recent_total > 0 else 0.5,
        }

    def get_level(self, student_id: str) -> int:
        """Get student level (1-10)."""
        score = self.get_overall_score(student_id)

        level = int(score * 10)
        return max(1, min(10, level))

    def update_streak(self, student_id: str) -> None:
        """Update daily streak."""
        if student_id not in self.progress_data:
            self.progress_data[student_id] = {
                "topics": {},
                "total_correct": 0,
                "total_answers": 0,
                "last_active": None,
                "streak": 0,
            }

        student_data = self.progress_data[student_id]
        today = datetime.now().date().isoformat()

        last_active = student_data.get("last_active")

        if last_active == today:
            return

        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()

        if last_active == yesterday:
            student_data["streak"] = student_data.get("streak", 0) + 1
        else:
            student_data["streak"] = 1

        student_data["last_active"] = today
        self._save()

    def get_streak(self, student_id: str) -> int:
        """Get current streak."""
        if student_id not in self.progress_data:
            return 0
        return self.progress_data[student_id].get("streak", 0)

    def needs_remedial(self, student_id: str, topic: str) -> bool:
        """Check if student needs remedial help."""
        score = self.get_topic_score(student_id, topic)
        return score < 0.6


_progress_tracker_instance: Optional[ProgressTracker] = None


def get_progress_tracker() -> ProgressTracker:
    """Get global progress tracker instance."""
    global _progress_tracker_instance
    if _progress_tracker_instance is None:
        _progress_tracker_instance = ProgressTracker()
    return _progress_tracker_instance