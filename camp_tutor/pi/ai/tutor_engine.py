"""Tutor engine - core teaching logic with Pearson Edexcel curriculum."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from ai import language_detection, tflite_models, progress_tracker
from audio import text_to_speech
from config import settings

logger = logging.getLogger(__name__)


class CurriculumManager:
    """Manages curriculum content based on Pearson Edexcel standards."""

    def __init__(self):
        self.curriculum = settings.CURRICULUM
        self.age_groups = settings.AGE_GROUPS
        self.subject_list = settings.CURRICULUM_SUBJECTS

    def get_age_group(self, age: int) -> str:
        """Determine age group from student age."""
        for group_key, group_info in self.age_groups.items():
            if group_info["min"] <= age < group_info["max"]:
                return group_key
        return "primary"

    def get_curriculum_content(
        self,
        subject: str,
        age_group: str,
        topic: Optional[str] = None,
    ) -> dict:
        """Get curriculum content for subject and age group."""
        if age_group not in self.curriculum:
            age_group = "primary"
        if subject not in self.curriculum[age_group]:
            subject = "mathematics"

        age_content = self.curriculum[age_group][subject]
        if topic and topic in age_content:
            return age_content[topic]
        return age_content

    def get_topics_for_subject(self, subject: str, age_group: str) -> list[str]:
        """Get all topics for a subject in an age group."""
        if age_group not in self.curriculum:
            return []
        if subject not in self.curriculum[age_group]:
            return []
        return list(self.curriculum[age_group][subject].keys())

    def get_intro_message(self, subject: str, age_group: str, topic: str) -> str:
        """Get introduction message for a topic."""
        content = self.get_curriculum_content(subject, age_group, topic)
        if isinstance(content, dict) and "intro" in content:
            return content["intro"]
        return f"Welcome to {topic}!"

    def get_concepts(self, subject: str, age_group: str, topic: str) -> list:
        """Get concepts for a topic."""
        content = self.get_curriculum_content(subject, age_group, topic)
        if isinstance(content, dict):
            for key in ["concepts", "topics", "contents"]:
                if key in content:
                    return content[key]
        return []


class TutorEngine:
    """Core tutoring engine with curriculum integration."""

    def __init__(self):
        self.current_student_id: Optional[str] = None
        self.current_language: str = "en"
        self.current_subject: str = "mathematics"
        self.current_age_group: str = "primary"
        self.current_topic: str = ""
        self.current_concept_index: int = 0
        self.tts: Optional[text_to_speech.TextToSpeech] = None
        self.session_active: bool = False
        self.curriculum_manager = CurriculumManager()
        self.student_age: int = 10

    def start_session(
        self,
        student_id: str,
        language: str = "en",
        age: int = 10,
    ) -> bool:
        """Start a tutoring session."""
        self.current_student_id = student_id
        self.current_language = language
        self.student_age = age
        self.current_age_group = self.curriculum_manager.get_age_group(age)
        self.session_active = True

        self.tts = text_to_speech.TextToSpeech(language=language)

        logger.info(
            f"Session started for student {student_id}, age {age}, "
            f"group {self.current_age_group}, language {language}"
        )
        return True

    def end_session(self) -> None:
        """End the current session."""
        if self.current_student_id and self.tts:
            self.tts.speak("Goodbye! See you next time! Keep learning!")

        self.session_active = False
        self.current_student_id = None
        logger.info("Session ended")

    def get_greeting(self) -> str:
        """Get greeting message."""
        greetings = [
            "Hello! Welcome to Camp Tutor!",
            "Hi there! Ready to learn?",
            "Hello! Let's explore something new!",
        ]
        import random
        return random.choice(greetings)

    def get_topic_list(self) -> list[str]:
        """Get list of available topics."""
        return self.curriculum_manager.get_topics_for_subject(
            self.current_subject, self.current_age_group
        )

    def get_next_phrase(self) -> Optional[str]:
        """Get next phrase to teach."""
        return self.get_next_concept()

    def speak(self, text: str) -> None:
        """Speak text to student."""
        if self.tts:
            self.tts.speak(text)

    def set_student_age(self, age: int) -> None:
        """Set student age and update age group."""
        self.student_age = age
        self.current_age_group = self.curriculum_manager.get_age_group(age)
        logger.info(f"Student age set to {age}, age group: {self.current_age_group}")

    def teach_subject(self, subject: str) -> str:
        """Start teaching a subject."""
        if subject not in settings.CURRICULUM_SUBJECTS:
            subject = "mathematics"

        self.current_subject = subject
        topics = self.curriculum_manager.get_topics_for_subject(
            subject, self.current_age_group
        )
        if topics:
            self.current_topic = topics[0]
        else:
            self.current_topic = ""

        self.current_concept_index = 0

        intro = self.curriculum_manager.get_intro_message(
            subject, self.current_age_group, self.current_topic
        )
        self.speak(intro)
        return intro

    def teach_topic(self, topic: str) -> str:
        """Start teaching a specific topic."""
        self.current_topic = topic
        self.current_concept_index = 0

        intro = self.curriculum_manager.get_intro_message(
            self.current_subject, self.current_age_group, topic
        )
        self.speak(intro)
        return intro

    def get_next_concept(self) -> Optional[str]:
        """Get next concept in current topic."""
        concepts = self.curriculum_manager.get_concepts(
            self.current_subject, self.current_age_group, self.current_topic
        )

        if not concepts or self.current_concept_index >= len(concepts):
            self._speak_completion()
            return None

        concept = concepts[self.current_concept_index]
        self.current_concept_index += 1

        if isinstance(concept, str):
            self.speak(f"Let's learn about {concept}.")
            return concept
        return str(concept)

    def _speak_completion(self) -> None:
        """Speak completion message."""
        messages = [
            "Great job! You've completed this topic!",
            "Excellent work! Shall we move to another topic?",
            "Well done! Ready for something new?",
        ]
        import random

        self.speak(random.choice(messages))

    def get_subject_list(self) -> list[str]:
        """Get available subjects."""
        return settings.CURRICULUM_SUBJECTS

    def get_age_group_topics(self) -> list[str]:
        """Get topics for current age group."""
        return self.curriculum_manager.get_topics_for_subject(
            self.current_subject, self.current_age_group
        )

    def set_language(self, language: str) -> bool:
        """Set teaching language."""
        if language in settings.LANGUAGE_CODES:
            self.current_language = language
            if self.tts:
                self.tts.set_language(language)
            return True
        return False

    def get_curriculum_summary(self) -> dict:
        """Get summary of available curriculum."""
        summary = {}
        for group_key, group_info in settings.AGE_GROUPS.items():
            summary[group_key] = {
                "name": group_info["name"],
                "subjects": {},
            }
            for subject in settings.CURRICULUM_SUBJECTS:
                topics = self.curriculum_manager.get_topics_for_subject(
                    subject, group_key
                )
                summary[group_key]["subjects"][subject] = topics
        return summary


class AdaptiveTutor(TutorEngine):
    """Tutor with adaptive learning based on age and performance."""

    def __init__(self):
        super().__init__()
        self.progress = progress_tracker.get_progress_tracker()
        self.lang_detector = language_detection.get_language_detector()
        self.recommender = tflite_models.get_recommendation_model()

    def recommend_next_topic(self) -> str:
        """Recommend next topic based on progress."""
        if not self.current_student_id:
            return "mathematics"

        history = self.progress.get_topic_history(self.current_student_id)
        current_level = self.progress.get_level(self.current_student_id)

        topic = self.recommender.recommend_topic(history, current_level)
        return topic or "mathematics"

    def adapt_difficulty(self) -> int:
        """Adapt difficulty based on performance."""
        if not self.current_student_id:
            return 1

        recent = self.progress.get_recent_performance(self.current_student_id)
        if not recent:
            return 1

        correct = recent.get("correct", 0)
        total = recent.get("total", 1)

        classifier = tflite_models.get_difficulty_classifier()
        result = classifier.predict_level(correct, total, 60)
        return result if result is not None else 1

    def generate_adaptive_lesson(self) -> str:
        """Generate lesson adapted to student age and performance."""
        topic = self.recommend_next_topic()
        logger.info(
            f"Generating adaptive lesson: subject={topic}, "
            f"age_group={self.current_age_group}"
        )
        return self.teach_subject(topic)


_tutor_engine_instance: Optional[TutorEngine] = None


def get_tutor_engine() -> TutorEngine:
    """Get global tutor engine instance."""
    global _tutor_engine_instance
    if _tutor_engine_instance is None:
        _tutor_engine_instance = TutorEngine()
    return _tutor_engine_instance


def get_adaptive_tutor() -> AdaptiveTutor:
    """Get adaptive tutor instance."""
    return AdaptiveTutor()


def get_curriculum_manager() -> CurriculumManager:
    """Get curriculum manager instance."""
    return CurriculumManager()