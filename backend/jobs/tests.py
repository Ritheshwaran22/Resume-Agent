from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import JobDescription

class JobAPITests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="jobuser1", password="Password123!")
        self.user2 = User.objects.create_user(username="jobuser2", password="Password123!")
        self.client = APIClient()

    def test_create_and_list_job(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "Senior Backend Developer",
            "description": "Looking for a seasoned developer with Python, Django, PostgreSQL, Docker, and AWS experience."
        }
        response = self.client.post('/api/jobs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Senior Backend Developer")

        # List jobs
        list_response = self.client.get('/api/jobs/')
        self.assertEqual(len(list_response.data), 1)

    def test_prevent_cross_user_job_access(self):
        job1 = JobDescription.objects.create(
            user=self.user1,
            title="Private Role",
            description="Highly confidential job posting specifications for internal project."
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/jobs/{job1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
