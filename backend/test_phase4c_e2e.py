import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from resumes.models import Resume
from jobs.models import JobDescription
from analysis.models import Analysis

def run_phase4c_e2e():
    print("=" * 60)
    print("PHASE 4C END-TO-END VERIFICATION SUITE")
    print("=" * 60)

    client_a = APIClient()
    client_b = APIClient()

    # Clean up any leftover test users if they exist
    User.objects.filter(username__in=['e2e_user_a', 'e2e_user_b']).delete()

    # --- 1. Account workflow: Register User A and User B ---
    print("\n--- ACCOUNT WORKFLOW ---")
    reg_a = client_a.post('/api/accounts/register/', {
        'username': 'e2e_user_a',
        'email': 'usera_orig@example.com',
        'password': 'InitialPassword123!',
        'password2': 'InitialPassword123!'
    }, format='json')
    assert reg_a.status_code == status.HTTP_201_CREATED, f"User A registration failed: {reg_a.data}"
    print("[Step 1] Register User A: PASS")

    reg_b = client_b.post('/api/accounts/register/', {
        'username': 'e2e_user_b',
        'email': 'userb_control@example.com',
        'password': 'UserBPassword123!',
        'password2': 'UserBPassword123!'
    }, format='json')
    assert reg_b.status_code == status.HTTP_201_CREATED, f"User B registration failed: {reg_b.data}"
    print("[Step 1b] Register User B (Control): PASS")

    # --- 2. Log in ---
    login_a = client_a.post('/api/accounts/login/', {
        'username': 'e2e_user_a',
        'password': 'InitialPassword123!'
    }, format='json')
    assert login_a.status_code == status.HTTP_200_OK, f"User A login failed: {login_a.data}"
    token_a = login_a.data['access']
    client_a.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')
    print("[Step 2] Log in User A: PASS")

    login_b = client_b.post('/api/accounts/login/', {
        'username': 'e2e_user_b',
        'password': 'UserBPassword123!'
    }, format='json')
    assert login_b.status_code == status.HTTP_200_OK
    token_b = login_b.data['access']
    client_b.credentials(HTTP_AUTHORIZATION=f'Bearer {token_b}')
    print("[Step 2b] Log in User B: PASS")

    # --- 3. Open /settings (GET /api/accounts/me/) ---
    me_res = client_a.get('/api/accounts/me/')
    assert me_res.status_code == status.HTTP_200_OK, f"GET /api/accounts/me/ failed: {me_res.data}"
    print("[Step 3] Open /settings endpoint: PASS")

    # --- 4. Verify account information ---
    user_info = me_res.data
    assert user_info['username'] == 'e2e_user_a'
    assert user_info['email'] == 'usera_orig@example.com'
    assert 'date_joined' in user_info
    assert user_info['total_resumes'] == 0
    assert user_info['total_analyses'] == 0
    assert 'password' not in user_info
    print(f"[Step 4] Account info verified (Username: {user_info['username']}, Email: {user_info['email']}): PASS")

    # --- 5. Change email ---
    email_patch = client_a.patch('/api/accounts/me/', {'email': 'usera_updated@example.com'}, format='json')
    assert email_patch.status_code == status.HTTP_200_OK, f"Email update failed: {email_patch.data}"
    print("[Step 5] Change email: PASS")

    # --- 6. Verify the updated email appears ---
    me_after_email = client_a.get('/api/accounts/me/')
    assert me_after_email.status_code == status.HTTP_200_OK
    assert me_after_email.data['email'] == 'usera_updated@example.com'
    print(f"[Step 6] Updated email confirmed ({me_after_email.data['email']}): PASS")

    # --- 7. Change password ---
    pw_change = client_a.post('/api/accounts/change-password/', {
        'current_password': 'InitialPassword123!',
        'new_password': 'BrandNewPassword456!',
        'confirm_password': 'BrandNewPassword456!'
    }, format='json')
    assert pw_change.status_code == status.HTTP_200_OK, f"Password change failed: {pw_change.data}"
    assert 'tokens' in pw_change.data
    print("[Step 7] Change password: PASS")

    # --- 8. Log out / clear credentials ---
    client_a.credentials()
    print("[Step 8] Log out / clear credentials: PASS")

    # --- 9. Log in using the new password ---
    new_login = client_a.post('/api/accounts/login/', {
        'username': 'e2e_user_a',
        'password': 'BrandNewPassword456!'
    }, format='json')
    assert new_login.status_code == status.HTTP_200_OK, f"Login with new password failed: {new_login.data}"
    new_token_a = new_login.data['access']
    client_a.credentials(HTTP_AUTHORIZATION=f'Bearer {new_token_a}')
    print("[Step 9] Log in using new password: PASS")

    # --- 10. Confirm old password no longer works ---
    old_login = client_a.post('/api/accounts/login/', {
        'username': 'e2e_user_a',
        'password': 'InitialPassword123!'
    }, format='json')
    assert old_login.status_code == status.HTTP_401_UNAUTHORIZED, f"Old password should fail: {old_login.status_code}"
    print("[Step 10] Old password invalidated: PASS")

    # --- DATA WORKFLOW ---
    print("\n--- DATA WORKFLOW ---")
    # --- 11. Upload test resume ---
    import pymupdf as fitz
    doc_a = fitz.open()
    page_a = doc_a.new_page()
    page_a.insert_text((50, 50), "User A Resume\nSkills: Python, Django, React, Postgres")
    pdf_bytes_a = doc_a.tobytes()
    doc_a.close()

    resume_file_a = SimpleUploadedFile("usera_resume.pdf", pdf_bytes_a, content_type="application/pdf")
    upload_a = client_a.post('/api/resumes/upload/', {'file': resume_file_a}, format='multipart')
    assert upload_a.status_code == status.HTTP_201_CREATED, f"User A resume upload failed: {upload_a.data}"
    resume_id_a = upload_a.data['id']
    resume_obj_a = Resume.objects.get(id=resume_id_a)
    physical_path_a = resume_obj_a.file.name
    assert resume_obj_a.file.storage.exists(physical_path_a), "Physical resume file should exist on disk"
    print(f"[Step 11] Upload test resume: PASS (Resume ID: {resume_id_a}, File: {physical_path_a})")

    # Also upload a resume for User B to verify isolation
    doc_b = fitz.open()
    page_b = doc_b.new_page()
    page_b.insert_text((50, 50), "User B Resume\nSkills: Figma, Design Systems, Prototyping")
    pdf_bytes_b = doc_b.tobytes()
    doc_b.close()

    resume_file_b = SimpleUploadedFile("userb_resume.pdf", pdf_bytes_b, content_type="application/pdf")
    upload_b = client_b.post('/api/resumes/upload/', {'file': resume_file_b}, format='multipart')
    assert upload_b.status_code == status.HTTP_201_CREATED
    resume_id_b = upload_b.data['id']
    print(f"[Step 11b] Upload User B resume (Control): PASS (Resume ID: {resume_id_b})")

    # --- 12. Create test job description ---
    job_res_a = client_a.post('/api/jobs/', {
        'title': 'Senior Fullstack Engineer',
        'description': 'Python, Django, React, Postgres'
    }, format='json')
    assert job_res_a.status_code == status.HTTP_201_CREATED, f"Job creation failed: {job_res_a.data}"
    job_id_a = job_res_a.data['id']
    print(f"[Step 12] Create test job description: PASS (Job ID: {job_id_a})")

    job_res_b = client_b.post('/api/jobs/', {
        'title': 'Product Designer',
        'description': 'Figma, Design Systems'
    }, format='json')
    assert job_res_b.status_code == status.HTTP_201_CREATED
    job_id_b = job_res_b.data['id']
    print(f"[Step 12b] Create User B job (Control): PASS (Job ID: {job_id_b})")

    # --- 13. Create test analysis record ---
    user_a = User.objects.get(username='e2e_user_a')
    user_b = User.objects.get(username='e2e_user_b')
    analysis_a = Analysis.objects.create(
        user=user_a,
        resume=resume_obj_a,
        job_description=JobDescription.objects.get(id=job_id_a),
        match_score=88,
        result={'matched_skills': ['Python', 'Django'], 'missing_skills': ['Postgres']}
    )
    analysis_b = Analysis.objects.create(
        user=user_b,
        resume=Resume.objects.get(id=resume_id_b),
        job_description=JobDescription.objects.get(id=job_id_b),
        match_score=92,
        result={'matched_skills': ['Figma'], 'missing_skills': ['Prototyping']}
    )
    print(f"[Step 13] Test analyses created: PASS (Analysis A ID: {analysis_a.id}, Analysis B ID: {analysis_b.id})")

    # --- 14. Verify data appears correctly & counts in settings ---
    me_with_data = client_a.get('/api/accounts/me/')
    assert me_with_data.status_code == status.HTTP_200_OK
    assert me_with_data.data['total_resumes'] == 1
    assert me_with_data.data['total_analyses'] == 1
    print(f"[Step 14] Data verified in profile counts (Resumes: {me_with_data.data['total_resumes']}, Analyses: {me_with_data.data['total_analyses']}): PASS")

    # User isolation check before deletion
    iso_check_1 = client_a.get(f'/api/resumes/{resume_id_b}/')
    assert iso_check_1.status_code == status.HTTP_404_NOT_FOUND, "User A must not access User B resume"
    iso_check_2 = client_a.get(f'/api/analysis/{analysis_b.id}/')
    assert iso_check_2.status_code == status.HTTP_404_NOT_FOUND, "User A must not access User B analysis"
    print("[Isolation Check] Cross-user access rejected (HTTP 404): PASS")

    # --- DELETION WORKFLOW ---
    print("\n--- DELETION WORKFLOW ---")
    # --- 15. Open Settings ---
    me_pre_del = client_a.get('/api/accounts/me/')
    assert me_pre_del.status_code == status.HTTP_200_OK
    print("[Step 15] Open Settings prior to deletion: PASS")

    # --- 16. Navigate to Danger Zone & 17. Open delete confirmation & 18. Confirm deletion explicitly ---
    del_res = client_a.delete('/api/accounts/me/')
    assert del_res.status_code == status.HTTP_200_OK, f"Delete account failed: {del_res.data}"
    assert "permanently deleted" in del_res.data['message']
    print("[Steps 16-18] Explicit account deletion confirmed & executed: PASS")

    # --- 19. Verify the account is deleted ---
    assert not User.objects.filter(username='e2e_user_a').exists(), "User A should not exist in database"
    login_del = client_a.post('/api/accounts/login/', {'username': 'e2e_user_a', 'password': 'BrandNewPassword456!'})
    assert login_del.status_code == status.HTTP_401_UNAUTHORIZED, "Deleted user login must fail"
    print("[Step 19] Account deletion verified (User absent, login rejected): PASS")

    # --- 20. Verify deleted user's previous data is no longer accessible and physical files cleaned up ---
    assert not Resume.objects.filter(id=resume_id_a).exists(), "User A resume must be deleted"
    assert not JobDescription.objects.filter(id=job_id_a).exists(), "User A job must be deleted"
    assert not Analysis.objects.filter(id=analysis_a.id).exists(), "User A analysis must be deleted"
    assert not resume_obj_a.file.storage.exists(physical_path_a), "Physical resume file must be removed from disk"
    print(f"[Step 20] Deleted user data & physical file cleanup verified (File deleted: {physical_path_a}): PASS")

    # --- 21. Verify another test user's data remains intact ---
    assert User.objects.filter(username='e2e_user_b').exists(), "User B must still exist"
    assert Resume.objects.filter(id=resume_id_b).exists(), "User B resume must still exist"
    assert JobDescription.objects.filter(id=job_id_b).exists(), "User B job must still exist"
    assert Analysis.objects.filter(id=analysis_b.id).exists(), "User B analysis must still exist"

    me_b = client_b.get('/api/accounts/me/')
    assert me_b.status_code == status.HTTP_200_OK
    assert me_b.data['username'] == 'e2e_user_b'
    assert me_b.data['total_resumes'] == 1
    assert me_b.data['total_analyses'] == 1
    print("[Step 21] Control user B data & account completely intact: PASS")

    # Clean up User B
    client_b.delete('/api/accounts/me/')

    print("\n" + "=" * 60)
    print("ALL 21 PHASE 4C E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_phase4c_e2e()
