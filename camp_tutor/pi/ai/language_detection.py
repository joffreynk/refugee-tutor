"""Language detection module."""

import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


LANGUAGE_KEYWORDS = {
    "en": ["hello", "student", "learn", "teach", "yes", "no", "what", "the", "is", "good", "morning", "question", "answer", "help", "please", "thank", "you"],
    "zh": ["你好", "学生", "学习", "教", "是", "不", "什么", "的", "是", "好", "早上", "问题", "答案", "帮助", "请", "谢谢"],
    "hi": ["namaste", "chhatre", "sikhna", "padhna", "haan", "nahin", "kya", "hai", "accha", "subah", "sawal", "javab", "madad", "kripaya", "dhanyavad"],
    "ar": ["marhaba", "talib", "dirasa", "taalim", "na'am", "la", "ma", "huwa", "al", "yawm", "suwal", "jawab", "musaada", "min fadlak", "shukran"],
    "fr": ["bonjour", "étudiant", "apprendre", "enseigner", "oui", "non", "quoi", "le", "est", "bien", "matin", "question", "réponse", "aide", "s'il vous plaît", "merci"],
    "bn": ["namaskar", "chhatro", "shikha", "porano", "hena", "nah", "ki", "ache", "valo", "shupto", "prasno", "uttar", "sahayya", "doya", "dhonnobad"],
    "pt": ["olá", "estudante", "aprender", "ensinar", "sim", "não", "o que", "é", "bom", "manhã", "pergunta", "resposta", "ajuda", "por favor", "obrigado"],
    "ru": ["privet", "student", "uchitsya", "uchit", "da", "net", "chto", "est", "horosho", "utro", "vopros", "otvet", "pomoshch", "pozhaluysta", "spasibo"],
    "id": ["halo", "siswa", "belajar", "ajar", "ya", "tidak", "apa", "ini", "baik", "pagi", "pertanyaan", "jawaban", "bantuan", "tolong", "terima kasih"],
    "ur": ["assalamualaikum", "talib", "parhna", "parhana", "haan", "nahin", "kya", "hai", "accha", "subah", "sawal", "javab", "madad", "kripaya", "shukria"],
    "de": ["hallo", "schüler", "lernen", "lehren", "ja", "nein", "was", "ist", "gut", "morgen", "frage", "antwort", "hilfe", "bitte", "danke"],
    "ja": ["konnichiwa", "gakusei", "manabu", "oshieru", "hai", "iie", "nani", "da", "ii", "asa", "shitsumon", "kaitou", "tasuke", "onegaishimasu", "arigatou"],
    "pcm": ["hello", "student", "learn", "teach", "yes", "no", "wetin", "dey", "good", "morning", "question", "answer", "help", "pls", "thanks"],
    "ar-eg": ["marhaba", "talib", "dirasa", "taalim", "aiwa", "la", "eih", "howa", "al", "yom", "suwal", "gawab", "musaada", "law samaht", "shukran"],
    "mr": ["namaskar", "vidyarthi", "shikna", "shikav", "haan", "nahi", "kay", "ahot", "chOTA", "sang", "prashna", "uttar", "sahayya", "kara", "dhanyavad"],
    "vi": ["xin chao", "hoc sinh", "hoc", "day", "co", "khong", "gi", "la", "tot", "sang", "cau hoi", "tra loi", "giup do", "xin", "cam on"],
    "te": ["namaste", "vidyarthi", "koru", "chevu", "leh", "kadhu", "enti", "undhi", "bagundi", "puvv", "prashnam", "pratipadamu", "samarthyam", "madam", "dhanyavadal"],
    "tr": ["merhaba", "ogrenci", "ogrenmek", "ogretmek", "evet", "hayir", "ne", "bu", "iyi", "sabah", "soru", "cevap", "yardim", "lutfen", "tesekkurler"],
    "yue": ["nei hou", "hoksang", "hok", "gau", "hai", "mhai", "mat", "hai", "hou", "gan", "mangi", "dabui", "gob", "maih", "dor"],
}

LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Mandarin Chinese",
    "hi": "Hindi",
    "ar": "Standard Arabic",
    "fr": "French",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "id": "Indonesian",
    "ur": "Urdu",
    "de": "German",
    "ja": "Japanese",
    "pcm": "Nigerian Pidgin",
    "ar-eg": "Egyptian Arabic",
    "mr": "Marathi",
    "vi": "Vietnamese",
    "te": "Telugu",
    "tr": "Turkish",
    "yue": "Cantonese (Yue)",
}


class LanguageDetector:
    """Detects the learner's language."""

    def __init__(self):
        self.current_language: Optional[str] = None
        self.confidence: float = 0.0

    def detect(self, text: str) -> str:
        """Detect language from text."""
        if not text:
            return "en"

        text_lower = text.lower()
        scores = {}

        for lang, keywords in LANGUAGE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[lang] = score

        if not scores:
            self.current_language = "en"
            self.confidence = 0.5
            return "en"

        detected = max(scores.items(), key=lambda x: x[1])[0]
        max_score = scores[detected]
        total = sum(scores.values())

        self.current_language = detected
        self.confidence = max_score / total if total > 0 else 0.5

        logger.info(f"Detected language: {detected} (confidence: {self.confidence:.2f})")
        return detected

    def detect_from_voice(self, audio_data: bytes) -> str:
        """Detect language from voice input (simplified)."""
        return self.detect("")

    def confirm_language(self, language: str) -> bool:
        """Confirm detected language or set new one."""
        if language in settings.LANGUAGE_CODES:
            self.current_language = language
            self.confidence = 1.0
            return True
        return False

    def get_current_language(self) -> Optional[str]:
        """Get current language."""
        return self.current_language

    def get_confidence(self) -> float:
        """Get detection confidence."""
        return self.confidence

    def is_confident(self) -> bool:
        """Check if confidence is high enough."""
        return self.confidence >= 0.7


_language_detector_instance: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """Get global language detector instance."""
    global _language_detector_instance
    if _language_detector_instance is None:
        _language_detector_instance = LanguageDetector()
    return _language_detector_instance