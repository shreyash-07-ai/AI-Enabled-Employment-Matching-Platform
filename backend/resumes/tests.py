"""
Integration tests for Resumes API and matching engine.
"""
import os
os.environ.setdefault('SBERT_ENABLED', 'False')

import io
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User, JobSeekerProfile, RecruiterProfile
from jobs.models import JobPosting
from resumes.models import UploadedResume, JobApplication
from resumes.matching_engine import (
    compute_match, extract_skills_from_text,
    BM25_AVAILABLE, SBERT_AVAILABLE,
)


def make_seeker(username='seeker_test'):
    user = User.objects.create_user(username=username, password='pass123', role='JOB_SEEKER')
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return user, profile


def make_recruiter(username='rec_test', company='TestCo'):
    user = User.objects.create_user(username=username, password='pass123', role='RECRUITER')
    profile, _ = RecruiterProfile.objects.get_or_create(user=user, defaults={'company_name': company})
    return user, profile


# ════════════════════════════════════════════════════════════════════
# Matching Engine Unit Tests (no HTTP — pure Python)
# ════════════════════════════════════════════════════════════════════
class MatchingEngineTests(APITestCase):

    def test_sbert_disabled_by_env(self):
        """SBERT_ENABLED=False → SBERT_AVAILABLE should be False."""
        self.assertFalse(SBERT_AVAILABLE)

    def test_bm25_available(self):
        self.assertTrue(BM25_AVAILABLE)

    def test_extract_skills_finds_known_skills(self):
        text = "Experience with Python, Django, PostgreSQL, and Docker."
        skills = extract_skills_from_text(text)
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertIn('postgresql', skills)
        self.assertIn('docker', skills)

    def test_extract_skills_handles_synonyms(self):
        text = "Worked with nodejs and sklearn."
        skills = extract_skills_from_text(text)
        self.assertIn('node', skills)
        self.assertIn('scikit-learn', skills)

    def test_compute_match_returns_positive_score(self):
        resume = (
            "Python developer, 3 years. Django, REST, PostgreSQL, Docker. "
            "Built recommendation systems with machine learning."
        )
        jd = "Looking for Python backend engineer with Django, REST, Docker."
        result = compute_match(resume, jd)
        self.assertGreater(result['match_score_pct'], 0)

    def test_compute_match_result_structure(self):
        result = compute_match("Python django developer", "Python developer needed")
        required_keys = [
            'match_score_pct', 'tfidf_score', 'bm25_score', 'sbert_score',
            'matched_skills', 'missing_skills', 'suggestions', 'engines_used',
        ]
        for key in required_keys:
            self.assertIn(key, result)

    def test_compute_match_score_in_range(self):
        result = compute_match("Python django developer", "Python developer needed")
        self.assertGreaterEqual(result['match_score_pct'], 0)
        self.assertLessEqual(result['match_score_pct'], 100)

    def test_compute_match_tfidf_score_in_range(self):
        result = compute_match("Python developer", "Python engineer")
        self.assertGreaterEqual(result['tfidf_score'], 0)
        self.assertLessEqual(result['tfidf_score'], 100)

    def test_compute_match_bm25_non_negative(self):
        """BM25 should never be negative (we clamp to 0)."""
        result = compute_match("completely unrelated text here", "python django javascript")
        self.assertGreaterEqual(result['bm25_score'], 0)

    def test_compute_match_sbert_zero_when_disabled(self):
        result = compute_match("Python developer", "Python engineer")
        self.assertEqual(result['sbert_score'], 0.0)
        self.assertFalse(result['engines_used']['sbert'])

    def test_compute_match_engines_used(self):
        result = compute_match("Python developer", "Python engineer")
        self.assertTrue(result['engines_used']['tfidf'])
        self.assertTrue(result['engines_used']['bm25'])

    def test_matched_and_missing_skills(self):
        resume = "Python Django developer"
        jd = "Python Django React developer"
        result = compute_match(resume, jd)
        self.assertIn('python', result['matched_skills'])
        self.assertIn('django', result['matched_skills'])
        self.assertIn('react', result['missing_skills'])

    def test_suggestions_generated_for_missing_skills(self):
        result = compute_match("Python developer", "Python React Django developer needed")
        self.assertTrue(len(result['suggestions']) > 0)

    def test_empty_texts_do_not_crash(self):
        result = compute_match("", "")
        self.assertIsInstance(result['match_score_pct'], float)

    def test_very_long_text_handled(self):
        long_text = "python django " * 500
        result = compute_match(long_text, "python developer")
        self.assertIsInstance(result['match_score_pct'], float)


