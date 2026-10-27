"""
Integration tests for the accounts / authentication API.
"""
import os
os.environ.setdefault('SBERT_ENABLED', 'False')

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import User, JobSeekerProfile, RecruiterProfile


class RegisterLoginTests(APITestCase):
    """Test user registration and login flows."""

    def test_register_job_seeker_success(self):
        url = reverse('register')
        data = {
            'username': 'seeker1',
            'email': 'seeker1@example.com',
            'password': 'TestPass123!',
            'role': 'JOB_SEEKER',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        # Profile should be created automatically
        user = User.objects.get(username='seeker1')
        self.assertEqual(user.role, 'JOB_SEEKER')
        self.assertTrue(JobSeekerProfile.objects.filter(user=user).exists())

    def test_register_recruiter_success(self):
        url = reverse('register')
        data = {
            'username': 'recruiter1',
            'email': 'recruiter1@example.com',
            'password': 'TestPass123!',
            'role': 'RECRUITER',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='recruiter1')
        self.assertTrue(RecruiterProfile.objects.filter(user=user).exists())

    def test_register_duplicate_username_fails(self):
        User.objects.create_user(username='existing', password='pass123', role='JOB_SEEKER')
        url = reverse('register')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'role': 'JOB_SEEKER',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password_fails(self):
        url = reverse('register')
        data = {'username': 'nopwd', 'role': 'JOB_SEEKER'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_returns_tokens(self):
        User.objects.create_user(username='loginuser', password='pass123', role='JOB_SEEKER')
        JobSeekerProfile.objects.get_or_create(user=User.objects.get(username='loginuser'))
        url = reverse('login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'pass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_fails(self):
        User.objects.create_user(username='badlogin', password='correct', role='JOB_SEEKER')
        url = reverse('login')
        response = self.client.post(url, {'username': 'badlogin', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_endpoint_requires_token(self):
        url = reverse('job_seeker_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_contains_role_and_username(self):
        """Custom token serializer adds role and username claims."""
        User.objects.create_user(username='roletest', password='pass123', role='RECRUITER')
        RecruiterProfile.objects.get_or_create(
            user=User.objects.get(username='roletest'),
            defaults={'company_name': 'TestCo'},
        )
        url = reverse('login')
        response = self.client.post(url, {'username': 'roletest', 'password': 'pass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Decode the access token to verify claims
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(response.data['access'])
        self.assertEqual(token.get('role'), 'RECRUITER')
        self.assertEqual(token.get('username'), 'roletest')
