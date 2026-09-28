import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Keep the existing matching engine untouched.
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from resumes.matching_engine import compute_match, extract_text_from_file


st.set_page_config(
    page_title="AI Employment Matching Platform",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 AI-Enabled Employment Matching Platform")
st.caption(
    "Streamlit deployment layer using the existing TF-IDF + BM25 + SBERT matching engine."
)

st.info(
    "This Streamlit app is a standalone deployment interface. "
    "The existing Django + React application remains unchanged."
)

with st.sidebar:
    st.header("⚙️ Matching Settings")
    st.write("The original project weights are used by default:")
    st.code("TF-IDF  25%\nBM25    15%\nSBERT   60%")
    st.markdown("---")
    st.write("Supported resume formats: PDF, DOCX")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Resume")
    resume_file = st.file_uploader(
        "Upload a resume",
        type=["pdf", "docx"],
        help="Upload a text-based PDF or DOCX resume.",
    )

with col2:
    st.subheader("💼 Job Description")
    job_title = st.text_input(
        "Job title",
        placeholder="e.g. AI/ML Engineer",
    )
    job_description = st.text_area(
        "Paste the complete job description",
        height=280,
        placeholder="Paste the job description, required skills, responsibilities, education and experience...",
    )

analyze = st.button("🚀 Analyze Match", type="primary", use_container_width=True)

if analyze:
    if not resume_file:
        st.error("Please upload a PDF or DOCX resume.")
        st.stop()

    if not job_description.strip():
        st.error("Please enter a job description.")
        st.stop()

    temp_path = None

    try:
        suffix = Path(resume_file.name).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(resume_file.getbuffer())
            temp_path = tmp.name

        with st.spinner("Extracting resume and calculating AI match..."):
            resume_text = extract_text_from_file(temp_path)

            if not resume_text.strip():
                st.error(
                    "No readable text was extracted from the resume. "
                    "Try a text-based PDF or DOCX file."
                )
                st.stop()

            result = compute_match(resume_text, job_description)

        st.success("Match analysis completed.")

        score = float(result["match_score_pct"])

        st.subheader("📊 Match Result")
        score_col, tf_col, bm_col, sb_col = st.columns(4)

        score_col.metric("Overall Match", f"{score:.2f}%")
        tf_col.metric("TF-IDF", f'{result["tfidf_score"]:.2f}%')
        bm_col.metric("BM25", f'{result["bm25_score"]:.2f}%')
        sb_col.metric("SBERT", f'{result["sbert_score"]:.2f}%')

        if job_title:
            st.write(f"**Job:** {job_title}")

        st.progress(min(max(score / 100, 0.0), 1.0))

        left, right = st.columns(2)

        with left:
            st.subheader("✅ Matched Skills")
            matched = result.get("matched_skills", [])
            if matched:
                st.write(", ".join(matched))
            else:
                st.write("No known matching skills detected.")

        with right:
            st.subheader("⚠️ Missing Skills")
            missing = result.get("missing_skills", [])
            if missing:
                st.write(", ".join(missing))
            else:
                st.write("No missing skills detected from the known skill database.")

        st.subheader("💡 Resume Suggestions")
        suggestions = result.get("suggestions", [])
        if suggestions:
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
        else:
            st.write("No additional suggestions.")

        with st.expander("🔍 Matching Engine Details"):
            st.json(
                {
                    "engines_used": result.get("engines_used", {}),
                    "resume_characters": len(resume_text),
                    "job_description_characters": len(job_description),
                }
            )

        with st.expander("📄 Extracted Resume Text"):
            st.text_area(
                "Resume text",
                resume_text,
                height=350,
                label_visibility="collapsed",
            )

    except Exception as exc:
        st.error("The analysis could not be completed.")
        st.exception(exc)

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

st.markdown("---")
st.caption(
    "AI-Enabled Employment Matching Platform • Existing matching engine preserved"
)