# ════════════════════════════════════════════════════════════════════
# Resume Upload API Tests
# ════════════════════════════════════════════════════════════════════
class ResumeUploadTests(APITestCase):

    def setUp(self):
        self.seeker_user, self.seeker_profile = make_seeker('uploader1')
        self.client.force_authenticate(user=self.seeker_user)

    def test_unauthenticated_upload_rejected(self):
        self.client.logout()
        self.client.force_authenticate(user=None)
        url = reverse('resume-upload')
        dummy = SimpleUploadedFile("resume.txt", b"Python developer", content_type="text/plain")
        response = self.client.post(url, {'file': dummy}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_resumes_returns_empty_list_initially(self):
        url = reverse('my-resumes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


# ════════════════════════════════════════════════════════════════════
# Job Application API Tests
# ════════════════════════════════════════════════════════════════════
class JobApplicationTests(APITestCase):

    def setUp(self):
        self.seeker_user, self.seeker_profile = make_seeker('appseeker1')
        self.rec_user, self.rec_profile = make_recruiter('apprec1', 'AppCo')
        self.job = JobPosting.objects.create(
            recruiter=self.rec_profile,
            title='Python Dev',
            description='We need a Python developer with Django.',
            required_skills='python, django',
            status='ACTIVE',
        )

    def test_apply_without_resume_creates_application_with_zero_score(self):
        self.client.force_authenticate(user=self.seeker_user)
        url = reverse('job-apply')
        response = self.client.post(url, {'job_posting': self.job.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        app = JobApplication.objects.get(job_seeker=self.seeker_profile, job_posting=self.job)
        self.assertEqual(app.status, 'APPLIED')
        # No resume text → match score is 0
        self.assertEqual(float(app.match_score_pct), 0.0)

    def test_duplicate_application_rejected(self):
        self.client.force_authenticate(user=self.seeker_user)
        url = reverse('job-apply')
        self.client.post(url, {'job_posting': self.job.pk}, format='json')
        response = self.client.post(url, {'job_posting': self.job.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_apply_to_nonexistent_job_returns_404(self):
        self.client.force_authenticate(user=self.seeker_user)
        url = reverse('job-apply')
        response = self.client.post(url, {'job_posting': 99999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_applications_list(self):
        self.client.force_authenticate(user=self.seeker_user)
        url_apply = reverse('job-apply')
        self.client.post(url_apply, {'job_posting': self.job.pk}, format='json')
        url_list = reverse('my-applications')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_cannot_apply(self):
        url = reverse('job-apply')
        response = self.client.post(url, {'job_posting': self.job.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_apply_with_parsed_resume_text_generates_match_score(self):
        """When a resume with parsed text exists, compute_match is called."""
        self.client.force_authenticate(user=self.seeker_user)
        # Directly create a resume record with parsed_text (skip file upload)
        resume = UploadedResume.objects.create(
            job_seeker=self.seeker_profile,
            parsed_text="Python developer with Django, REST, and PostgreSQL experience.",
            extracted_skills="python, django, postgresql",
        )
        url = reverse('job-apply')
        response = self.client.post(
            url, {'job_posting': self.job.pk, 'resume': resume.pk}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        app = JobApplication.objects.get(job_seeker=self.seeker_profile, job_posting=self.job)
        # With relevant resume text and SBERT=False, TF-IDF+BM25 should produce > 0
        self.assertGreater(float(app.match_score_pct), 0)

    def test_recruiter_can_update_application_status(self):
        self.client.force_authenticate(user=self.seeker_user)
        url_apply = reverse('job-apply')
        resp = self.client.post(url_apply, {'job_posting': self.job.pk}, format='json')
        app_id = resp.data['id']

        self.client.force_authenticate(user=self.rec_user)
        url_status = reverse('update-app-status', kwargs={'pk': app_id})
        response = self.client.patch(url_status, {'status': 'SHORTLISTED'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SHORTLISTED')

    def test_invalid_status_rejected(self):
        self.client.force_authenticate(user=self.seeker_user)
        url_apply = reverse('job-apply')
        resp = self.client.post(url_apply, {'job_posting': self.job.pk}, format='json')
        app_id = resp.data['id']

        self.client.force_authenticate(user=self.rec_user)
        url_status = reverse('update-app-status', kwargs={'pk': app_id})
        response = self.client.patch(url_status, {'status': 'INVALID_STATUS'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
