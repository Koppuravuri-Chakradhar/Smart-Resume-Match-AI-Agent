from __future__ import annotations

import logging
import json
import re
from typing import Dict
from dotenv import load_dotenv
import os
import google.generativeai as genai

from memory.session_state import SessionState
from tools.keyword_extractor import KeywordExtractor

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Dict:
    """Safely extract JSON object from a string response."""
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return {}
        return json.loads(m.group())
    except Exception:
        try:
            return json.loads(text)
        except Exception:
            return {}


class SkillExtractionAgent:
    """Agent that extracts skills and an estimated years_experience from resume text."""

    def __init__(self, session: SessionState, model: str = "models/gemini-2.5-flash") -> None:
        self.session = session
        self.model_name = model
        self.keyword_extractor = KeywordExtractor()
        self.gemini_enabled = API_KEY is not None
        if not self.gemini_enabled:
            logger.warning("GOOGLE_API_KEY not found; SkillExtractionAgent will not call Gemini API.")

    def run(self) -> Dict:
        """Extract skill entities and persist into session."""
        resume_text = self.session.get("resume_text", "")
        if not resume_text:
            raise ValueError("Resume text missing in session state")

        structured = self._call_gemini(resume_text)
        keywords = [kw for kw, _ in self.keyword_extractor.extract(resume_text, max_keywords=40)]

        skill_payload = {
            "skills": structured.get("skills") or keywords,
            "keywords": keywords,
            "years_experience": structured.get("years_experience") or self._estimate_experience(resume_text),
        }

        self.session.set("resume_features", skill_payload)
        logger.info("SkillExtractionAgent extracted %s skills", len(skill_payload["skills"]))
        return skill_payload

    def _call_gemini(self, resume_text: str) -> Dict:
        """Invoke Gemini to identify skill list and experience estimate in JSON form."""
        if not self.gemini_enabled:
            return {}
        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = (
                "Extract structured JSON from this resume. Return fields:\n"
                "  - skills: list of primary technical & domain skills\n"
                "  - years_experience: integer estimate\n\n"
                f"Resume:\n{resume_text}\n\n"
                "Return ONLY valid JSON. Example: {\"skills\": [\"Python\", \"SQL\"], \"years_experience\": 2}"
            )
            response = model.generate_content(prompt)
            raw = response.text or ""
            return _extract_json(raw)
        except Exception as exc:
            logger.error("Gemini parsing failed: %s", exc)
            return {}

    def _estimate_experience(self, resume_text: str) -> int:
        """Simple heuristic to estimate years of experience."""
        text = resume_text.lower()
        # look for patterns like '3 years' or '3 yrs' or '3+ years'
        import re
        m = re.search(r"(\d{1,2})\s*(?:\+)?\s*(?:years|yrs|year)", text)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
        # fallback to counting digit occurrences and using a conservative default
        digits = [int(tok) for tok in re.findall(r"\b(\d{1,2})\b", text) if 0 < int(tok) < 50]
        return max(digits, default=0)
