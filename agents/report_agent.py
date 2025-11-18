from __future__ import annotations

import logging
import json
from typing import Dict
from dotenv import load_dotenv
import os
import google.generativeai as genai

from memory.session_state import SessionState
from tools.scoring_engine import MatchBreakdown

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

logger = logging.getLogger(__name__)

def _extract_text(response) -> str:
    """Safely return response text."""
    try:
        return response.text or ""
    except Exception:
        return ""

class ReportAgent:
    """Agent that generates a clean, emoji-rich HR report without repeating ATS breakdown."""

    def __init__(self, session: SessionState, model: str = "models/gemini-2.5-flash") -> None:
        self.session = session
        self.model_name = model
        self.gemini_enabled = API_KEY is not None

    def run(self) -> Dict[str, str]:
        resume_features = self.session.get("resume_features", {})
        jd_features = self.session.get("jd_features", {})
        breakdown: MatchBreakdown = self.session.get("score_breakdown")

        narrative = self._generate_narrative(resume_features, jd_features, breakdown)

        report = {
            "summary": narrative,
            "skill_gap": self._derive_skill_gap(resume_features, jd_features),
        }
        self.session.set("report", report)
        return report

    def _generate_narrative(self, resume: Dict, jd: Dict, breakdown: MatchBreakdown | None) -> str:
        fallback = (
            f"Resume matches job at {breakdown.total if breakdown else 0:.2f}%. "
            "Review missing skills to improve alignment."
        )

        if not self.gemini_enabled:
            return fallback

        try:
            model = genai.GenerativeModel(self.model_name)

            prompt = f"""
You are an expert HR recruiter. Generate a clean, professional evaluation in Markdown with emojis.

DO NOT repeat ATS Score Breakdown because UI already shows it.

FORMAT EXACTLY:

📄 **Summary**
<3–5 sentence summary>

🎯 **Strengths**
- point
- point

⚠️ **Weaknesses**
- point
- point

🥇 **Fit Rating**
{breakdown.fit_rating if breakdown else "N/A"}

🛠️ **Improvement Suggestions**
1. suggestion
2. suggestion
3. suggestion

❌ **Missing Skills**
(Just list missing skills)

Inputs:
Resume Skills: {resume.get('skills', [])}
Job Skills: {jd.get('skills', [])}
"""

            response = model.generate_content(prompt)
            return _extract_text(response).strip() or fallback

        except Exception as exc:
            logger.error("Gemini error: %s", exc)
            return fallback

    def _derive_skill_gap(self, resume: Dict, jd: Dict) -> str:
        resume_skills = {s.lower() for s in resume.get("skills", [])}
        missing = [s for s in jd.get("skills", []) if s.lower() not in resume_skills]
        return ", ".join(sorted(set(missing))) or "No significant gaps identified."
