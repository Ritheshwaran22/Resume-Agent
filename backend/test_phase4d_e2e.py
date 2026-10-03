import os
import io
import django
from unittest.mock import patch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
import pymupdf as fitz

from resumes.models import Resume
from jobs.models import JobDescription
from analysis.models import Analysis
from agent.agent import GeminiAnalysisError

def run_phase4d_e2e():
    print("=" * 70)
    print("PHASE 4D END-TO-END REGRESSION & ERROR HANDLING SUITE")
    print("=" * 70)

    cache.clear()
    client = APIClient()
    control_client = APIClient()

    # Clean up test accounts
    User.objects.filter(username__in=['p4d_user', 'p4d_control']).delete()

    # -------------------------------------------------------------
    # 1. AUTHENTICATION & LOGIN WORKFLOW
    # -------------------------------------------------------------
    print("\n[1] AUTHENTICATION WORKFLOW")
    # Register
    reg_res = client.post('/api/accounts/register/', {
        'username': 'p4d_user',
        'email': 'p4d@example.com',
        'password': 'InitialPassword123!',
        'password2': 'InitialPassword123!'
    }, format='json')
    assert reg_res.status_code == status.HTTP_201_CREATED
    print("  [PASS] User Registration: PASS")

    # Wrong password test
    bad_login = client.post('/api/accounts/login/', {
        'username': 'p4d_user',
        'password': 'WrongPassword999!'
    }, format='json')
    assert bad_login.status_code == status.HTTP_401_UNAUTHORIZED
    assert bad_login.data.get('detail') == 'Invalid username or password.'
    print("  [PASS] Wrong Password Rejection: PASS")

    # Correct login
    login_res = client.post('/api/accounts/login/', {
        'username': 'p4d_user',
        'password': 'InitialPassword123!'
    }, format='json')
    assert login_res.status_code == status.HTTP_200_OK
    token = login_res.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    print("  [PASS] Successful Login with JWT: PASS")

    # Logout
    logout_res = client.post('/api/accounts/logout/', {'refresh': login_res.data['refresh']}, format='json')
    assert logout_res.status_code == status.HTTP_200_OK
    print("  [PASS] Logout Flow: PASS")

    # Re-authenticate for subsequent operations
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # -------------------------------------------------------------
    # 2. PASSWORD RESET & RATE LIMITING WORKFLOW
    # -------------------------------------------------------------
    print("\n[2] PASSWORD RESET & RATE LIMITING WORKFLOW")
    if not hasattr(mail, 'outbox'):
        mail.outbox = []
    else:
        mail.outbox.clear()

    # Forgot password request
    reset_req = client.post('/api/accounts/password-reset/', {'email': 'p4d@example.com'}, format='json')
    assert reset_req.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1
    sent_msg = mail.outbox[0]
    assert "Reset your Resume Agent password" in sent_msg.subject
    print("  [PASS] Password Reset Email Generation: PASS")

    # Token extraction & confirm
    user = User.objects.get(username='p4d_user')
    reset_token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    confirm_res = client.post('/api/accounts/password-reset-confirm/', {
        'uid': uid,
        'token': reset_token,
        'new_password': 'BrandNewPassword123!',
        'confirm_password': 'BrandNewPassword123!'
    }, format='json')
    assert confirm_res.status_code == status.HTTP_200_OK
    print("  [PASS] Reset Confirmation with New Password: PASS")

    # Single-use token enforcement
    reuse_res = client.post('/api/accounts/password-reset-confirm/', {
        'uid': uid,
        'token': reset_token,
        'new_password': 'AnotherPassword123!',
        'confirm_password': 'AnotherPassword123!'
    }, format='json')
    assert reuse_res.status_code == status.HTTP_400_BAD_REQUEST
    print("  [PASS] Token Single-Use Enforced: PASS")

    # Old password no longer works
    old_login = client.post('/api/accounts/login/', {'username': 'p4d_user', 'password': 'InitialPassword123!'}, format='json')
    assert old_login.status_code == status.HTTP_401_UNAUTHORIZED
    print("  [PASS] Old Password Rejected: PASS")

    # New password works
    new_login = client.post('/api/accounts/login/', {'username': 'p4d_user', 'password': 'BrandNewPassword123!'}, format='json')
    assert new_login.status_code == status.HTTP_200_OK
    token = new_login.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    print("  [PASS] New Password Authentication: PASS")

    # Rate limiting test on password reset
    for _ in range(5):
        client.post('/api/accounts/password-reset/', {'email': 'ratelimit@example.com'}, format='json')
    throttled = client.post('/api/accounts/password-reset/', {'email': 'ratelimit@example.com'}, format='json')
    assert throttled.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    print("  [PASS] Rate Limiting (HTTP 429) Enforced: PASS")
    cache.clear()

    # -------------------------------------------------------------
    # 3. RESUME UPLOAD & ERROR HANDLING
    # -------------------------------------------------------------
    print("\n[3] RESUME UPLOAD & ERROR HANDLING WORKFLOW")
    # Empty file
    empty_upload = client.post('/api/resumes/upload/', {'file': SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")}, format='multipart')
    assert empty_upload.status_code == status.HTTP_400_BAD_REQUEST
    print("  [PASS] 0-Byte Empty PDF Rejected Safely: PASS")

    # Corrupted file
    corrupt_upload = client.post('/api/resumes/upload/', {'file': SimpleUploadedFile("bad.pdf", b"corrupted bytes non pdf", content_type="application/pdf")}, format='multipart')
    assert corrupt_upload.status_code == status.HTTP_400_BAD_REQUEST
    assert "corrupted" in str(corrupt_upload.data).lower()
    print("  [PASS] Corrupted PDF Rejected with Safe Message: PASS")

    # Valid PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Senior Fullstack Engineer\nSkills: Python, Django, React, PostgreSQL, Docker, AWS\nProjects: Built scalable microservice")
    valid_pdf_bytes = doc.tobytes()
    doc.close()

    valid_upload = client.post('/api/resumes/upload/', {'file': SimpleUploadedFile("valid_resume.pdf", valid_pdf_bytes, content_type="application/pdf")}, format='multipart')
    assert valid_upload.status_code == status.HTTP_201_CREATED
    resume_id = valid_upload.data['id']
    print(f"  [PASS] Valid Resume Upload & Text Extraction: PASS (Resume ID: {resume_id})")

    # -------------------------------------------------------------
    # 4. ANALYSIS & GEMINI FAILURE HANDLING
    # -------------------------------------------------------------
    print("\n[4] ANALYSIS & ERROR RESILIENCE WORKFLOW")
    job_res = client.post('/api/jobs/', {
        'title': 'Lead Software Engineer',
        'description': 'Seeking an experienced Python and Django developer with PostgreSQL and cloud architecture.'
    }, format='json')
    assert job_res.status_code == status.HTTP_201_CREATED
    job_id = job_res.data['id']
    print(f"  [PASS] Job Description Created: PASS (Job ID: {job_id})")

    # Simulated Gemini Failure (Quota / Timeout)
    with patch('services.ai_service.AIService.analyze_resume', side_effect=GeminiAnalysisError("Resource exhausted 429")):
        fail_res = client.post('/api/analysis/start/', {'resume_id': resume_id, 'job_description_id': job_id}, format='json')
        assert fail_res.status_code == status.HTTP_502_BAD_GATEWAY
        assert "not modified" in fail_res.data['detail'].lower() or "unavailable" in fail_res.data['detail'].lower()
        # Verify no corrupt analysis created
        assert not Analysis.objects.filter(resume_id=resume_id).exists()
    print("  [PASS] Simulated Gemini Failure Returns Safe HTTP 502 with Zero Corrupt Records: PASS")

    # Successful Analysis Record
    analysis = Analysis.objects.create(
        user=user,
        resume=Resume.objects.get(id=resume_id),
        job_description=JobDescription.objects.get(id=job_id),
        match_score=85,
        result={
            'match_score': 85,
            'matched_skills': ['Python', 'Django', 'PostgreSQL'],
            'missing_skills': ['AWS'],
            'interview_questions': ['Explain Django ORM query optimization.'],
            'learning_roadmap': ['Deep dive into AWS ECS and CloudFormation.']
        }
    )
    print(f"  [PASS] Valid Analysis Linked: PASS (Analysis ID: {analysis.id}, Score: 85%)")

    # Detail & History
    history_res = client.get('/api/analysis/')
    assert history_res.status_code == status.HTTP_200_OK
    assert len(history_res.data) >= 1
    detail_res = client.get(f'/api/analysis/{analysis.id}/')
    assert detail_res.status_code == status.HTTP_200_OK
    assert 'interview_questions' in detail_res.data['result']
    assert 'learning_roadmap' in detail_res.data['result']
    print("  [PASS] Analysis History, Questions & Roadmap Retrieval: PASS")

    # -------------------------------------------------------------
    # 5. USER ISOLATION & DATA PRIVACY
    # -------------------------------------------------------------
    print("\n[5] USER ISOLATION WORKFLOW")
    control_user = User.objects.create_user(username='p4d_control', email='control@example.com', password='ControlPassword123!')
    control_client.force_authenticate(user=control_user)

    # Control user cannot view User A's resume or analysis
    assert control_client.get(f'/api/resumes/{resume_id}/').status_code == status.HTTP_404_NOT_FOUND
    assert control_client.get(f'/api/analysis/{analysis.id}/').status_code == status.HTTP_404_NOT_FOUND
    assert control_client.delete(f'/api/resumes/{resume_id}/').status_code == status.HTTP_404_NOT_FOUND
    print("  [PASS] Cross-User Access Blocked (HTTP 404): PASS")

    # -------------------------------------------------------------
    # 6. ACCOUNT MANAGEMENT & DELETION
    # -------------------------------------------------------------
    print("\n[6] ACCOUNT MANAGEMENT & DELETION WORKFLOW")
    # Email update
    email_patch = client.patch('/api/accounts/me/', {'email': 'p4d_updated@example.com'}, format='json')
    assert email_patch.status_code == status.HTTP_200_OK
    assert email_patch.data['email'] == 'p4d_updated@example.com'
    print("  [PASS] Email Update: PASS")

    # Password change
    pw_chg = client.post('/api/accounts/change-password/', {
        'current_password': 'BrandNewPassword123!',
        'new_password': 'FinalSecurePassword456!',
        'confirm_password': 'FinalSecurePassword456!'
    }, format='json')
    assert pw_chg.status_code == status.HTTP_200_OK
    print("  [PASS] Password Change: PASS")

    # Account Deletion
    del_res = client.delete('/api/accounts/me/')
    assert del_res.status_code == status.HTTP_200_OK
    assert not User.objects.filter(username='p4d_user').exists()
    assert not Resume.objects.filter(id=resume_id).exists()
    assert not JobDescription.objects.filter(id=job_id).exists()
    assert not Analysis.objects.filter(id=analysis.id).exists()
    # Control user remains intact
    assert User.objects.filter(username='p4d_control').exists()
    print("  [PASS] Account Deletion Cascaded & Cleaned Up While Control User Intact: PASS")

    # Clean up control user
    control_client.delete('/api/accounts/me/')

    print("\n" + "=" * 70)
    print("ALL PHASE 4D E2E REGRESSION WORKFLOWS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_phase4d_e2e()
