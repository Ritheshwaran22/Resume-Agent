import requests
import json
import pymupdf as fitz
import io

BASE_URL = 'http://127.0.0.1:8000'

def run_e2e():
    print("=== STARTING FULL END-TO-END VERIFICATION ===")

    # 1. Health check
    res = requests.get(f"{BASE_URL}/api/health/")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[1/6] Health check: OK")

    # 2. Register user
    import random
    rand_num = random.randint(10000, 99999)
    username = f"e2e_user_{rand_num}"
    password = "SuperPassword123!"

    reg_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password,
        "password2": password
    }
    res = requests.post(f"{BASE_URL}/api/accounts/register/", json=reg_payload)
    assert res.status_code == 201, f"Registration failed: {res.text}"
    data = res.json()
    access_token = data["tokens"]["access"]
    print(f"[2/6] User registration: OK (Username: {username})")

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create PDF and upload resume
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Jane Doe - Lead Software Architect\n"
        "Skills: Python, Django, REST APIs, PostgreSQL, Git, Redis, Linux, System Design\n"
        "Projects: Built scalable inventory microservice using Django REST framework and PostgreSQL."
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("Jane_Doe_Resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    res = requests.post(f"{BASE_URL}/api/resumes/upload/", files=files, headers=headers)
    assert res.status_code == 201, f"Resume upload failed: {res.text}"
    resume_data = res.json()
    resume_id = resume_data["id"]
    assert "Python" in resume_data["extracted_text"]
    print(f"[3/6] Resume upload & PyMuPDF extraction: OK (Resume ID: {resume_id})")

    # 4. Create Job Description
    job_payload = {
        "title": "Senior Backend Engineer",
        "description": "Seeking an experienced Python and Django developer with PostgreSQL, Docker, AWS, and Redis experience."
    }
    res = requests.post(f"{BASE_URL}/api/jobs/", json=job_payload, headers=headers)
    assert res.status_code == 201, f"Job creation failed: {res.text}"
    job_data = res.json()
    job_id = job_data["id"]
    print(f"[4/6] Job Description created: OK (Job ID: {job_id})")

    # 5. Start Analysis via AI Resume Agent
    analysis_payload = {
        "resume_id": resume_id,
        "job_description_id": job_id
    }
    res = requests.post(f"{BASE_URL}/api/analysis/start/", json=analysis_payload, headers=headers)
    assert res.status_code == 201, f"Analysis start failed: {res.text}"
    analysis_data = res.json()
    analysis_id = analysis_data["id"]
    match_score = analysis_data["match_score"]
    result = analysis_data["result"]
    assert match_score > 0
    assert "matched_skills" in result
    assert "Python" in result["matched_skills"]
    assert "Django" in result["matched_skills"]
    assert "PostgreSQL" in result["matched_skills"]
    assert "Redis" in result["matched_skills"]

    assert "missing_skills" in result
    assert "AWS" in result["missing_skills"]
    assert "Docker" in result["missing_skills"]

    # Critical anti-hallucination checks
    assert "PostgreSQL" not in result["missing_skills"]
    assert "AWS" not in result["matched_skills"]
    assert "Docker" not in result["matched_skills"]

    assert "interview_questions" in result
    assert "learning_roadmap" in result
    print(f"[5/6] Resume Agent Analysis: OK (Score: {match_score}%, ID: {analysis_id})")
    print(f"      Matched: {result['matched_skills']}")
    print(f"      Missing: {result['missing_skills']}")

    # 6. List Analysis History & Detail
    res = requests.get(f"{BASE_URL}/api/analysis/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    res = requests.get(f"{BASE_URL}/api/analysis/{analysis_id}/", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == analysis_id
    print(f"[6/6] Analysis History & Detail Retrieval: OK")

    print("\n=== ALL END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_e2e()
