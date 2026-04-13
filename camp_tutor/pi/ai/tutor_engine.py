"""Tutor engine - core teaching logic with Pearson Edexcel curriculum."""

import logging
import random
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
        self._current_subtopic_index: int = 0
        self._current_lesson_part: str = "hook"
        self._current_section_index: int = 0
        self._teach_counter: int = 0
        self._pearson_curriculum = settings.PEARSON_CURRICULUM

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

    def deliver_pearson_lesson(self, listen_for_answers: bool = True) -> Optional[dict]:
        """Deliver interactive Pearson Edexcel lesson:
        - 20 min: Teach 4 min, then listen 10 sec for questions, repeat
        - 30 min: Student Q&A
        - 15 min: Quiz
        - 15 min: Feedback
        Total: 80 minutes
        """
        subtopics = self._get_pearson_subtopics()
        if not subtopics or self._current_subtopic_index >= len(subtopics):
            return None
        
        subtopic = subtopics[self._current_subtopic_index]
        sections = subtopic.get("sections", [])
        
        if not sections:
            return None
        
        if self._current_lesson_part == "hook":
            hook = subtopic.get("hook", "")
            self._target_teach_time = 20 * 60
            self._teach_time = 0
            self.speak(f"Welcome to your {subtopic.get('name', 'lesson')}! This lesson lasts 80 minutes total. I'll teach for 4 minutes, then pause 10 seconds for questions. Then 30 minutes for your questions, 15 minutes quiz, and 15 minutes feedback. Let's begin! {hook}")
            self._current_lesson_part = "teach"
            self._teach_counter = 0
            return {"part": "hook", "phase": "intro", "duration_min": 2}
        
        elif self._current_lesson_part == "teach":
            self._target_teach_time = getattr(self, '_target_teach_time', 80 * 60)
            
            self.speak("TEACHING - 4 minutes. Listen carefully!")
            
            sections = self._get_curriculum_sections()
            for section in sections:
                if self._teach_time >= self._target_teach_time:
                    break
                title = section.get("title", "")
                content = section.get("content", "")
                self.speak(f"Let's learn about {title}. {content}")
                self._teach_time += 120
            
            self._current_lesson_part = "listen_q"
            return {"part": "teach", "phase": "teaching", "duration_min": 4, "action": "teaching", "total_teach_time": self._teach_time}
        
        elif self._current_lesson_part == "listen_q":
            self.speak("I finished teaching for now. This is your time to ask questions! You have 60 seconds - speak up now if you have a question!")
            
            question = self._listen_for_student_question_timeout(60)
            
            if question and len(question) > 2:
                self.speak("I hear you! Tell me your question, and say 'that's my question thanks' when finished.")
                full_question = self._listen_until_thanks()
                
                if full_question and len(full_question) > 2:
                    guidance = self._provide_guidance(full_question)
                    self.speak(f"That's a great question! {guidance}")
                else:
                    self.speak("I didn't catch your question. That's okay, ask next time!")
            else:
                self.speak("No questions? Let's continue!")
            
            if self._teach_time >= self._target_teach_time:
                self._current_lesson_part = "questions"
                return {"part": "teach_done", "phase": "teaching_complete", "duration_min": 80}
            else:
                self._current_lesson_part = "teach"
                return {"part": "listen_done", "phase": "listening", "action": "listened", "continue_teaching": True}
        
        elif self._current_lesson_part == "questions":
            self.speak("PHASE 2: YOUR QUESTIONS - 30 minutes. Ask me anything!")
            
            for _ in range(6):
                answer = self._listen_for_student_question()
                if answer and len(answer) > 2:
                    guidance = self._provide_guidance(answer)
                    self.speak(f"Great question! {guidance}")
            
            self._current_lesson_part = "quiz"
            return {"part": "questions", "phase": "qa", "duration_min": 30}
        
        elif self._current_lesson_part == "quiz":
            self.speak("PHASE 3: QUIZ - 15 minutes!")
            
            all_quiz = []
            for section in sections:
                all_quiz.extend(section.get("quiz", []))
            
            if all_quiz:
                responses = self._ask_and_listen_quiz(all_quiz)
                self.speak(responses)
            
            self._current_lesson_part = "feedback"
            return {"part": "quiz", "phase": "quiz", "duration_min": 15}
        
        elif self._current_lesson_part == "feedback":
            self.speak("PHASE 4: FEEDBACK. Great work today! Keep learning!")
            self._current_lesson_part = "complete"
            return {"part": "feedback", "phase": "feedback", "duration_min": 15}
        
        elif self._current_lesson_part == "complete":
            self.speak("Excellent! Lesson complete! See you next time!")
            self._current_lesson_part = "hook"
            self._current_subtopic_index += 1
            return {"part": "complete", "duration_min": 2}
        
        return None
    
    def _listen_for_student_question_timeout(self, timeout_sec: int = 10) -> str:
        """Listen for student question with timeout."""
        from audio import speech_to_text
        stt = speech_to_text.SpeechToText()
        try:
            return stt.listen(timeout=float(timeout_sec)) or ""
        except Exception:
            return ""
    
    def _listen_until_thanks(self) -> str:
        """Keep listening until student says 'that's my question thanks'."""
        from audio import speech_to_text
        stt = speech_to_text.SpeechToText()
        
        full_question = ""
        self.speak("I'm listening...")
        
        for _ in range(15):
            try:
                answer = stt.listen(timeout=5.0)
                if answer:
                    answer_lower = answer.lower()
                    full_question += " " + answer
                    if "thanks" in answer_lower or "done" in answer_lower or "that's it" in answer_lower:
                        break
            except Exception:
                break
        
        return full_question.strip()
    
    def _listen_for_student_question(self) -> str:
        """Listen for student questions during Q&A phase."""
        if not self.tts:
            return ""
        
        from audio import speech_to_text
        stt = speech_to_text.SpeechToText()
        
        self.speak("What's your question?")
        try:
            answer = stt.listen(timeout=10.0)
            return answer or ""
        except Exception:
            return ""
    
    def _provide_guidance(self, question: str) -> str:
        """Provide interactive guidance based on student question."""
        try:
            from ai.llm_client import get_llm_client
            llm = get_llm_client()
            llm.set_topic(self.current_topic, self.current_subject)
            llm.set_lesson(self._current_subtopic_index, self._current_section_index)
            if llm.is_available():
                answer = llm.answer_question(question)
                if answer:
                    return answer
        except Exception as e:
            logger.warning(f"LLM not available: {e}")
        
        keywords = question.lower()
        
        if any(k in keywords for k in ["cpu", "processor", "brain"]):
            return "The CPU is the central processing unit - think of it as the brain of the computer. It fetches instructions, decodes them, and executes them billions of times per second!"
        elif any(k in keywords for k in ["memory", "ram", "storage"]):
            return "RAM is like your short-term memory - it's fast but temporary. Storage is like a bookshelf - slower but keeps things permanently."
        elif any(k in keywords for k in ["binary", "0", "1", "number"]):
            return "Computers use binary because electricity is either on or off. ON is 1, OFF is 0. That's it - just two digits, but combined they create everything!"
        elif any(k in keywords for k in ["network", "internet", "wifi"]):
            return "Networks connect computers together like a web. Your home router is the gateway to the internet - data packets travel through many computers to reach their destination."
        else:
            return "That's an interesting question! The best way to learn is to keep exploring and experimenting with code. Don't be afraid to make mistakes - that's how we learn!"
    
    def _ask_and_listen_quiz(self, questions: list) -> str:
        """Ask quiz questions and listen for student answers."""
        if not self.tts:
            return ""
        
        from audio import speech_to_text
        stt = speech_to_text.SpeechToText()
        
        responses = []
        for i, question in enumerate(questions[:5], 1):
            self.speak(f"Question {i}: {question}. Take a moment to think, then answer.")
            
            try:
                answer = stt.listen(timeout=15.0)
                if answer:
                    responses.append(f"Question {i}: You answered: {answer}. ")
                    if len(answer) > 3:
                        responses.append("Excellent thinking! ")
                    else:
                        responses.append("Try to explain a bit more next time! ")
                else:
                    responses.append(f"Question {i}: No answer received. ")
            except Exception:
                responses.append(f"Question {i}: Let's move on. ")
        
        responses.append("Great effort on the quiz! Remember, every attempt helps you learn.")
        return " ".join(responses)

    def _get_pearson_subtopics(self) -> list:
        """Get subtopics using new COMPREHENSIVE_CURRICULUM."""
        try:
            curriculum = settings.COMPREHENSIVE_CURRICULUM.get(self.current_age_group, {}).get(self.current_subject, {})
            topics_list = curriculum.get("topics", [])
            if topics_list and self._current_subtopic_index < len(topics_list):
                topic = topics_list[self._current_subtopic_index]
                return [{"name": topic.get("name", ""), "subtopics": topic.get("subtopics", [])}]
            return []
        except Exception as e:
            logger.warning(f"Could not get subtopics: {e}")
            return []
    
    def _get_curriculum_sections(self) -> list:
        """Get sections from comprehensive curriculum."""
        try:
            curriculum = settings.COMPREHENSIVE_CURRICULUM.get(self.current_age_group, {}).get(self.current_subject, {})
            topics_list = curriculum.get("topics", [])
            if topics_list and self._current_subtopic_index < len(topics_list):
                topic = topics_list[self._current_subtopic_index]
                subtopics = topic.get("subtopics", [])
                return [{"title": s.title(), "content": f"Learning about {s}. This is an important concept in {self.current_subject}."} for s in subtopics]
            return []
        except Exception as e:
            logger.warning(f"Could not get sections: {e}")
            return []

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