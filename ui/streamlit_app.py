"""
Streamlit UI for Smart Resume → Job Match AI Agent.
Mobile-friendly version (Android/iPhone support)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List
import streamlit as st

# Add parent directory so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import process_multiple_resumes

# -------------------------------------------------
# 🔥 MOBILE FIX (CRITICAL) — Prevent 403 Forbidden Error
# -------------------------------------------------
st.markdown(
    """
    <meta name="referrer" content="no-referrer">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# MOBILE FIX 1 — Improved responsiveness + viewport
# -------------------------------------------------
st.set_page_config(page_title="Smart Resume Match", layout="wide")

# Style fixes
st.markdown("""
<style>
html, body {
    max-width: 100%;
    overflow-x: hidden;
}

.block-container {
    padding-left: 1rem;
    padding-right: 1rem;
}

@media (max-width: 600px) {
    .block-container {
        padding: 0.5rem;
    }
    textarea, input, .stTextArea {
        font-size: 14px !important;
    }
}
</style>

<meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

# -------------------------------------------------
# UI SECTION
# -------------------------------------------------
st.title("Smart Resume → Job Match AI Agent")
st.write("Upload PDF or DOCX resumes and paste a job description to generate match scores and reports.")

uploaded_resumes = st.file_uploader(
    "Upload Resumes (PDF or DOCX only)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

job_description = st.text_area("Paste Job Description", height=180)

# -------------------------------------------------
# MOBILE FIX 2 — Limit file size for mobile browsers
# -------------------------------------------------
if uploaded_resumes:
    for file in uploaded_resumes:
        if file.size > 3 * 1024 * 1024:  # 3MB limit
            st.error(f"{file.name} is too large (>3MB). Please upload from laptop/desktop.")
            st.stop()

# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------
if st.button("Analyze"):

    if not uploaded_resumes:
        st.error("Please upload at least one resume.")
        st.stop()

    if not job_description.strip():
        st.error("Please paste a job description.")
        st.stop()

    st.success("Processing resumes... Please wait ⏳")


    # Convert UploadedFile → bytes
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

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------
    for session, file in zip(sessions, uploaded_resumes):

        st.subheader(f"Results for: {file.name}")

        score = session.get("score_breakdown")
        report = session.get("report")

        # Total Score
        if score:
            st.metric("Total Score", f"{score.total:.2f}")
        else:
            st.metric("Total Score", "0.00")

        # Summary
        st.write("### Summary")
        if report:
            st.markdown(report.get("summary", "No summary available."), unsafe_allow_html=True)
        else:
            st.write("No report generated.")

        # Missing Skills
        st.write("### Missing Skills")
        if report:
            st.write(report.get("skill_gap", "None"))
        else:
            st.write("N/A")

else:
    st.info("Upload resume(s) and a job description, then click Analyze.")
