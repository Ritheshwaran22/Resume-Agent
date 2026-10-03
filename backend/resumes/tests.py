import io
import pymupdf as fitz
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Resume

def create_mock_pdf_bytes(text="John Doe Software Engineer Python Django REST APIs PostgreSQL Git"):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

class ResumeAPITests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="Password123!")
        self.user2 = User.objects.create_user(username="user2", password="Password123!")
        self.client = APIClient()

    def test_upload_valid_pdf_extracts_text(self):
        self.client.force_authenticate(user=self.user1)
        pdf_bytes = create_mock_pdf_bytes("Experienced Python and Django Developer building RESTful microservices.")
        uploaded_file = SimpleUploadedFile("resume.pdf", pdf_bytes, content_type="application/pdf")

        response = self.client.post('/api/resumes/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("extracted_text", response.data)
        self.assertIn("Python", response.data["extracted_text"])

        # Check DB
        resume = Resume.objects.get(id=response.data["id"])
        self.assertEqual(resume.user, self.user1)

    def test_upload_rejects_non_pdf(self):
        self.client.force_authenticate(user=self.user1)
        uploaded_file = SimpleUploadedFile("malicious.exe", b"executable bytes", content_type="application/octet-stream")
        response = self.client.post('/api/resumes/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_access_other_users_resume(self):
        # Create resume for user1
        pdf_bytes = create_mock_pdf_bytes()
        resume1 = Resume.objects.create(
            user=self.user1,
            filename="user1_resume.pdf",
            extracted_text="Python Django experience"
        )

        # User2 tries to retrieve user1's resume
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/resumes/{resume1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User2 lists resumes — should be empty
        list_response = self.client.get('/api/resumes/')
        self.assertEqual(len(list_response.data), 0)
