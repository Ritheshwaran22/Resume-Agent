import os
import sys
import django

# Setup django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pymupdf as fitz
from agent.agent import ResumeAgent

def test_real_pdf_analysis():
    pdf_path = os.path.join(os.path.dirname(__file__), "media", "resumes", "Ritheshwaran_Resume_Updated.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    doc = fitz.open(pdf_path)
    resume_text = ""
    for page in doc:
        resume_text += page.get_text() + "\n"
    doc.close()

    print(f"Loaded real PDF: length {len(resume_text)} chars")
    agent = ResumeAgent()

    print("\n" + "="*50)
    print("TEST A: REAL PDF WITH INSUFFICIENT JD ('Full Stack Developer')")
    print("="*50)
    res_insufficient = agent.analyze(
        resume_text=resume_text,
        job_title="Full Stack Developer",
        job_description=""
    )

    print(f"Analysis Status: {res_insufficient['analysis_status']}")
    print(f"Match Score: {res_insufficient['match_score']}")
    print(f"Matched Skills: {res_insufficient['matched_skills']}")
    print(f"Missing Skills: {res_insufficient['missing_skills']}")
    print(f"Keywords Found: {res_insufficient['keywords_found']}")
    print(f"Learning Roadmap: {res_insufficient['learning_roadmap']}")
    print(f"Project Analysis Titles: {[p['project'] for p in res_insufficient['project_analysis']]}")
    print(f"Interview Question Categories: {list(res_insufficient['interview_questions'].keys())}")

    assert res_insufficient['analysis_status'] == 'insufficient_jd'
    assert res_insufficient['match_score'] is None
    assert res_insufficient['matched_skills'] == []
    assert res_insufficient['missing_skills'] == []
    assert res_insufficient['learning_roadmap'] == []
    assert 'FullStack' not in res_insufficient['keywords_found']
    assert 'Full Stack Developer' not in res_insufficient['keywords_found']
    for p in res_insufficient['project_analysis']:
        assert p['project'].strip().upper() != 'INTERNSHIP'
    assert 'Job-Specific Questions' not in res_insufficient['interview_questions']
    assert 'Resume-Based Questions' in res_insufficient['interview_questions']
    print(">>> TEST A PASSED: Insufficient JD handled correctly with null score, empty roadmap, clean project names.")

    print("\n" + "="*50)
    print("TEST B: REAL PDF WITH SUFFICIENT JD (Python, Django, React, Docker, AWS)")
    print("="*50)
    res_sufficient = agent.analyze(
        resume_text=resume_text,
        job_title="Full Stack Developer",
        job_description="Looking for a Full Stack Developer skilled in Python, Django, React, Docker, and AWS."
    )

    print(f"Analysis Status: {res_sufficient['analysis_status']}")
    print(f"Match Score: {res_sufficient['match_score']}%")
    print(f"Matched Skills: {res_sufficient['matched_skills']}")
    print(f"Missing Skills: {res_sufficient['missing_skills']}")
    print(f"Keywords Found: {res_sufficient['keywords_found']}")
    print(f"Learning Roadmap: {[r['title'] for r in res_sufficient['learning_roadmap']]}")
    print(f"Project Analysis: {[p['project'] for p in res_sufficient['project_analysis']]}")

    assert res_sufficient['analysis_status'] == 'complete'
    assert res_sufficient['match_score'] is not None
    assert 'Python' in res_sufficient['matched_skills']
    assert 'Django' in res_sufficient['matched_skills']
    assert 'Docker' in res_sufficient['missing_skills']
    assert 'AWS' in res_sufficient['missing_skills']
    # Ensure forbidden technologies are NOT added
    for forbidden in ['Redis', 'Kubernetes', 'CI/CD']:
        assert forbidden not in res_sufficient['matched_skills']
        assert forbidden not in res_sufficient['missing_skills']

    # Ensure roadmap only has missing skills from JD (Docker, AWS)
    roadmap_skills = []
    for item in res_sufficient['learning_roadmap']:
        roadmap_skills.extend(item.get('skills', []))
    print(f"Roadmap Skills: {roadmap_skills}")
    for sk in roadmap_skills:
        assert sk in ['Docker', 'AWS', 'React']

    # Ensure FullStack is NOT in keywords
    assert 'FullStack' not in res_sufficient['keywords_found']
    assert 'Full Stack Developer' not in res_sufficient['keywords_found']

    # Ensure INTERNSHIP is not in project titles
    for p in res_sufficient['project_analysis']:
        assert p['project'].strip().upper() != 'INTERNSHIP'

    print(">>> TEST B PASSED: Real PDF analysis adheres 100% to truthfulness, zero hallucination, and evidence grounding!")

    print("\n" + "="*50)
    print("TEST C: REAL PDF WITH BACKEND DEVELOPER JD (Required & Preferred Skills)")
    print("="*50)
    backend_jd = """
    We are looking for a Backend Developer.
    
    Required Skills:
    Python
    Django
    Django REST Framework
    REST APIs
    MySQL
    Git
    SQL
    API development

    Preferred Skills:
    FastAPI
    PostgreSQL
    Docker
    Redis
    Linux
    """
    res_backend = agent.analyze(
        resume_text=resume_text,
        job_title="Backend Developer",
        job_description=backend_jd
    )

    print(f"Analysis Status: {res_backend['analysis_status']}")
    print(f"Match Score: {res_backend['match_score']}%")
    print(f"Scoring Formula: {res_backend.get('scoring_formula')}")
    print(f"Required Skills Total: {res_backend.get('required_skills_total')}")
    print(f"Required Skills Matched: {res_backend.get('required_skills_matched')}")
    print(f"Required Skills Missing: {res_backend.get('required_skills_missing')}")
    print(f"Preferred Skills Total: {res_backend.get('preferred_skills_total')}")
    print(f"Preferred Skills Matched: {res_backend.get('preferred_skills_matched')}")
    print(f"Preferred Skills Missing: {res_backend.get('preferred_skills_missing')}")
    print(f"Keywords Found: {res_backend.get('keywords_found')}")
    print(f"Keywords Missing: {res_backend.get('keywords_missing')}")
    print(f"Skills Breakdown: {res_backend.get('skills_breakdown')}")
    print(f"Project Analysis: {[p['project'] for p in res_backend['project_analysis']]}")
    for p in res_backend['project_analysis']:
        print(f"  Project: {p['project']}")
        print(f"    Technologies: {p.get('technologies')}")
        print(f"    Improvements: {p.get('improvements')}")

    # Assertions
    # 1. Required vs Preferred separation
    for pref in ['FastAPI', 'PostgreSQL', 'Docker', 'Redis', 'Linux']:
        assert pref in res_backend.get('preferred_skills_missing', []), f"{pref} should be in preferred_skills_missing"
        assert pref not in res_backend.get('required_skills_missing', []), f"{pref} must NOT be in required_skills_missing"

    # 2. Score calculation check: matched / total required skills
    req_total = res_backend.get('required_skills_total', 0)
    req_matched = len(res_backend.get('required_skills_matched', []))
    expected_score = round((req_matched / req_total) * 100) if req_total > 0 else 0
    assert res_backend['match_score'] == expected_score, f"Expected {expected_score}%, got {res_backend['match_score']}%"

    # 3. SQL consistency check: SQL must not be simultaneously classified as found keyword and missing skill
    kw_found_lower = [k.lower() for k in res_backend.get('keywords_found', [])]
    skills_missing = res_backend.get('required_skills_missing', [])
    assert not ('sql' in kw_found_lower and 'SQL' in skills_missing), "SQL must not be both found in keywords and missing from skills!"

    # 4. Project improvement truthfulness: No recommendation to migrate database
    for p in res_backend['project_analysis']:
        for imp in p.get('improvements', []):
            assert "migrat" not in imp.lower(), f"Forbidden migration suggestion found: {imp}"
            assert "replace sqlite" not in imp.lower(), f"Forbidden replacement suggestion found: {imp}"

    print(">>> TEST C PASSED: Backend Developer JD passed all required/preferred separation, scoring, SQL consistency, and truthful project recommendations!")

if __name__ == '__main__':
    test_real_pdf_analysis()

