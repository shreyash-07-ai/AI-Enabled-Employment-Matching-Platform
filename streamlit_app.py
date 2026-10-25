import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI Employment Matching Platform", page_icon="💼", layout="wide")

st.title("💼 AI-Enabled Employment Matching Platform")
st.caption("A demo Streamlit interface for exploring resume-to-job matching.")

st.info(
    "This Streamlit app is a standalone demo interface. The repository's full application "
    "uses a React/Vite frontend and a Django REST API. This demo does not connect to that "
    "backend automatically; deploy the Django API separately to enable full user accounts, "
    "resume uploads, recruiter dashboards, and asynchronous matching."
)

with st.sidebar:
    st.header("About")
    st.write("Explore a simple keyword-based resume/job matching demo.")
    st.caption("Demo scoring only; not a hiring decision.")

left, right = st.columns(2)
with left:
    st.subheader("Job description")
    job_text = st.text_area(
        "Paste the job description",
        placeholder="Example: Python, SQL, machine learning, NLP, Django...",
        height=220,
    )
with right:
    st.subheader("Resume text")
    resume_text = st.text_area(
        "Paste resume text (remove personal information first)",
        placeholder="Example: Built ML projects using Python, pandas, scikit-learn...",
        height=220,
    )

if st.button("Match resume to job", type="primary", use_container_width=True):
    if not job_text.strip() or not resume_text.strip():
        st.warning("Please enter both a job description and resume text.")
    else:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(stop_words="english")
            vectors = vectorizer.fit_transform([job_text, resume_text])
            score = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0]) * 100
            job_terms = set(vectorizer.get_feature_names_out())
            resume_vector = vectors[1].toarray().ravel()
            job_vector = vectors[0].toarray().ravel()
            job_weights = {term: job_vector[i] for i, term in enumerate(vectorizer.get_feature_names_out())}
            resume_weights = {term: resume_vector[i] for i, term in enumerate(vectorizer.get_feature_names_out())}
            missing = sorted(
                [(term, weight) for term, weight in job_weights.items()
                 if weight > 0 and resume_weights.get(term, 0) == 0],
                key=lambda x: x[1], reverse=True
            )[:10]

            st.subheader("Matching results")
            st.metric("Keyword similarity", f"{score:.1f}%")
            st.progress(min(max(score / 100, 0.0), 1.0))
            st.caption("This is TF-IDF text similarity, not a validated probability of job suitability.")
            if missing:
                st.write("Terms in the job description that were not found in the resume:")
                st.write(", ".join(term for term, _ in missing))
            else:
                st.success("The resume contains the terms detected in the job description.")
        except Exception as exc:
            st.error(f"Could not calculate match: {exc}")

st.divider()
st.subheader("Full project deployment")
st.markdown(
    "To run the original application with authentication, recruiter/job-seeker pages, and "
    "the Django REST API, deploy the `backend/` and `frontend/` folders as separate services. "
    "See [the deployment notes](https://github.com/shreyash-07-ai/AI-Enabled-Employment-Matching-Platform/blob/main/STREAMLIT_DEPLOYMENT.md)."
)
