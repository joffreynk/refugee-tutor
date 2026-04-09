"""TensorFlow Lite model wrapper for Camp Tutor."""

import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

try:
    import tflite_runtime.interpreter as tflite
    HAS_TFLITE = True
except ImportError:
    try:
        import tensorflow as tflite
        HAS_TFLITE = True
    except ImportError:
        HAS_TFLITE = False

from config import settings

logger = logging.getLogger(__name__)


class TFLiteModel:
    """Wrapper for TensorFlow Lite models."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path
        self.interpreter: Optional[Any] = None
        self.input_index: Optional[int] = None
        self.output_index: Optional[int] = None
        self._loaded = False

    def load(self, model_path: Optional[Path] = None) -> bool:
        """Load the TFLite model."""
        if not HAS_TFLITE:
            logger.warning("TensorFlow Lite not available")
            return False

        path = model_path or self.model_path
        if not path:
            logger.error("No model path specified")
            return False

        try:
            self.interpreter = tflite.Interpreter(str(path))
            self.interpreter.allocate_tensors()

            self.input_index = self.interpreter.get_input_details()[0]["index"]
            self.output_index = self.interpreter.get_output_details()[0]["index"]

            self._loaded = True
            self.model_path = path
            logger.info(f"Loaded model: {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def predict(self, input_data: np.ndarray) -> Optional[np.ndarray]:
        """Run inference."""
        if not self._loaded or not self.interpreter:
            return None

        try:
            self.interpreter.set_tensor(self.input_index, input_data)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_index)
            return output
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return None

    def predict_class(self, input_data: np.ndarray) -> Optional[int]:
        """Get predicted class."""
        output = self.predict(input_data)
        if output is None:
            return None
        return int(np.argmax(output))

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded


class LanguageClassifier(TFLiteModel):
    """Language classification model."""

    def __init__(self, model_path: Optional[Path] = None):
        super().__init__(model_path)
        self.languages = settings.LANGUAGE_CODES

    def predict_language(self, text: str) -> Optional[str]:
        """Predict language from text (simplified feature extraction)."""
        if not self.is_loaded():
            return None

        features = self._extract_features(text)
        input_data = np.array([features], dtype=np.float32)

        result = self.predict(input_data)
        if result is None:
            return None

        idx = int(np.argmax(result))
        return self.languages[idx] if idx < len(self.languages) else None

    def _extract_features(self, text: str) -> list[float]:
        """Extract simple features from text."""
        features = []
        text_lower = text.lower()

        for lang in settings.LANGUAGE_CODES:
            keywords = {
                "en": ["the", "is", "are", "a", "an"],
                "fr": ["le", "la", "est", "sont", "un"],
                "es": ["el", "la", "es", "son", "un"],
                "de": ["der", "die", "ist", "sind", "ein"],
                "zh": ["的", "是", "在", "有"],
            }
            count = sum(1 for kw in keywords.get(lang, []) if kw in text_lower)
            features.append(count / max(len(text), 1))

        while len(features) < 10:
            features.append(0.0)

        return features[:10]


class DifficultyClassifier(TFLiteModel):
    """Student difficulty level classifier."""

    def __init__(self, model_path: Optional[Path] = None):
        super().__init__(model_path)
        self.num_levels = settings.DIFFICULTY_LEVELS

    def predict_level(
        self,
        correct_count: int,
        total_count: int,
        time_seconds: int,
    ) -> Optional[int]:
        """Predict appropriate difficulty level."""
        if not self.is_loaded():
            return self._fallback_level(correct_count, total_count)

        accuracy = correct_count / max(total_count, 1)
        features = [accuracy, total_count / 100.0, time_seconds / 3600.0]

        input_data = np.array([features], dtype=np.float32)
        result = self.predict(input_data)

        if result is None:
            return self._fallback_level(correct_count, total_count)

        level = int(np.argmax(result)) + 1
        return min(max(level, 1), self.num_levels)

    def _fallback_level(self, correct: int, total: int) -> int:
        """Fallback level calculation."""
        if total == 0:
            return 1
        accuracy = correct / total
        if accuracy >= 0.9:
            return min(10, max(5, int(accuracy * 10)))
        return max(1, int(accuracy * 5))


class RecommendationModel(TFLiteModel):
    """Topic recommendation model."""

    def __init__(self, model_path: Optional[Path] = None):
        super().__init__(model_path)
        self.topics = settings.TOPICS

    def recommend_topic(
        self,
        student_history: dict,
        current_level: int,
    ) -> Optional[str]:
        """Recommend next topic."""
        if not self.is_loaded():
            return self._fallback_recommend(student_history, current_level)

        features = self._extract_history_features(student_history, current_level)
        input_data = np.array([features], dtype=np.float32)

        result = self.predict(input_data)
        if result is None:
            return self._fallback_recommend(student_history, current_level)

        idx = int(np.argmax(result))
        return self.topics[idx] if idx < len(self.topics) else self.topics[0]

    def _extract_history_features(
        self,
        history: dict,
        level: int,
    ) -> list[float]:
        """Extract history features."""
        features = [level / 10.0]

        for topic in self.topics:
            score = history.get(topic, {}).get("score", 0.5)
            features.append(score)

        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    def _fallback_recommend(
        self,
        history: dict,
        current_level: int,
    ) -> str:
        """Fallback recommendation."""
        weak_topics = [
            t for t in self.topics
            if history.get(t, {}).get("score", 1.0) < 0.6
        ]

        if weak_topics:
            return weak_topics[0]

        for topic in self.topics:
            if topic not in history:
                return topic

        return self.topics[0]


_language_classifier_instance: Optional[LanguageClassifier] = None
_difficulty_classifier_instance: Optional[DifficultyClassifier] = None
_recommendation_model_instance: Optional[RecommendationModel] = None


def get_language_classifier() -> LanguageClassifier:
    """Get language classifier instance."""
    global _language_classifier_instance
    if _language_classifier_instance is None:
        _language_classifier_instance = LanguageClassifier()
    return _language_classifier_instance


def get_difficulty_classifier() -> DifficultyClassifier:
    """Get difficulty classifier instance."""
    global _difficulty_classifier_instance
    if _difficulty_classifier_instance is None:
        _difficulty_classifier_instance = DifficultyClassifier()
    return _difficulty_classifier_instance


def get_recommendation_model() -> RecommendationModel:
    """Get recommendation model instance."""
    global _recommendation_model_instance
    if _recommendation_model_instance is None:
        _recommendation_model_instance = RecommendationModel()
    return _recommendation_model_instance