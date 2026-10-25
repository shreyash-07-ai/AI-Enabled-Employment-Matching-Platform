"""
AI Matching Engine — Semantic Resume-to-Job matching using
TF-IDF, BM25, and Sentence Transformers (SBERT).

This module provides:
  • Text extraction from PDF/DOCX
  • NLP preprocessing (tokenization, stopword removal, lemmatization)
  • Skill / entity extraction
  • TF-IDF + BM25 scoring
  • Sentence-Transformer (SBERT) semantic embedding scoring
  • Combined scoring with configurable weights
  • Missing-skills analysis and resume improvement suggestions
"""

import re
import logging
import hashlib
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from pdfminer.high_level import extract_text as pdf_extract
import docx

# ── Optional: BM25 ──────────────────────────────────────────────────
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

# ── Optional: Sentence Transformers ─────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

# ── NLTK bootstrap ──────────────────────────────────────────────────
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Download NLTK packages lazily when needed (not at import time)
_NLTK_DOWNLOADED = False

def ensure_nltk_data():
    """Download NLTK data packages if not already done"""
    global _NLTK_DOWNLOADED
    if _NLTK_DOWNLOADED:
        return
    
    for pkg in ["punkt", "stopwords", "punkt_tab"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception as e:
            log = logging.getLogger(__name__)
            log.warning(f"Could not download NLTK package {pkg}: {e}")
    _NLTK_DOWNLOADED = True

log = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════
# KNOWN SKILLS DATABASE  (expandable)
# ════════════════════════════════════════════════════════════════════
KNOWN_SKILLS = {
    # Programming
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "dart", "lua", "shell", "bash", "powershell", "sql",
    # Web
    "html", "css", "react", "angular", "vue", "django", "flask",
    "fastapi", "spring", "node", "express", "next", "nuxt", "tailwind",
    "bootstrap", "jquery", "graphql", "rest", "soap",
    # Data / ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "opencv", "nltk", "spacy", "transformers",
    "huggingface", "bert", "gpt", "llm", "deep learning", "machine learning",
    "nlp", "computer vision", "data analysis", "data science", "statistics",
    "big data", "hadoop", "spark", "kafka", "airflow", "mlflow",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "nginx",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "dynamodb", "firebase", "oracle", "sqlite", "cassandra",
    # Soft skills / domains
    "leadership", "communication", "teamwork", "problem solving",
    "project management", "agile", "scrum", "jira",
}

# Mapping of synonyms to canonical skill names for semantic equivalence
SKILL_SYNONYMS = {
    "js": "javascript",
    "ts": "typescript",
    "node.js": "node",
    "nodejs": "node",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "next.js": "next",
    "nuxt.js": "nuxt",
    "express.js": "express",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "ml": "machine learning",
    "dl": "deep learning",
    "natural language processing": "nlp",
    "cv": "computer vision",
    "managed team": "leadership",
    "led team": "leadership",
    "team lead": "leadership",
    "scripting": "python",
    "data analysis tools": "data analysis",
}

# ════════════════════════════════════════════════════════════════════
# TEXT EXTRACTION
# ════════════════════════════════════════════════════════════════════
_STOP_WORDS = None

def get_stop_words():
    """Get English stop words, downloading NLTK data if needed"""
    global _STOP_WORDS
    if _STOP_WORDS is None:
        ensure_nltk_data()
        _STOP_WORDS = set(stopwords.words("english"))
    return _STOP_WORDS


def extract_pdf(path: str) -> str:
    try:
        return pdf_extract(path) or ""
    except Exception as e:
        log.warning(f"PDF extraction failed [{path}]: {e}")
        return ""


def extract_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    parts.append(cell.text)
        return " ".join(parts)
    except Exception as e:
        log.warning(f"DOCX extraction failed [{path}]: {e}")
        return ""


def extract_text_from_file(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_docx(path)
    else:
        log.warning(f"Unsupported file type: {path}")
        return ""


# ════════════════════════════════════════════════════════════════════
# NLP PREPROCESSING
# ════════════════════════════════════════════════════════════════════
def clean_text(text: str) -> str:
    """Lowercase, strip URLs/emails, remove non-alphanumeric, remove stopwords."""
    ensure_nltk_data()
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    stop_words = get_stop_words()
    tokens = [w for w in tokens if w not in stop_words and len(w) > 1]
    return " ".join(tokens)


def extract_skills_from_text(text: str) -> list:
    """Extract known skills from raw text using both direct match and synonyms."""
    text_lower = text.lower()
    found = set()

    # Direct skill matching
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found.add(skill)

    # Synonym matching
    for synonym, canonical in SKILL_SYNONYMS.items():
        if re.search(r'\b' + re.escape(synonym) + r'\b', text_lower):
            found.add(canonical)

    return sorted(found)


def extract_keywords(text: str, top_n: int = 30) -> list:
    """Extract the most significant words using TF-IDF on a single doc."""
    vectorizer = TfidfVectorizer(max_features=top_n, ngram_range=(1, 2))
    try:
        vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()
    except Exception:
        return []


# ════════════════════════════════════════════════════════════════════
# SCORING ENGINES
# ════════════════════════════════════════════════════════════════════
def tfidf_score(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between resume and JD using TF-IDF vectors."""
    vec = TfidfVectorizer()
    mat = vec.fit_transform([resume_text, jd_text])
    sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
    return float(sim)


def bm25_score(resume_text: str, jd_text: str) -> float:
    """BM25 relevance score (normalised to 0-1)."""
    if not BM25_AVAILABLE:
        return 0.0
    corpus = [resume_text.split()]
    bm25 = BM25Okapi(corpus)
    query = jd_text.split()
    scores = bm25.get_scores(query)
    max_s = max(scores) if max(scores) > 0 else 1
    return float(scores[0] / max_s)


# ── Lazy-loaded SBERT model singleton ────────────────────────────
_sbert_model = None

def _get_sbert_model():
    global _sbert_model
    if _sbert_model is None and SBERT_AVAILABLE:
        log.info("Loading SBERT model (all-MiniLM-L6-v2)...")
        _sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _sbert_model


def sbert_score(resume_text: str, jd_text: str) -> float:
    """Semantic similarity using Sentence-BERT embeddings."""
    model = _get_sbert_model()
    if model is None:
        return 0.0
    embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True)
    sim = st_util.cos_sim(embeddings[0], embeddings[1])
    return float(sim.item())


# ════════════════════════════════════════════════════════════════════
# COMBINED MATCHING
# ════════════════════════════════════════════════════════════════════
def compute_match(resume_text: str, jd_text: str,
                  tfidf_weight: float = 0.25,
                  bm25_weight: float = 0.15,
                  sbert_weight: float = 0.60) -> dict:
    """
    Master matching function.  Returns a rich result dict with:
      - match_score_pct
      - tfidf_score, bm25_score, sbert_score (individual)
      - matched_skills, missing_skills
      - resume_suggestions
    """
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)

    # ── Individual scores ────────────────────────────────────────
    tf = tfidf_score(clean_resume, clean_jd)
    bm = bm25_score(clean_resume, clean_jd) if BM25_AVAILABLE else 0.0
    sb = sbert_score(clean_resume, clean_jd) if SBERT_AVAILABLE else 0.0

    # Adjust weights if optional engines are missing
    actual_tf_w = tfidf_weight
    actual_bm_w = bm25_weight if BM25_AVAILABLE else 0.0
    actual_sb_w = sbert_weight if SBERT_AVAILABLE else 0.0
    total_w = actual_tf_w + actual_bm_w + actual_sb_w
    if total_w > 0:
        actual_tf_w /= total_w
        actual_bm_w /= total_w
        actual_sb_w /= total_w

    combined = actual_tf_w * tf + actual_bm_w * bm + actual_sb_w * sb
    match_pct = round(combined * 100, 2)

    # ── Skill analysis ───────────────────────────────────────────
    resume_skills = set(extract_skills_from_text(resume_text))
    jd_skills = set(extract_skills_from_text(jd_text))
    matched_skills = sorted(resume_skills & jd_skills)
    missing_skills = sorted(jd_skills - resume_skills)

    # ── Suggestions ──────────────────────────────────────────────
    suggestions = []
    if missing_skills:
        suggestions.append(f"Consider adding these skills to your resume: {', '.join(missing_skills[:10])}")
    if len(resume_text.split()) < 150:
        suggestions.append("Your resume appears short. Add more detail about projects and experience.")
    if not any(kw in resume_text.lower() for kw in ["project", "developed", "built", "created", "implemented"]):
        suggestions.append("Include specific project descriptions with technologies used.")
    if not any(kw in resume_text.lower() for kw in ["certified", "certification", "certificate"]):
        suggestions.append("Consider adding relevant certifications to strengthen your profile.")

    return {
        "match_score_pct": match_pct,
        "tfidf_score": round(tf * 100, 2),
        "bm25_score": round(bm * 100, 2),
        "sbert_score": round(sb * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "engines_used": {
            "tfidf": True,
            "bm25": BM25_AVAILABLE,
            "sbert": SBERT_AVAILABLE,
        },
    }


def rank_candidates(resumes: list, jd_text: str) -> list:
    """
    Rank multiple resumes against a single JD.
    resumes: list of dicts with 'id', 'name', 'text' keys
    Returns sorted list (best first) with match results attached.
    """
    results = []
    for r in resumes:
        match = compute_match(r["text"], jd_text)
        match["resume_id"] = r["id"]
        match["resume_name"] = r["name"]
        results.append(match)

    results.sort(key=lambda x: x["match_score_pct"], reverse=True)
    for i, item in enumerate(results, start=1):
        item["rank"] = i
    return results
