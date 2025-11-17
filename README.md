# Smart Resume → Job Match AI Agent

## Problem
Recruiters waste hours manually comparing resumes to complex job descriptions. The process lacks transparency, repeatability, and scales poorly when evaluating multiple candidates.

## Solution
This project implements a modular multi-agent architecture powered by Google Gemini, NLTK, and custom tools. Each agent tackles a specific stage: parsing resumes, extracting skills, analyzing job descriptions, scoring matches, and generating explainable reports. The workflow persists state between agents, logs every step, and supports parallel evaluation of multiple resumes. A Streamlit UI exposes the pipeline for interactive analysis.

## Architecture
```
Streamlit UI → Orchestrator (app.py)
  ├─ ResumeParserAgent → PDFParser tool
  ├─ SkillExtractionAgent → Gemini + KeywordExtractor tool
  ├─ JobDescriptionAgent → Gemini + KeywordExtractor tool
  ├─ ScoringAgent → ScoringEngine tool
  └─ ReportAgent → Gemini narrative
```
State flows through `memory/session_state.py` and observability is provided via Python logging.

## Setup
1. **Python**: Install Python 3.10+ and create a virtual environment.
2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   (If the file is missing, install: `streamlit PyPDF2 pandas numpy nltk google-generativeai`.)
3. **Environment**: Export your Gemini key—never hardcode it.
   ```bash
   set GEMINI_API_KEY="YOUR_KEY"
   ```
4. **NLTK Data**: The first run downloads tokenizer assets automatically.

## Usage
1. **Run Orchestrator Tests** (optional):
   ```bash
   python app.py
   ```
2. **Launch UI**:
   ```bash
   streamlit run ui/streamlit_app.py
   ```
3. **Interact**:
   - Upload one or more PDF resumes.
   - Paste the target job description.
   - View scores, explanations, and missing skill highlights.

## Demo Ideas
- Evaluate several mock resumes in parallel to showcase ranking output.
- Modify scoring weights inside `tools/scoring_engine.py` to demonstrate extensibility.
- Extend `ReportAgent` prompts for customized HR narratives.

