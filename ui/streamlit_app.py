"""
Streamlit UI for Smart Resume → Job Match AI Agent
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app import process_multiple_resumes

st.set_page_config(page_title="Smart Resume Match", layout="wide")

st.title("Smart Resume → Job Match AI Agent")
st.write("Upload PDF or DOCX resumes and paste a job description to generate ATS scores and a recruiter-style summary.")

uploaded_resumes = st.file_uploader(
    "Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

jd_text = st.text_area("Paste Job Description")

if st.button("Analyze"):

    if not uploaded_resumes:
        st.error("Upload at least one resume.")
        st.stop()

    if not jd_text.strip():
        st.error("Paste a job description.")
        st.stop()

    st.success("Processing resumes… Please wait ⏳")

    resume_bytes = [file.read() for file in uploaded_resumes]

    sessions = process_multiple_resumes(resume_bytes, jd_text)

    # Output
    for session, file in zip(sessions, uploaded_resumes):
        st.markdown(f"## 📄 Results for: **{file.name}**")

        score = session.get("score_breakdown", {})
        rep = session.get("report", {})

        # TOTAL SCORE
        st.metric("🎯 Total Score", f"{score.get('total', 0)}")

        # FIT RATING
        st.metric("🏅 Fit Rating", score.get("fit_rating", "N/A"))

        # ATS Breakdown
        st.markdown("### 📊 ATS Score Breakdown")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Skill Match", f"{score.get('skill_match', 0)}%")
        c2.metric("Keyword Match", f"{score.get('keyword_match', 0)}%")
        c3.metric("Experience", f"{score.get('experience_match', 0)}%")
        c4.metric("Structure Score", f"{score.get('structure_score', 0)}%")

        # Summary
        st.markdown("### 🧾 Summary")
        st.write(rep.get("summary", ""))

        # Strengths
        st.markdown("### 🎯 Strengths")
        for s in rep.get("strengths", []):
            st.write(f"• {s}")

        # Weaknesses
        st.markdown("### ⚠️ Weaknesses")
        for w in rep.get("weaknesses", []):
            st.write(f"• {w}")

        # Improvements
        st.markdown("### 🛠️ Improvement Suggestions")
        for i in rep.get("improvements", []):
            st.write(f"• {i}")

        # Missing Skills
        st.markdown("### ❌ Missing Skills")
        for m in rep.get("skill_gap", []):
            st.write(f"• {m}")

else:
    st.info("Upload resumes + JD → Click Analyze")
