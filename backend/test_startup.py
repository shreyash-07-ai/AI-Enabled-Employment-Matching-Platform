"""
Startup performance and import cleanliness test.
Run: python test_startup.py
"""
import os, sys, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['SECRET_KEY'] = 'test-ci-key'
os.environ['DEBUG'] = 'True'
os.environ['SBERT_ENABLED'] = 'False'

start = time.time()
import django
django.setup()
from core.wsgi import application  # noqa: F401
elapsed = time.time() - start

errors = []

print(f"WSGI app loaded in {elapsed:.2f}s")
print(f"sentence_transformers in sys.modules: {'sentence_transformers' in sys.modules}")
print(f"torch in sys.modules: {'torch' in sys.modules}")

if elapsed > 10:
    errors.append(f"Startup too slow: {elapsed:.2f}s (should be <10s)")
if 'sentence_transformers' in sys.modules:
    errors.append("sentence_transformers was imported during startup")
if 'torch' in sys.modules:
    errors.append("torch was imported during startup")

from resumes.matching_engine import SBERT_AVAILABLE, BM25_AVAILABLE
print(f"SBERT_AVAILABLE: {SBERT_AVAILABLE} (expected: False)")
print(f"BM25_AVAILABLE: {BM25_AVAILABLE} (expected: True)")

if SBERT_AVAILABLE:
    errors.append("SBERT_AVAILABLE should be False when SBERT_ENABLED=False")
if not BM25_AVAILABLE:
    errors.append("BM25_AVAILABLE should be True (rank-bm25 is installed)")

print()
if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("PASS: startup is clean and fast")
