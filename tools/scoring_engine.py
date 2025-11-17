from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
import re


@dataclass
class MatchBreakdown:
    total: float
    skill_match: float
    keyword_match: float
    experience_match: float
    structure_score: float
    fit_rating: str


class ScoringEngine:
    """Provides combined ATS + Skill + Experience scoring."""

    @staticmethod
    def score(resume: Dict, jd: Dict, resume_text: str) -> MatchBreakdown:
        resume_skills = set(s.lower() for s in resume.get("skills", []))
        jd_skills = set(s.lower() for s in jd.get("skills", []))

        # SKILL MATCH
        matched_skills = resume_skills & jd_skills
        skill_match = (
            (len(matched_skills) / len(jd_skills)) * 100
            if jd_skills else 0
        )

        # KEYWORD MATCH
        keywords = jd.get("keywords", [])
        found_keywords = [k for k in keywords if k.lower() in resume_text.lower()]
        keyword_match = (
            (len(found_keywords) / len(keywords)) * 100
            if keywords else 0
        )

        # EXPERIENCE MATCH
        jd_years = int(jd.get("years_experience", 0))
        resume_years = int(resume.get("years_experience", 0))

        if jd_years == 0:
            experience_match = 100
        else:
            experience_match = min((resume_years / jd_years) * 100, 100)

        # STRUCTURE SCORE
        structure_elements = ["summary", "skills", "experience", "projects", "education"]
        structure_score = sum(1 for sec in structure_elements if sec in resume_text.lower()) / 5 * 100

        # FINAL ATS SCORE
        total = (
            skill_match * 0.4 +
            keyword_match * 0.3 +
            experience_match * 0.2 +
            structure_score * 0.1
        )

        # FIT RATING
        if total >= 80:
            fit = "Strong Fit"
        elif total >= 55:
            fit = "Medium Fit"
        else:
            fit = "Poor Fit"

        return MatchBreakdown(
            total=round(total, 2),
            skill_match=round(skill_match, 2),
            keyword_match=round(keyword_match, 2),
            experience_match=round(experience_match, 2),
            structure_score=round(structure_score, 2),
            fit_rating=fit,
        )
