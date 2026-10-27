"""
Smoke test: verify matching_engine works correctly with SBERT disabled
(simulating Render free-tier with SBERT_ENABLED=False).
Run from backend/ directory:  python test_matching_smoke.py
"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['SBERT_ENABLED'] = 'False'   # force TF-IDF + BM25 only

import django
django.setup()

from resumes.matching_engine import (
    compute_match, extract_skills_from_text,
    extract_text_from_file, BM25_AVAILABLE, SBERT_AVAILABLE,
)

errors = []

# ── 1. Check flags ─────────────────────────────────────────────────
print(f"BM25_AVAILABLE  : {BM25_AVAILABLE}")
print(f"SBERT_AVAILABLE : {SBERT_AVAILABLE}")  # should be True (flag starts True, lazy)

# ── 2. skill extraction ────────────────────────────────────────────
resume_text = (
    "Python developer with 3 years experience. Skilled in Django, REST APIs, "
    "PostgreSQL, Docker, and scikit-learn. Led a team of 5 engineers. "
    "Built recommendation systems using machine learning and deep learning. "
    "Certified AWS Solutions Architect."
)
jd_text = (
    "Looking for a Python backend engineer with Django, REST, PostgreSQL, "
    "Docker, and machine learning experience. Team leadership a plus."
)

skills = extract_skills_from_text(resume_text)
print(f"\nextract_skills_from_text result: {skills}")
if 'python' not in skills:
    errors.append("'python' not found in extracted skills")
if 'django' not in skills:
    errors.append("'django' not found in extracted skills")

# ── 3. compute_match ──────────────────────────────────────────────
result = compute_match(resume_text, jd_text)
print(f"\ncompute_match result:")
print(f"  match_score_pct : {result['match_score_pct']}")
print(f"  tfidf_score     : {result['tfidf_score']}")
print(f"  bm25_score      : {result['bm25_score']}")
print(f"  sbert_score     : {result['sbert_score']}")
print(f"  matched_skills  : {result['matched_skills']}")
print(f"  missing_skills  : {result['missing_skills']}")
print(f"  engines_used    : {result['engines_used']}")
print(f"  suggestions     : {result['suggestions']}")

if result['match_score_pct'] <= 0:
    errors.append("match_score_pct should be > 0")
if 'python' not in result['matched_skills']:
    errors.append("'python' should be in matched_skills")
if 'django' not in result['matched_skills']:
    errors.append("'django' should be in matched_skills")
if result['engines_used']['tfidf'] is not True:
    errors.append("tfidf engine should be True")

# ── 4. startup import check ───────────────────────────────────────
import sys as _sys
st_imported = 'sentence_transformers' in _sys.modules
torch_imported = 'torch' in _sys.modules
print(f"\nsentence_transformers in sys.modules : {st_imported}")
print(f"torch in sys.modules                : {torch_imported}")
if st_imported:
    errors.append("sentence_transformers should NOT be imported at startup")
if torch_imported:
    errors.append("torch should NOT be imported at startup")

# ── Result ────────────────────────────────────────────────────────
print()
if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: all checks passed")
