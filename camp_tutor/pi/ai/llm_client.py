"""LLM client for answering student questions using OpenAI-compatible API."""

import logging
import json
import os
import requests
from typing import Optional, Dict
from config import settings

logger = logging.getLogger(__name__)

CURRICULUM_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "computing_year7.json")


class LLMClient:
    """Client for LLM API to answer student questions."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.api_url = settings.LLM_API_URL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.conversation_history = []
        self.current_topic = ""
        self.current_subject = ""
        self._curriculum_cache = None
        self._current_lesson_info = ""

    def load_curriculum(self) -> Dict:
        if self._curriculum_cache is not None:
            return self._curriculum_cache
        try:
            if os.path.exists(CURRICULUM_FILE):
                with open(CURRICULUM_FILE, 'r') as f:
                    self._curriculum_cache = json.load(f)
                    logger.info("Curriculum loaded")
                    return self._curriculum_cache
        except Exception as e:
            logger.warning(f"Could not load curriculum: {e}")
        return {}

    def set_topic(self, topic: str, subject: str) -> None:
        self.current_topic = topic
        self.current_subject = subject

    def set_lesson(self, topic_index: int, subtopic_index: int) -> None:
        self._update_lesson_info()

    def _update_lesson_info(self) -> None:
        self._current_lesson_info = ""
        try:
            curriculum = self.load_curriculum()
            topics = curriculum.get("topics", [])
            for topic in topics:
                subtopics = topic.get("subtopics", [])
                for st in subtopics:
                    script = st.get("teaching_script", {})
                    key_terms = script.get("key_terms_list", [])
                    if key_terms:
                        for t in key_terms:
                            self._current_lesson_info += f"{t['term']}: {t['definition']}. "
        except Exception:
            pass

    def _get_relevant_content(self, question: str) -> str:
        """Find relevant curriculum by keyword matching."""
        q_lower = question.lower()
        curriculum = self.load_curriculum()
        topics = curriculum.get("topics", [])
        
        matches = []
        for topic in topics:
            for st in topic.get("subtopics", []):
                name = st.get("name", "").lower()
                desc = st.get("description", "").lower()
                script = st.get("teaching_script", {})
                terms = script.get("key_terms_list", [])
                term_names = " ".join([t.get("term", "").lower() for t in terms])
                
                score = sum(1 for w in q_lower.split() if len(w) > 2 and (w in name or w in desc or w in term_names))
                if score > 0:
                    term_list = ", ".join([t.get("term", "") for t in terms])
                    matches.append(f"{st.get('name')}: {term_list}")
        
        if not matches:
            for topic in topics[:2]:
                for st in topic.get("subtopics", [])[:1]:
                    terms = st.get("teaching_script", {}).get("key_terms_list", [])
                    term_list = ", ".join([t.get("term", "") for t in terms])
                    matches.append(f"{st.get('name')}: {term_list}")
        
        return " | ".join(matches[:6])

    def _generate_hints(self, question: str) -> str:
        """Map question keywords to curriculum hints."""
        q = question.lower()
        hints = {
            "computer": "hardware software input output",
            "hardware": "monitor keyboard mouse CPU memory",
            "software": "programs apps operating system",
            "input": "keyboard mouse microphone",
            "output": "monitor speaker printer",
            "file": "folder directory save",
            "folder": "directory organize files",
            "mouse": "click double click drag",
            "keyboard": "typing keys",
            "monitor": "screen display",
            "cpu": "processor brain",
            "memory": "RAM storage",
            "binary": "0 1 computer numbers",
            "internet": "network wifi",
            "windows": "operating system",
            "operating system": "windows mac linux",
        }
        found = [hints[k] for k in hints if k in q]
        return " ".join(found) if found else ""

    def is_available(self) -> bool:
        return bool(self.api_key)

    def answer_question(self, question: str) -> Optional[str]:
        if not self.is_available():
            return None
        try:
            prompt = self._build_prompt(question)
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Student asks: {question}"}
            ]
            response = self._call_api(messages)
            if response:
                return response
        except Exception as e:
            logger.error(f"LLM error: {e}")
        return None

    def _build_prompt(self, question: str) -> str:
        curriculum = self._get_relevant_content(question)
        hints = self._generate_hints(question)
        terms = self._current_lesson_info
        
        return f"""You are Camp Tutor, a teaching robot for Year 7 Computing students.
Student asks: {question}
Use these KEY TERMS from lesson: {terms}
Related topics: {curriculum}
Hint keywords: {hints}
Answer in 1-2 sentences. Use the key term definitions from the curriculum."""

    def _call_api(self, messages: list) -> Optional[str]:
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            logger.warning(f"API error: {resp.status_code}")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
        return None

    def clear_history(self) -> None:
        self.conversation_history = []


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client