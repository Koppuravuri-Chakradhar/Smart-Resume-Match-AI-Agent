"""
Main orchestrator for the Smart Resume → Job Match AI Agent pipeline.
"""

from __future__ import annotations

import concurrent.futures
import logging
from pathlib import Path
from typing import Iterable, List

from agents.jd_agent import JobDescriptionAgent
from agents.parser_agent import ResumeParserAgent
from agents.report_agent import ReportAgent
from agents.score_agent import ScoringAgent
from agents.skill_agent import SkillExtractionAgent
from memory.session_state import SessionState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("app")


def run_pipeline(resume_source: Path | bytes, jd_text: str) -> SessionState:
    """
    Execute sequential multi-agent pipeline for a single resume.
    """
    session = SessionState()
    # Sequential hand-off between agents ensures deterministic flow.
    ResumeParserAgent(session).run(resume_source)
    SkillExtractionAgent(session).run()
    JobDescriptionAgent(session).run(jd_text)
    ScoringAgent(session).run()
    ReportAgent(session).run()
    return session


def process_multiple_resumes(resume_sources: Iterable[Path | bytes], jd_text: str) -> List[SessionState]:
    """
    Process multiple resumes in parallel using thread pool execution.
    """
    sources = list(resume_sources)
    # ThreadPoolExecutor keeps CPU-bound scoring responsive for multiple resumes.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda src: run_pipeline(src, jd_text), sources))
    return results


if __name__ == "__main__":
    logger.info("Smart Resume → Job Match AI Agent orchestrator ready.")

