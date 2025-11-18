"""
Streamlit UI for Smart Resume → Job Match AI Agent.
Supports PDF & DOCX resumes.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Add parent directory to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app import process_multiple_resumes

# Page setup
st.set_page_config(page_title="Smart Resume Match", layout="wide")
st.title("Smart Resume → Job Match AI Agent")
st.write("Upload PDF or DOCX resumes and paste a job description to generate match scores, ATS breakdown, and HR-style evaluation reports.")

# Upload Section
uploaded_resumes = st.file_uploader(
    "Upload Resumes (PDF or DOCX only)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

job_description = st.text_area("Paste Job Description", height=200)

# Main Action Button
if st.button("Analyze"):

    if not uploaded_resumes:
        st.error("❗ Please upload at least one resume.")
    elif not job_description.strip():
        st.error("❗ Please paste a job description.")
    else:
        st.success("Processing resumes... Please wait ⏳")

        # Convert uploaded files to bytes
        resume_payloads: List[bytes] = []
        for file in uploaded_resumes:
            try:
                file_bytes = file.read()
                file.seek(0)
                resume_payloads.append(file_bytes)
            except Exception as e:
                st.error(f"Error reading file {file.name}: {e}")
                continue

        # Run pipeline
        try:
            sessions = process_multiple_resumes(resume_payloads, job_description)
        except Exception as e:
            st.error(f"🔥 Pipeline Error: {e}")
            st.stop()

        # DISPLAY RESULTS
        for session, file in zip(sessions, uploaded_resumes):

            st.markdown(f"## 📝 Results for: **{file.name}**")

            score = session.get("score_breakdown")
            report = session.get("report")

            # SCORE CARD
            st.markdown("### 🎯 Total Score")
            if score:
                st.metric("", f"{score.total:.2f}")
            else:
                st.metric("", "0.00")

            # FIT RATING
            if score:
                st.markdown(f"""
                ### 🏅 Fit Rating  
                **{score.fit_rating}**
                """)

            # ATS BREAKDOWN
            if score:
                st.markdown("""
                ### 📊 ATS Score Breakdown
                """)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Skill Match", f"{score.skill_match}%")
                col2.metric("Keyword Match", f"{score.keyword_match}%")
                col3.metric("Experience Match", f"{score.experience_match}%")
                col4.metric("Structure Score", f"{score.structure_score}%")

            # SUMMARY
            st.markdown("### 🧾 Summary")
            if report:
                st.markdown(report.get("summary", "No summary available."), unsafe_allow_html=True)
            else:
                st.write("No summary available.")

            # MISSING SKILLS
            st.markdown("### ❌ Missing Skills")
            if report:
                st.markdown(report.get("skill_gap", "None"))
            else:
                st.write("N/A")

else:
    st.info("📂 Upload resume(s) and a job description, then click **Analyze**.")
