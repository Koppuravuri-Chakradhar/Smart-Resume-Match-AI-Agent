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

    # OUTPUT PER RESUME
    for session, file in zip(sessions, uploaded_resumes):
        st.markdown(f"## 📄 Results for: **{file.name}**")

        score = session.get("score_breakdown")
        report = session.get("report", {})

        # -----------------------------
        # TOTAL SCORE
        # -----------------------------
        if score:
            st.metric("🎯 Total Score", f"{score.total:.2f}")
        else:
            st.metric("🎯 Total Score", "0.00")

        # -----------------------------
        # FIT RATING
        # -----------------------------
        if score:
            st.metric("🏅 Fit Rating", score.fit_rating)
        else:
            st.metric("🏅 Fit Rating", "N/A")

        # -----------------------------
        # ATS BREAKDOWN (4 columns)
        # -----------------------------
        if score:
            st.markdown("### 📊 ATS Score Breakdown")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skill Match", f"{score.skill_match:.2f}%")
            c2.metric("Keyword Match", f"{score.keyword_match:.2f}%")
            c3.metric("Experience Match", f"{score.experience_match:.2f}%")
            c4.metric("Structure Score", f"{score.structure_score:.2f}%")

        # -----------------------------
        # FULL SUMMARY (generated markdown)
        # -----------------------------
        st.markdown("### 🧾 Summary")
        st.markdown(report.get("summary", "No summary available."), unsafe_allow_html=True)

        # -----------------------------
        # MISSING SKILLS
        # -----------------------------
        st.markdown("### ❌ Missing Skills")
        st.write(report.get("skill_gap", "None"))

else:
    st.info("Upload resumes + JD → Click Analyze")
