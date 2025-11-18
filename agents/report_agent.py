from __future__ import annotations

import logging
import os
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai

from memory.session_state import SessionState
from tools.scoring_engine import MatchBreakdown

# Load key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

logger = logging.getLogger(__name__)


def _extract_text(response) -> str:
    try:
        return response.text or ""
    except:
        return ""


class ReportAgent:
    """Generates clean HR-style report WITHOUT ATS section (UI handles that)."""

    def __init__(self, session: SessionState, model="models/gemini-2.5-flash"):
        self.session = session
        self.model = model
        self.enabled = API_KEY is not None

    def run(self) -> Dict[str, str]:
        resume = self.session.get("resume_features", {})
        jd = self.session.get("jd_features", {})
        breakdown: MatchBreakdown = self.session.get("score_breakdown")

        narrative = self._generate(resume, jd, breakdown)
        return {
            "summary": narrative,
            "skill_gap": self._skill_gap(resume, jd)
        }

    def _generate(self, resume, jd, breakdown):
        fallback = "Unable to generate report."

        if not self.enabled:
            return fallback

        try:
            model = genai.GenerativeModel(self.model)

            prompt = f"""
You must generate ONLY the sections below — NO ATS numbers.
ATS breakdown is handled by frontend UI.

FORMAT EXACTLY:

🧾 Summary
<4–6 sentence professional summary>

🎯 Strengths
• point
• point
• point

⚠️ Weaknesses
• point
• point
• point

🥇 Fit Rating: {breakdown.fit_rating}
<short paragraph>

🛠️ Improvement Suggestions
1. suggestion
2. suggestion
3. suggestion

❌ Missing Skills
(This section will be filled by backend — DO NOT add items.)

STRICT RULES:
- DO NOT include ATS scores here.
- DO NOT repeat Missing Skills.
- DO NOT add emojis at the end of lines.
- DO NOT use '-' for bullets, only '•'.
- Keep spacing EXACTLY like shown.

Resume Skills: {resume.get('skills', [])}
Job Skills: {jd.get('skills', [])}
"""

            resp = model.generate_content(prompt)
            return _extract_text(resp).strip() or fallback

        except Exception as e:
            logger.error("Gemini report generation failed: %s", e)
            return fallback

    def _skill_gap(self, resume, jd):
        rs = {s.lower() for s in resume.get("skills", [])}
        missing = [s for s in jd.get("skills", []) if s.lower() not in rs]
        return ", ".join(sorted(set(missing))) or "No significant gaps identified."
