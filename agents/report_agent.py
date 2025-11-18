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
            logger.warning("GOOGLE_API_KEY not found; ReportAgent will fallback to deterministic narrative.")

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
        """Use Gemini to create a premium ATS-style evaluation summary."""
        
        fallback = (
            f"Resume matches job at {breakdown.total if breakdown else 0:.2f}%. "
            "Review missing skills to improve alignment."
        )

        if not self.gemini_enabled:
            return fallback

        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")

           prompt = (
    "You are an expert HR recruiter. Generate a structured ATS evaluation "
    "using EXACTLY the following sections with these emojis. Do NOT remove emojis. "
    "Do NOT add new headings. Keep formatting consistent every time.\n\n"

    "📄 **Results Overview**\n"
    "- Provide a one-line summary of resume–job match quality.\n\n"

    "🎯 **Total Score**\n"
    "- Provide ONLY the score explanation in 1–2 lines.\n\n"

    "🏅 **Fit Rating**\n"
    "- State the fit rating (Poor/Moderate/Strong) with 1–2 lines of reasoning.\n\n"

    "📊 **ATS Score Breakdown**\n"
    f"- Skill Match: {breakdown.skill_match}%\n"
    f"- Keyword Match: {breakdown.keyword_match}%\n"
    f"- Experience Match: {breakdown.experience_match}%\n"
    f"- Structure Score: {breakdown.structure_score}%\n\n"

    "🧾 **Summary**\n"
    "- Provide a 2–3 line overall interpretation of the candidate profile.\n\n"

    "✨ **Strengths**\n"
    "List exactly 3 bullet points.\n\n"

    "⚠️ **Weaknesses**\n"
    "List exactly 3 bullet points.\n\n"

    "🎓 **Improvement Suggestions**\n"
    "Provide exactly 3 numbered, actionable suggestions.\n\n"

    "❌ **Missing Skills**\n"
    "- Provide comma-separated missing skills only.\n\n"

    f"Resume Skills: {resume.get('skills', [])}\n"
    f"Job Description Skills: {jd.get('skills', [])}\n\n"

    "Return ONLY the formatted markdown with emojis — no extra commentary."
)


            response = model.generate_content(prompt)
            text = _extract_text(response)
            return text.strip() or fallback

        except Exception as exc:
            logger.error(f"Gemini report generation failed: {exc}")
            return fallback

    def _derive_skill_gap(self, resume: Dict, jd: Dict) -> str:
        resume_skills = {s.lower() for s in resume.get("skills", [])}
        missing = [s for s in jd.get("skills", []) if s.lower() not in resume_skills]
        return ", ".join(sorted(set(missing))) or "No significant gaps identified."
