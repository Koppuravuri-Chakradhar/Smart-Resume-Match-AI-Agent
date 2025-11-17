from memory.session_state import SessionState
from tools.scoring_engine import ScoringEngine

class ScoringAgent:
    def __init__(self, session: SessionState):
        self.session = session

    def run(self):
        resume = self.session.get("resume_features")
        jd = self.session.get("jd_features")
        resume_text = self.session.get("resume_text", "")

        breakdown = ScoringEngine.score(resume, jd, resume_text)
        self.session.set("score_breakdown", breakdown)
        return breakdown
