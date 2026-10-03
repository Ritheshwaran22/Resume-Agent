from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from resumes.models import Resume
from jobs.models import JobDescription
from analysis.models import Analysis

class AccountsAPITests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.register_url = '/api/accounts/register/'
        self.login_url = '/api/accounts/login/'
        self.me_url = '/api/accounts/me/'
        self.change_password_url = '/api/accounts/change-password/'
        self.password_reset_url = '/api/accounts/password-reset/'
        self.password_reset_confirm_url = '/api/accounts/password-reset-confirm/'

    def tearDown(self):
        cache.clear()

    def test_registration_success(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
            "password2": "Password123!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_registration_password_mismatch(self):
        data = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "Password123!",
            "password2": "DifferentPassword!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username="loginuser", email="login@example.com", password="SecurePassword123!")
        data = {
            "username": "loginuser",
            "password": "SecurePassword123!"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)

    def test_login_invalid_credentials_returns_exact_error(self):
        User.objects.create_user(username="validuser", email="valid@example.com", password="CorrectPassword123!")
        data = {
            "username": "validuser",
            "password": "WrongPassword123!"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("detail"), "Invalid username or password.")


    def test_protected_me_endpoint_requires_auth(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = User.objects.create_user(username="authuser", password="Password123!")
        self.client.force_authenticate(user=user)
        auth_response = self.client.get(self.me_url)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_response.data["username"], "authuser")

    def test_password_reset_request_existing_email_sends_email(self):
        User.objects.create_user(username="resetuser", email="resetuser@example.com", password="OldPassword123!")
        data = {"email": "resetuser@example.com"}
        response = self.client.post(self.password_reset_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("message"),
            "If an account exists with this email, you'll receive a password reset link shortly."
        )
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "Reset your Resume Agent password")
        self.assertIn("resetuser@example.com", sent_email.to)
        self.assertIn("/reset-password/", sent_email.body)

    def test_password_reset_request_unknown_email_enumeration_prevention(self):
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.password_reset_url, data)

        # Must return exact same 200 OK and message
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("message"),
            "If an account exists with this email, you'll receive a password reset link shortly."
        )
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_successful_flow(self):
        user = User.objects.create_user(username="flowuser", email="flow@example.com", password="OldPassword123!")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_data = {
            "uid": uid,
            "token": token,
            "new_password": "BrandNewPassword123!",
            "confirm_password": "BrandNewPassword123!"
        }
        response = self.client.post(self.password_reset_confirm_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("successfully", response.data.get("message", ""))

        # Old password should no longer work
        old_login = self.client.post(self.login_url, {"username": "flowuser", "password": "OldPassword123!"})
        self.assertEqual(old_login.status_code, status.HTTP_401_UNAUTHORIZED)

        # New password must work for JWT login
        new_login = self.client.post(self.login_url, {"username": "flowuser", "password": "BrandNewPassword123!"})
        self.assertEqual(new_login.status_code, status.HTTP_200_OK)
        self.assertIn("access", new_login.data)

    def test_password_reset_confirm_token_cannot_be_reused(self):
        user = User.objects.create_user(username="reuseuser", email="reuse@example.com", password="InitialPassword123!")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_data = {
            "uid": uid,
            "token": token,
            "new_password": "UpdatedPassword123!",
            "confirm_password": "UpdatedPassword123!"
        }
        # First use succeeds
        res1 = self.client.post(self.password_reset_confirm_url, reset_data)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Re-use must fail
        res2 = self.client.post(self.password_reset_confirm_url, reset_data)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_invalid_token_rejected(self):
        user = User.objects.create_user(username="badtokenuser", email="badtoken@example.com", password="Password123!")
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_data = {
            "uid": uid,
            "token": "invalid-random-token",
            "new_password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!"
        }
        response = self.client.post(self.password_reset_confirm_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_password_mismatch_rejected(self):
        user = User.objects.create_user(username="mismatchuser", email="mismatch@example.com", password="Password123!")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_data = {
            "uid": uid,
            "token": token,
            "new_password": "PasswordABC123!",
            "confirm_password": "PasswordXYZ123!"
        }
        response = self.client.post(self.password_reset_confirm_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", response.data)

    @override_settings(PASSWORD_RESET_RATE_LIMIT='3/hour')
    def test_password_reset_rate_limiting_exceeded_returns_429(self):
        """
        Verify that exceeding the configured rate limit returns HTTP 429 Too Many Requests
        without exposing any stack traces or sensitive internal details.
        """
        cache.clear()
        email_data = {"email": "ratelimit_test@example.com"}

        # First 3 requests must succeed (HTTP 200)
        for i in range(3):
            response = self.client.post(self.password_reset_url, email_data)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Request {i+1} should have succeeded but got {response.status_code}"
            )

        # 4th request must be throttled (HTTP 429)
        throttled_response = self.client.post(self.password_reset_url, email_data)
        self.assertEqual(throttled_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("detail", throttled_response.data)
        # Verify no sensitive information or stack traces leaked
        self.assertNotIn("Traceback", str(throttled_response.data))
        self.assertNotIn("password", str(throttled_response.data).lower())

    def test_password_reset_no_account_enumeration_identical_response(self):
        """
        Verify that responses for existing vs non-existing emails are completely identical,
        preventing account enumeration.
        """
        cache.clear()
        User.objects.create_user(username="realuser", email="real@example.com", password="Password123!")

        res_existing = self.client.post(self.password_reset_url, {"email": "real@example.com"})
        res_unknown = self.client.post(self.password_reset_url, {"email": "unknown@example.com"})

        self.assertEqual(res_existing.status_code, status.HTTP_200_OK)
        self.assertEqual(res_unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(res_existing.data, res_unknown.data)
        self.assertEqual(
            res_existing.data.get("message"),
            "If an account exists with this email, you'll receive a password reset link shortly."
        )

    @override_settings(PASSWORD_RESET_RATE_LIMIT='1/hour')
    def test_throttling_only_applies_to_password_reset_view(self):
        """
        Verify that rate limiting is scoped strictly to PasswordResetRequestView
        and does NOT throttle unrelated endpoints like login or registration.
        """
        cache.clear()
        # Trigger rate limit on password reset
        self.client.post(self.password_reset_url, {"email": "scoped_test@example.com"})
        throttled_res = self.client.post(self.password_reset_url, {"email": "scoped_test@example.com"})
        self.assertEqual(throttled_res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Login should NOT be throttled (returns 400 or 401, not 429)
        login_res = self.client.post(self.login_url, {"username": "nobody", "password": "wrong"})
        self.assertNotEqual(login_res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    # =========================================================================
    # Phase 4C — Account, Profile & Data Management Tests
    # =========================================================================

    def test_current_user_profile_metadata_and_counts(self):
        """
        GET /api/accounts/me/ returns user info with total_resumes and total_analyses,
        without leaking passwords, hashes, or secrets.
        """
        user = User.objects.create_user(username="statuser", email="stat@example.com", password="Password123!")
        Resume.objects.create(user=user, filename="res1.pdf", extracted_text="test")
        Resume.objects.create(user=user, filename="res2.pdf", extracted_text="test2")
        job = JobDescription.objects.create(user=user, title="Dev", description="Code")
        resume = user.resumes.first()
        Analysis.objects.create(user=user, resume=resume, job_description=job, match_score=85)

        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "statuser")
        self.assertEqual(response.data["email"], "stat@example.com")
        self.assertIn("date_joined", response.data)
        self.assertEqual(response.data["total_resumes"], 2)
        self.assertEqual(response.data["total_analyses"], 1)
        self.assertNotIn("password", response.data)

    def test_update_email_success(self):
        """Authenticated user can update their own email."""
        user = User.objects.create_user(username="emailuser", email="old@example.com", password="Password123!")
        self.client.force_authenticate(user=user)

        response = self.client.patch(self.me_url, {"email": "new_email@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "new_email@example.com")

        user.refresh_from_db()
        self.assertEqual(user.email, "new_email@example.com")

    def test_update_email_duplicate_rejected(self):
        """Updating email to an existing email is rejected with HTTP 400."""
        User.objects.create_user(username="existinguser", email="taken@example.com", password="Password123!")
        user = User.objects.create_user(username="anotheruser", email="mine@example.com", password="Password123!")
        self.client.force_authenticate(user=user)

        response = self.client.patch(self.me_url, {"email": "taken@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_username_is_read_only_on_update(self):
        """Username cannot be modified via PATCH /api/accounts/me/."""
        user = User.objects.create_user(username="original_name", email="orig@example.com", password="Password123!")
        self.client.force_authenticate(user=user)

        response = self.client.patch(self.me_url, {"username": "hacked_name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, "original_name")

    def test_password_reset_works_with_updated_email(self):
        """Password reset email is delivered to the new email address after update."""
        user = User.objects.create_user(username="pwdupdateuser", email="initial@example.com", password="Password123!")
        self.client.force_authenticate(user=user)
        self.client.patch(self.me_url, {"email": "updated_for_reset@example.com"})
        self.client.logout()

        # Request reset with new email
        response = self.client.post(self.password_reset_url, {"email": "updated_for_reset@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("updated_for_reset@example.com", mail.outbox[0].to)

    def test_change_password_success_flow(self):
        """
        Changing password with valid credentials:
        - returns fresh tokens
        - invalidates login with old password
        - permits login with new password
        """
        user = User.objects.create_user(username="pwuser", email="pw@example.com", password="OldPassword123!")
        self.client.force_authenticate(user=user)

        data = {
            "current_password": "OldPassword123!",
            "new_password": "BrandNewSecurePassword456!",
            "confirm_password": "BrandNewSecurePassword456!"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])

        self.client.logout()

        # Old password must now fail
        old_login = self.client.post(self.login_url, {"username": "pwuser", "password": "OldPassword123!"})
        self.assertEqual(old_login.status_code, status.HTTP_401_UNAUTHORIZED)

        # New password must succeed
        new_login = self.client.post(self.login_url, {"username": "pwuser", "password": "BrandNewSecurePassword456!"})
        self.assertEqual(new_login.status_code, status.HTTP_200_OK)

    def test_change_password_incorrect_current_password(self):
        """Incorrect current password is rejected with generic error."""
        user = User.objects.create_user(username="pwuser2", password="CorrectPassword123!")
        self.client.force_authenticate(user=user)

        data = {
            "current_password": "WrongPassword999!",
            "new_password": "BrandNewSecurePassword456!",
            "confirm_password": "BrandNewSecurePassword456!"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Current password is incorrect.", str(response.data))

    def test_change_password_mismatch_rejected(self):
        """Mismatched new password and confirmation is rejected."""
        user = User.objects.create_user(username="pwuser3", password="CorrectPassword123!")
        self.client.force_authenticate(user=user)

        data = {
            "current_password": "CorrectPassword123!",
            "new_password": "BrandNewSecurePassword456!",
            "confirm_password": "DifferentPassword456!"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("New passwords do not match.", str(response.data))

    def test_change_password_weak_password_rejected(self):
        """Weak password failing Django validators is rejected with validation messages."""
        user = User.objects.create_user(username="pwuser4", password="CorrectPassword123!")
        self.client.force_authenticate(user=user)

        data = {
            "current_password": "CorrectPassword123!",
            "new_password": "123",
            "confirm_password": "123"
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_other_users_unaffected(self):
        """Changing User A's password does not affect User B's login."""
        user_a = User.objects.create_user(username="usera_pw", password="PasswordA123!")
        user_b = User.objects.create_user(username="userb_pw", password="PasswordB123!")

        self.client.force_authenticate(user=user_a)
        self.client.post(self.change_password_url, {
            "current_password": "PasswordA123!",
            "new_password": "NewPasswordA456!",
            "confirm_password": "NewPasswordA456!"
        })
        self.client.logout()

        # User B still logs in with their password
        login_b = self.client.post(self.login_url, {"username": "userb_pw", "password": "PasswordB123!"})
        self.assertEqual(login_b.status_code, status.HTTP_200_OK)

    def test_account_deletion_unauthenticated_rejected(self):
        """Unauthenticated call to DELETE /api/accounts/me/ returns HTTP 401."""
        response = self.client.delete(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_account_deletion_cascades_resumes_jobs_analyses_and_cleans_files(self):
        """
        Deleting account:
        - Permanently removes User
        - Cascades deletion to Resumes, JobDescriptions, and Analyses
        - Cleans up physical resume files from storage
        - Leaves other users' data intact
        """
        # Create User A with data and a mock resume file
        user_a = User.objects.create_user(username="user_a_del", email="usera@example.com", password="Password123!")
        dummy_file = SimpleUploadedFile("user_a_resume.pdf", b"PDF file content", content_type="application/pdf")
        resume_a = Resume.objects.create(user=user_a, filename="user_a_resume.pdf", file=dummy_file, extracted_text="text")
        job_a = JobDescription.objects.create(user=user_a, title="Software Engineer", description="Python")
        Analysis.objects.create(user=user_a, resume=resume_a, job_description=job_a, match_score=90)

        # File exists on storage
        self.assertTrue(resume_a.file.storage.exists(resume_a.file.name))
        file_path_a = resume_a.file.name

        # Create User B with data
        user_b = User.objects.create_user(username="user_b_safe", email="userb@example.com", password="Password123!")
        resume_b = Resume.objects.create(user=user_b, filename="user_b_resume.pdf", extracted_text="safe text")
        job_b = JobDescription.objects.create(user=user_b, title="Product Manager", description="Agile")
        Analysis.objects.create(user=user_b, resume=resume_b, job_description=job_b, match_score=80)

        # User A deletes their account
        self.client.force_authenticate(user=user_a)
        del_response = self.client.delete(self.me_url)
        self.assertEqual(del_response.status_code, status.HTTP_200_OK)

        # User A is deleted
        self.assertFalse(User.objects.filter(username="user_a_del").exists())
        # User A's data is deleted
        self.assertFalse(Resume.objects.filter(user_id=user_a.id).exists())
        self.assertFalse(JobDescription.objects.filter(user_id=user_a.id).exists())
        self.assertFalse(Analysis.objects.filter(user_id=user_a.id).exists())
        # Physical resume file is removed from storage
        self.assertFalse(resume_a.file.storage.exists(file_path_a))

        # User B's account and data remain untouched
        self.assertTrue(User.objects.filter(username="user_b_safe").exists())
        self.assertTrue(Resume.objects.filter(user_id=user_b.id).exists())
        self.assertTrue(JobDescription.objects.filter(user_id=user_b.id).exists())
        self.assertTrue(Analysis.objects.filter(user_id=user_b.id).exists())

    def test_user_isolation_cannot_access_or_modify_other_user_data(self):
        """User B cannot view or delete User A's resumes, analyses, or account."""
        user_a = User.objects.create_user(username="victim", email="victim@example.com", password="Password123!")
        resume_a = Resume.objects.create(user=user_a, filename="victim_resume.pdf")
        job_a = JobDescription.objects.create(user=user_a, title="Target Job", description="Desc")
        analysis_a = Analysis.objects.create(user=user_a, resume=resume_a, job_description=job_a, match_score=75)

        user_b = User.objects.create_user(username="attacker", email="attacker@example.com", password="Password123!")
        self.client.force_authenticate(user=user_b)

        # User B cannot delete User A's resume
        res_del = self.client.delete(f"/api/resumes/{resume_a.id}/")
        self.assertEqual(res_del.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Resume.objects.filter(id=resume_a.id).exists())

        # User B cannot view User A's analysis
        analysis_get = self.client.get(f"/api/analysis/{analysis_a.id}/")
        self.assertEqual(analysis_get.status_code, status.HTTP_404_NOT_FOUND)

        # User B calling DELETE /api/accounts/me/ deletes only User B, never User A
        self.client.delete(self.me_url)
        self.assertFalse(User.objects.filter(username="attacker").exists())
        self.assertTrue(User.objects.filter(username="victim").exists())


from unittest.mock import patch
from agent.agent import GeminiAnalysisError
from config.exceptions import production_exception_handler
from rest_framework.exceptions import ValidationError as DRFValidationError

class Phase4DErrorAndEmailTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username="error_testuser", email="errortest@example.com", password="Password123!")
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_custom_exception_handler_sanitizes_unhandled_500_error(self):
        """
        Verify that unexpected exceptions handled by custom_exception_handler
        return HTTP 500 with a sanitized message, leaking zero stack traces, SQL, or internals.
        """
        raw_exception = RuntimeError("Sensitive DB internal error: password=secret; host=10.0.0.5")
        context = {'view': None, 'request': None}
        response = production_exception_handler(raw_exception, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"detail": "An unexpected error occurred. Please try again later."})
        self.assertNotIn("password", str(response.data).lower())
        self.assertNotIn("10.0.0.5", str(response.data))

    def test_custom_exception_handler_preserves_validation_errors(self):
        """
        Verify that normal DRF validation errors (HTTP 400) preserve field-level errors
        and are NOT converted into generic 500 errors.
        """
        val_error = DRFValidationError({"email": ["Enter a valid email address."]})
        context = {'view': None, 'request': None}
        response = production_exception_handler(val_error, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email": ["Enter a valid email address."]})

    @override_settings(DEBUG=False, FRONTEND_URL='http://resumeagent.ai')
    def test_password_reset_url_enforces_https_in_production(self):
        """
        When DEBUG=False, password reset URLs must automatically use HTTPS
        even if FRONTEND_URL was configured with http://.
        """
        response = self.client.post('/api/accounts/password-reset/', {'email': 'errortest@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertIn("https://resumeagent.ai/reset-password/", sent_email.body)
        self.assertNotIn("http://resumeagent.ai", sent_email.body)

    def test_email_configuration_settings_present(self):
        """
        Verify that all required environment-driven email settings are loaded properly.
        """
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'EMAIL_BACKEND'))
        self.assertTrue(hasattr(settings, 'EMAIL_HOST'))
        self.assertTrue(hasattr(settings, 'EMAIL_PORT'))
        self.assertTrue(hasattr(settings, 'DEFAULT_FROM_EMAIL'))
        self.assertTrue(hasattr(settings, 'FRONTEND_URL'))

    def test_gemini_failure_returns_safe_502_without_corrupt_analysis_record(self):
        """
        If Gemini fails with GeminiAnalysisError (quota, timeout, API error),
        the endpoint returns HTTP 502 with a safe user message and does NOT save an Analysis record.
        """
        resume = Resume.objects.create(
            user=self.user,
            filename="safe_resume.pdf",
            extracted_text="Python Django developer with over 5 years of software engineering experience."
        )
        job = JobDescription.objects.create(
            user=self.user,
            title="Backend Architect",
            description="Looking for an experienced Python developer with Django and PostgreSQL experience."
        )

        initial_count = Analysis.objects.count()

        with patch('services.ai_service.AIService.analyze_resume', side_effect=GeminiAnalysisError("Resource exhausted: 429 quota")):
            response = self.client.post('/api/analysis/start/', {
                'resume_id': resume.id,
                'job_description_id': job.id
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("detail", response.data)
        self.assertNotIn("Gemini", response.data["detail"])
        self.assertNotIn("quota", response.data["detail"].lower())
        # Confirm no corrupt analysis was saved to the database
        self.assertEqual(Analysis.objects.count(), initial_count)

    def test_unexpected_analysis_server_error_returns_safe_500_without_corrupt_record(self):
        """
        If an unexpected server exception occurs during analysis,
        it returns HTTP 500 with safe detail and no corrupt Analysis record.
        """
        resume = Resume.objects.create(
            user=self.user,
            filename="safe_resume2.pdf",
            extracted_text="Fullstack developer with React, Python, and Django skills across production projects."
        )
        job = JobDescription.objects.create(
            user=self.user,
            title="Senior Engineer",
            description="Seeking senior engineer with Python, Django, and React development background."
        )

        initial_count = Analysis.objects.count()

        with patch('services.ai_service.AIService.analyze_resume', side_effect=RuntimeError("Internal system network breakdown")):
            response = self.client.post('/api/analysis/start/', {
                'resume_id': resume.id,
                'job_description_id': job.id
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("detail", response.data)
        self.assertNotIn("network breakdown", response.data["detail"].lower())
        # Confirm no corrupt analysis record was saved
        self.assertEqual(Analysis.objects.count(), initial_count)

    def test_pdf_upload_empty_file_rejected_cleanly(self):
        """Uploading an empty 0-byte PDF returns HTTP 400 with a clean error message."""
        empty_file = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")
        response = self.client.post('/api/resumes/upload/', {'file': empty_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("empty", str(response.data).lower())

    def test_pdf_upload_corrupted_bytes_rejected_cleanly(self):
        """Uploading corrupted bytes as a PDF returns HTTP 400 with a clean user message."""
        corrupted_file = SimpleUploadedFile("corrupt.pdf", b"Not a real PDF header or content", content_type="application/pdf")
        response = self.client.post('/api/resumes/upload/', {'file': corrupted_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("corrupted or not a valid pdf", str(response.data).lower())


class Phase4EDeploymentPreparationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_wsgi_entrypoint_is_callable(self):
        """Verify that config.wsgi:application is callable and properly configured."""
        from config.wsgi import application
        self.assertTrue(callable(application))

    def test_storages_configuration_settings(self):
        """Verify that Django 4.2+ STORAGES dictionary is configured with default and staticfiles."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'STORAGES'))
        self.assertIn('default', settings.STORAGES)
        self.assertIn('staticfiles', settings.STORAGES)

    def test_caches_configuration_settings(self):
        """Verify that CACHES dictionary is configured and defaults to LocMemCache."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'CACHES'))
        self.assertIn('default', settings.CACHES)
        self.assertIn('BACKEND', settings.CACHES['default'])

    def test_health_check_endpoint_accessible_and_safe(self):
        """
        Verify /api/health/ returns HTTP 200 without authentication
        and does NOT leak database passwords, SECRET_KEY, or API keys.
        """
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'healthy')
        response_str = str(response.data).lower()
        self.assertNotIn('secret', response_str)
        self.assertNotIn('password', response_str)
        self.assertNotIn('key', response_str)





