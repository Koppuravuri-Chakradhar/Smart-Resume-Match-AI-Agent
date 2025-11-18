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
    """Safely return response text if available."""
    try:
        return response.text or ""
    except Exception:
        return ""


class ReportAgent:
    """Agent that synthesizes a premium HR-style narrative using Gemini."""

    def __init__(self, session: SessionState, model: str = "models/gemini-2.5-flash") -> None:
        self.session = session
        self.model_name = model
        self.gemini_enabled = API_KEY is not None
        if not self.gemini_enabled:
            logger.warning("GOOGLE_API_KEY not found; ReportAgent will fallback.")

    def run(self) -> Dict[str, str]:
        """Return structured report dictionary saved to session."""
        resume_features = self.session.get("resume_features", {})
        jd_features = self.session.get("jd_features", {})
        breakdown: MatchBreakdown = self.session.get("score_breakdown")

        narrative = self._generate_narrative(resume_features, jd_features, breakdown)

        report = {
            "summary": narrative,
            "skill_gap": self._derive_skill_gap(resume_features, jd_features),
        }
        self.session.set("report", report)
        logger.info("ReportAgent produced report of %s chars", len(narrative))
        return report

    # ------------------------------------------------------------------
    #   MAIN FIXED FUNCTION (EMOJIS + NO DUPLICATE ATS BREAKDOWN)
    # ------------------------------------------------------------------
    def _generate_narrative(self, resume: Dict, jd: Dict, breakdown: MatchBreakdown | None) -> str:
        """Generate a clean, emoji-rich HR evaluation WITHOUT ATS breakdown duplication."""

        fallback = (
            f"Resume matches job at {breakdown.total if breakdown else 0:.2f}%. "
            "Review missing skills to improve alignment."
        )

        if not self.gemini_enabled:
            return fallback

        try:
            model = genai.GenerativeModel(self.model_name)

            prompt = f"""
You are an expert HR Recruiter. Create a clean, emoji-enhanced ATS evaluation in Markdown.
DO NOT repeat any ATS score breakdown because the UI already shows it.

❗ REQUIRED SECTIONS IN EXACT ORDER:
1. 📄 **Summary**
2. 🎯 **Strengths**
3. ⚠️ **Weaknesses**
4. 🥇 **Fit Rating**
5. 🛠️ **Improvement Suggestions**
6. ❌ **Missing Skills**

RULES:
- Do NOT include ATS Score Breakdown.
- Do NOT repeat skill/keyword/experience/structure percentages.
- Use bullets where needed.
- Keep sentences sharp and professional.
- Maximum 150–180 words.

### Inputs
Resume Skills: {resume.get('skills', [])}
Job Description Skills: {jd.get('skills', [])}

Fit Rating: {breakdown.fit_rating if breakdown else "N/A"}

Now generate the final formatted report.
"""

            response = model.generate_content(prompt)
            text = _extract_text(response)
            return text.strip() or fallback

        except Exception as exc:
            logger.error("Gemini report generation failed: %s", exc)
            return fallback

    # ------------------------------------------------------------------
    #   SKILL GAP
    # ------------------------------------------------------------------
    def _derive_skill_gap(self, resume: Dict, jd: Dict) -> str:
        resume_skills = {s.lower() for s in resume.get("skills", [])}
        missing = [s for s in jd.get("skills", []) if s.lower() not in resume_skills]
        return ", ".join(sorted(set(missing))) or "No significant gaps identified."
