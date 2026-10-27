"""
Integration tests for the Jobs API.
"""
import os
os.environ.setdefault('SBERT_ENABLED', 'False')

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User, RecruiterProfile, JobSeekerProfile
from jobs.models import JobPosting


def make_recruiter(username='rec1', company='TestCo'):
    user = User.objects.create_user(username=username, password='pass123', role='RECRUITER')
    profile, _ = RecruiterProfile.objects.get_or_create(user=user, defaults={'company_name': company})
    return user, profile


def make_seeker(username='seek1'):
    user = User.objects.create_user(username=username, password='pass123', role='JOB_SEEKER')
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return user, profile


class JobListTests(APITestCase):

    def setUp(self):
        self.rec_user, self.rec_profile = make_recruiter()
        JobPosting.objects.create(
            recruiter=self.rec_profile,
            title='Backend Engineer',
            description='Django, PostgreSQL, REST APIs.',
            required_skills='python, django, postgresql',
            status='ACTIVE',
        )
        JobPosting.objects.create(
            recruiter=self.rec_profile,
            title='Draft Job',
            description='Not visible.',
            required_skills='java',
            status='DRAFT',
        )

    def test_unauthenticated_can_list_active_jobs(self):
        """GET /api/jobs/ is public (IsAuthenticatedOrReadOnly)."""
        url = reverse('job-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [j['title'] for j in response.data]
        self.assertIn('Backend Engineer', titles)
        self.assertNotIn('Draft Job', titles)

    def test_authenticated_seeker_can_list_jobs(self):
        seeker_user, _ = make_seeker()
        self.client.force_authenticate(user=seeker_user)
        url = reverse('job-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(user=self.rec_user)
        url = reverse('job-list-create')
        data = {
            'title': 'New Job',
            'description': 'Looking for a Python developer.',
            'required_skills': 'python, docker',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Job')

    def test_unauthenticated_cannot_create_job(self):
        url = reverse('job-list-create')
        data = {'title': 'Hack', 'description': 'x', 'required_skills': 'x'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recruiter_jobs_view_returns_own_jobs(self):
        self.client.force_authenticate(user=self.rec_user)
        url = reverse('recruiter-jobs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include both ACTIVE and DRAFT
        self.assertEqual(len(response.data), 2)

    def test_job_detail_get(self):
        job = JobPosting.objects.filter(status='ACTIVE').first()
        url = reverse('job-detail', kwargs={'pk': job.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], job.title)
