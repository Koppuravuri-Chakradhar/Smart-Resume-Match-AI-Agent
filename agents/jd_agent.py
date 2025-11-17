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
    """Safely extract first JSON object from a string; return {} if none found or parse fails."""
    try:
        # find first {...} block
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return {}
        return json.loads(m.group())
    except Exception:
        try:
            # as a fallback try to load the whole text
            return json.loads(text)
        except Exception:
            return {}


class JobDescriptionAgent:
    """Agent that processes job descriptions via Gemini and keyword extraction."""

    def __init__(self, session: SessionState, model: str = "models/gemini-2.5-flash") -> None:
        self.session = session
        self.model_name = model
        self.keyword_extractor = KeywordExtractor()
        self.gemini_enabled = API_KEY is not None
        if not self.gemini_enabled:
            logger.warning("GOOGLE_API_KEY not found; JD Agent will not call Gemini API.")

    def run(self, jd_text: str) -> Dict:
        """Analyze JD and persist extracted features."""
        structured = self._call_gemini(jd_text)
        # fallback to keyword extractor when model doesn't return skills
        keywords = [kw for kw, _ in self.keyword_extractor.extract(jd_text, max_keywords=40)]
        payload = {
            "skills": structured.get("skills", keywords),
            "keywords": keywords,
            "years_experience": structured.get("years_experience", 0),
            "summary": structured.get("summary", jd_text[:400]),
        }
        self.session.set("jd_features", payload)
        logger.info("JobDescriptionAgent captured %s skills", len(payload["skills"]))
        return payload

    def _call_gemini(self, jd_text: str) -> Dict:
        """Call Gemini for structured JD data (skills, years_experience, summary)."""
        if not self.gemini_enabled:
            return {}
        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = (
                "Extract structured JSON from this job description. Return an object with fields:\n"
                "  - skills: list of skills/keywords\n"
                "  - years_experience: integer (estimated)\n"
                "  - summary: short 1-2 sentence description\n\n"
                f"Job Description:\n{jd_text}\n\n"
                "Return ONLY valid JSON. Example: {\"skills\": [...], \"years_experience\": 2, \"summary\": \"...\"}"
            )
            response = model.generate_content(prompt)
            raw = response.text or ""
            return _extract_json(raw)
        except Exception as exc:
            logger.error("Gemini JD parsing failed: %s", exc)
            return {}
