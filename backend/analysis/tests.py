import re
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from resumes.models import Resume
from jobs.models import JobDescription
from .models import Analysis
from agent.tools.skill_normalization import (
    find_skill_evidence,
    normalize_skill_name,
    extract_skills_from_text
)
from agent.tools.resume_tools import extract_resume_entities
from agent.tools.analysis_tools import compare_resume_and_job, calculate_deterministic_match_score
from agent.agent import ResumeAgent
from agent.schemas import ResumeAnalysisOutput

class AnalysisAPITests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="anauser1", password="Password123!")
        self.user2 = User.objects.create_user(username="anauser2", password="Password123!")
        self.client = APIClient()

        self.resume1 = Resume.objects.create(
            user=self.user1,
            filename="backend_resume.pdf",
            extracted_text="John Doe. Senior Software Engineer with strong experience in Python, Django, REST APIs, PostgreSQL, and Git."
        )

        self.job1 = JobDescription.objects.create(
            user=self.user1,
            title="Senior Python Backend Engineer",
            description="We are looking for a Senior Python / Django developer with PostgreSQL, Docker, AWS, and Redis experience."
        )

    def test_start_analysis_success(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "resume_id": self.resume1.id,
            "job_description_id": self.job1.id
        }
        response = self.client.post('/api/analysis/start/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("match_score", response.data)
        self.assertIn("result", response.data)
        self.assertIn("matched_skills", response.data["result"])
        self.assertIn("missing_skills", response.data["result"])
        self.assertIn("interview_questions", response.data["result"])
        self.assertIn("learning_roadmap", response.data["result"])

        # Check that Python, Django, PostgreSQL are in matched_skills
        self.assertIn("Python", response.data["result"]["matched_skills"])
        self.assertIn("Django", response.data["result"]["matched_skills"])
        self.assertIn("PostgreSQL", response.data["result"]["matched_skills"])

        # PostgreSQL must NEVER be in missing_skills
        self.assertNotIn("PostgreSQL", response.data["result"]["missing_skills"])

    def test_prevent_cross_user_analysis(self):
        # User2 tries to run analysis using User1's resume
        self.client.force_authenticate(user=self.user2)
        data = {
            "resume_id": self.resume1.id,
            "job_description_id": self.job1.id
        }
        response = self.client.post('/api/analysis/start/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_analyses_user_isolation(self):
        Analysis.objects.create(
            user=self.user1,
            resume=self.resume1,
            job_description=self.job1,
            match_score=75,
            result={"status": "ok"}
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/analysis/')
        self.assertEqual(len(response.data), 0)

class TruthfulAnalysisGroundingTests(TestCase):
    def test_realistic_matching_and_missing_skills(self):
        """
        Tests the exact realistic scenario specified in requirements:
        Resume: Python, Django, FastAPI, PostgreSQL, React, Docker
        JD: Python, Django, PostgreSQL, Docker, AWS, Redis, Kubernetes
        Expected:
          Matched: Python, Django, PostgreSQL, Docker
          Missing: AWS, Redis, Kubernetes
          AWS, Redis, Kubernetes MUST NOT be classified as matched.
        """
        resume_text = "Skills: Python, Django, FastAPI, PostgreSQL, React, Docker. Developed web applications."
        jd_title = "Senior Cloud Backend Engineer"
        jd_desc = "Seeking engineer proficient in Python, Django, PostgreSQL, Docker, AWS, Redis, and Kubernetes."

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        matched = set(result["matched_skills"])
        missing = set(result["missing_skills"])

        # Verify matched skills
        self.assertIn("Python", matched)
        self.assertIn("Django", matched)
        self.assertIn("PostgreSQL", matched)
        self.assertIn("Docker", matched)

        # Verify missing skills
        self.assertIn("AWS", missing)
        self.assertIn("Redis", missing)
        self.assertIn("Kubernetes", missing)

        # Strict negation checks: missing skills must not be in matched
        self.assertNotIn("AWS", matched)
        self.assertNotIn("Redis", matched)
        self.assertNotIn("Kubernetes", matched)

        # Matched skills must not be in missing
        self.assertNotIn("Python", missing)
        self.assertNotIn("Django", missing)
        self.assertNotIn("PostgreSQL", missing)
        self.assertNotIn("Docker", missing)

    def test_skill_alias_matching(self):
        """
        Tests alias resolution:
        Resume has 'Postgres' and 'RESTful APIs'.
        JD has 'PostgreSQL' and 'REST APIs'.
        Expected: Both match to canonical names without being reported missing.
        """
        resume_text = "Proficient in Postgres database management and building RESTful APIs with Git."
        jd_title = "Backend Developer"
        jd_desc = "Must know PostgreSQL and REST APIs."

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        matched = result["matched_skills"]
        missing = result["missing_skills"]

        self.assertIn("PostgreSQL", matched)
        self.assertIn("REST APIs", matched)
        self.assertNotIn("PostgreSQL", missing)
        self.assertNotIn("REST APIs", missing)

    def test_no_sentence_fragments_as_projects(self):
        """
        Verifies that random sentence fragments like 'vision applications to high-impact projects.'
        are strictly rejected and never treated as project titles.
        """
        resume_text = (
            "John Doe\n"
            "Summary\n"
            "Delivered vision applications to high-impact projects.\n"
            "Skills: Python, Django\n"
        )
        entities = extract_resume_entities(resume_text)
        project_titles = [p['title'] for p in entities['projects']]

        self.assertNotIn("vision applications to high-impact projects.", project_titles)
        self.assertNotIn("Delivered vision applications to high-impact projects.", project_titles)

    def test_guardrails_prevent_false_claims(self):
        """
        Verifies that the guardrail corrects false claims:
        - If raw AI claimed Docker was matched when it is not in the resume, it is moved to missing.
        - If raw AI claimed PostgreSQL was missing when it is in the resume, it is moved to matched.
        """
        resume_text = "Experienced in Python, Django, PostgreSQL."
        jd_title = "Backend Dev"
        jd_desc = "Must know Python, Django, PostgreSQL, and Docker."

        # Simulate a hallucinated or flawed raw AI response
        flawed_ai_result = {
            "match_score": 35,
            "overview": "Flawed overview",
            "matched_skills": ["Python", "Docker"],  # Docker is hallucinated
            "missing_skills": ["PostgreSQL"],       # PostgreSQL is falsely marked missing
            "keywords_found": ["Containerization"],
            "keywords_missing": ["Microservices"],
            "project_analysis": [{
                "project": "vision applications to high-impact projects.",
                "technologies": ["Docker"]
            }],
            "resume_strengths": ["Strong production engineering experience"],
            "resume_weaknesses": ["Docker is missing"],
            "resume_suggestions": [],
            "interview_questions": {},
            "learning_roadmap": []
        }

        job_reqs = {'required_skills': ['Python', 'Django', 'PostgreSQL', 'Docker']}
        corrected = ResumeAgent.enforce_truthfulness_guardrails(
            raw_result=flawed_ai_result,
            resume_text=resume_text,
            job_title=jd_title,
            job_description=jd_desc,
            job_requirements=job_reqs
        )

        # Docker must NOT be matched (it's not in the resume)
        self.assertNotIn("Docker", corrected["matched_skills"])
        self.assertIn("Docker", corrected["missing_skills"])

        # PostgreSQL MUST be matched (it IS in the resume)
        self.assertIn("PostgreSQL", corrected["matched_skills"])
        self.assertNotIn("PostgreSQL", corrected["missing_skills"])

        # Project title must have been sanitized
        sanitized_title = corrected["project_analysis"][0]["project"]
        self.assertNotEqual(sanitized_title, "vision applications to high-impact projects.")

    def test_deterministic_score_is_reproducible(self):
        """
        Verifies that running analysis twice on the same resume and JD
        produces the exact same score.
        """
        matched = ["Python", "Django", "PostgreSQL"]
        total_reqs = ["Python", "Django", "PostgreSQL", "Docker", "AWS"]
        kw_found = ["API", "Backend"]
        kw_missing = ["Cloud"]

        score1 = calculate_deterministic_match_score(matched, total_reqs, kw_found, kw_missing)
        score2 = calculate_deterministic_match_score(matched, total_reqs, kw_found, kw_missing)

        self.assertEqual(score1, score2)
        # 3 of 5 skills matched (60% * 0.80 = 48%) + 2 of 3 kw (67% * 0.20 = 13%) -> 61%
        self.assertTrue(55 <= score1 <= 65)

    def test_case_1_insufficient_jd(self):
        """
        TEST 1:
        Resume: Python, Django, PostgreSQL, React
        JD: Full Stack Developer (no tech requirements)
        Expected:
          status = "insufficient_jd"
          score = None
          matched_skills = []
          missing_skills = []
          roadmap = []
        """
        resume_text = "Experienced Developer with skills in Python, Django, PostgreSQL, and React."
        jd_title = "Full Stack Developer"
        jd_desc = ""

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertEqual(result["analysis_status"], "insufficient_jd")
        self.assertIsNone(result["match_score"])
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["learning_roadmap"], [])

    def test_case_2_sufficient_jd_with_missing_skills(self):
        """
        TEST 2:
        Resume: Python, Django, PostgreSQL, React
        JD: Full Stack Developer
        Required Skills: Python, Django, PostgreSQL, React, Docker, AWS
        Expected:
          Matched: Python, Django, PostgreSQL, React
          Missing: Docker, AWS
          Roadmap: Docker, AWS (Nothing else!)
        """
        resume_text = "Proficient in Python, Django, PostgreSQL, React. Built several full-stack web applications."
        jd_title = "Full Stack Developer"
        jd_desc = "Required Skills:\nPython\nDjango\nPostgreSQL\nReact\nDocker\nAWS"

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertEqual(result["analysis_status"], "complete")
        self.assertIsNotNone(result["match_score"])
        self.assertEqual(sorted(result["matched_skills"]), ["Django", "PostgreSQL", "Python", "React"])
        self.assertEqual(sorted(result["missing_skills"]), ["AWS", "Docker"])

        roadmap_skills = []
        for item in result["learning_roadmap"]:
            roadmap_skills.extend(item.get("skills", []))
        self.assertEqual(sorted(roadmap_skills), ["AWS", "Docker"])

    def test_case_3_paragraph_jd_all_matched(self):
        """
        TEST 3:
        Resume: Python, Django, PostgreSQL, REST APIs
        JD: Full Stack Developer
        The candidate should build web applications using Python and Django,
        develop REST APIs, and work with PostgreSQL.
        Expected:
          Matched: Python, Django, PostgreSQL, REST APIs
          Missing: []
        """
        resume_text = "Developed applications using Python, Django, PostgreSQL, and REST APIs."
        jd_title = "Full Stack Developer"
        jd_desc = "The candidate should build web applications using Python and Django, develop REST APIs, and work with PostgreSQL."

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertEqual(result["analysis_status"], "complete")
        self.assertIsNotNone(result["match_score"])
        self.assertEqual(sorted(result["matched_skills"]), ["Django", "PostgreSQL", "Python", "REST APIs"])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["learning_roadmap"], [])

    def test_case_4_no_hallucinated_technologies(self):
        """
        TEST 4:
        Resume: Python, Django
        JD: Full Stack Developer
        Required: Python, Django, React, Docker, AWS
        Expected:
          Matched: Python, Django
          Missing: React, Docker, AWS
        The analyzer must NOT add Redis, Kubernetes, CI/CD, or any other technology.
        """
        resume_text = "Backend developer working with Python and Django."
        jd_title = "Full Stack Developer"
        jd_desc = "Required:\nPython\nDjango\nReact\nDocker\nAWS"

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertEqual(sorted(result["matched_skills"]), ["Django", "Python"])
        self.assertEqual(sorted(result["missing_skills"]), ["AWS", "Docker", "React"])

        # Must NOT contain Redis, Kubernetes, CI/CD
        for forbidden in ["Redis", "Kubernetes", "CI/CD"]:
            self.assertNotIn(forbidden, result["matched_skills"])
            self.assertNotIn(forbidden, result["missing_skills"])

        # Roadmap must only contain missing skills
        roadmap_skills = []
        for item in result["learning_roadmap"]:
            roadmap_skills.extend(item.get("skills", []))
        for r_skill in roadmap_skills:
            self.assertIn(r_skill, ["AWS", "Docker", "React"])

    def test_internship_not_extracted_as_project(self):
        """
        Verifies that 'INTERNSHIP' is not extracted as a project, and
        actual project names ('Smart File Organiser', 'Virtual Hand Gesture Mouse')
        are preserved.
        """
        resume_text = """
PROJECTS
Smart File Organiser | Python, Django, PostgreSQL
Developed an automated file classification utility with custom tagging.

Virtual Hand Gesture Mouse | Python, OpenCV
Created a computer vision based mouse controller using hand landmark tracking.

INTERNSHIP
Python Developer Intern at ABC Corp
Worked on backend APIs.
"""
        agent = ResumeAgent()
        result = agent.analyze(
            resume_text=resume_text,
            job_title="Full Stack Developer",
            job_description="Looking for Python, Django, PostgreSQL, and Docker."
        )
        project_titles = [p["project"] for p in result["project_analysis"]]
        for t in project_titles:
            self.assertNotEqual(t.strip().upper(), "INTERNSHIP")
        self.assertTrue(any("Smart File Organiser" in t for t in project_titles))
        self.assertTrue(any("Virtual Hand Gesture Mouse" in t for t in project_titles))

    def test_required_vs_preferred_skill_separation(self):
        """Area 1: Verify clear separation of required and preferred skills."""
        resume_text = "Proficient in Python, Django, MySQL, Git, REST APIs, and backend APIs."
        jd_title = "Backend Developer"
        jd_desc = """
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
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertIn("required_skills_matched", result)
        self.assertIn("required_skills_missing", result)
        self.assertIn("preferred_skills_matched", result)
        self.assertIn("preferred_skills_missing", result)

        # Check required matched
        self.assertIn("Python", result["required_skills_matched"])
        self.assertIn("Django", result["required_skills_matched"])
        self.assertIn("MySQL", result["required_skills_matched"])
        self.assertIn("Git", result["required_skills_matched"])

        # Check required missing (DRF, SQL)
        self.assertIn("Django REST Framework", result["required_skills_missing"])

        # Preferred skills must NOT be in required_skills_missing
        for pref in ["FastAPI", "PostgreSQL", "Docker", "Redis", "Linux"]:
            self.assertNotIn(pref, result["required_skills_missing"])
            self.assertIn(pref, result["preferred_skills_missing"])

    def test_required_skill_scoring_deterministic(self):
        """Area 2: Required skill score = matched required / total required."""
        matched = ["Python", "Django", "MySQL", "Git"]
        total_reqs = ["Python", "Django", "MySQL", "Git", "SQL"]
        score = calculate_deterministic_match_score(matched, total_reqs, keywords_found=[], keywords_missing=[])
        # 4 / 5 = 80%
        self.assertEqual(score, 80)

    def test_sql_mentioned_but_not_demonstrated(self):
        """Area 3: SQL explicitly present in Skills section but not in projects."""
        resume_text = """
TECHNICAL SKILLS
Languages: Python, SQL
Framework: Django
PROJECTS
Smart File Organiser | Python, Django
Automated file sorting utility.
"""
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPython\nDjango\nSQL"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertIn("SQL", result["required_skills_matched"])
        self.assertIn("SQL", result["matched_skills"])
        self.assertNotIn("SQL", result["required_skills_missing"])
        self.assertNotIn("SQL", result["missing_skills"])
        self.assertIn("SQL", result["skills_mentioned"])
        self.assertNotIn("SQL", result["skills_demonstrated"])

    def test_sql_explicitly_demonstrated(self):
        """Area 4: SQL explicitly demonstrated in project text."""
        resume_text = """
PROJECTS
Data Pipeline | Python, SQL
Wrote complex SQL queries to aggregate database records and filter reporting data.
"""
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPython\nSQL"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertIn("SQL", result["required_skills_matched"])
        self.assertIn("SQL", result["skills_demonstrated"])
        self.assertNotIn("SQL", result["missing_skills"])

    def test_django_rest_framework_vs_generic_rest_apis(self):
        """Area 5: Django != DRF, REST APIs != DRF."""
        resume_text = "Proficient in Python, Django, and developing REST APIs."
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPython\nDjango REST Framework"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertNotIn("Django REST Framework", result["matched_skills"])
        self.assertIn("Django REST Framework", result["missing_skills"])

    def test_postgresql_vs_mysql_distinction(self):
        """Area 6: MySQL != PostgreSQL."""
        resume_text = "Experienced in MySQL database management."
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPostgreSQL"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertNotIn("PostgreSQL", result["matched_skills"])
        self.assertIn("PostgreSQL", result["missing_skills"])

    def test_docker_vs_kubernetes_distinction(self):
        """Area 7: Docker != Kubernetes."""
        resume_text = "Containerized applications with Docker."
        jd_title = "DevOps Engineer"
        jd_desc = "Required Skills:\nKubernetes"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertNotIn("Kubernetes", result["matched_skills"])
        self.assertIn("Kubernetes", result["missing_skills"])

    def test_project_technology_evidence(self):
        """Area 8: Project technologies must be verified against actual project section only."""
        resume_text = """
TECHNICAL SKILLS
Database: MySQL, SQLite
Tools: Docker

PROJECTS
Smart File Organiser | Python, Django, SQLite
Maintained activity logs in SQLite database.
"""
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPython\nDjango\nMySQL\nDocker"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        p = result["project_analysis"][0]
        # Project should contain Python, Django, SQLite - NOT Docker or MySQL
        self.assertIn("SQLite", p["technologies"])
        self.assertNotIn("Docker", p["technologies"])
        self.assertNotIn("MySQL", p["technologies"])

    def test_no_fabricated_project_enhancements(self):
        """Area 9: Do not recommend migrating database from SQLite to MySQL or fabricating deficiencies."""
        resume_text = """
PROJECTS
Smart File Organiser | Python, Django, SQLite
Created file management application with SQLite database.
"""
        jd_title = "Backend Developer"
        jd_desc = "Required Skills:\nPython\nDjango\nMySQL\nREST APIs"
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        p = result["project_analysis"][0]
        imp_lower = p["improvements"].lower()
        # Must NOT recommend migrating SQLite to MySQL
        self.assertNotIn("migrate", imp_lower)
        self.assertNotIn("switch from sqlite", imp_lower)

    def test_no_preferred_skill_penalty_in_required_score(self):
        """Area 10: Missing preferred skills must not penalize required score."""
        resume_text = "Proficient in Python, Django, MySQL, Git."
        jd_title = "Backend Developer"
        jd_desc = """
Required Skills:
Python
Django
MySQL
Git

Preferred Skills:
FastAPI
PostgreSQL
Docker
Redis
Linux
"""
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        # 4/4 required skills matched -> 100%
        self.assertEqual(result["match_score"], 100)
        self.assertEqual(len(result["required_skills_missing"]), 0)
        self.assertEqual(len(result["preferred_skills_missing"]), 5)

    def test_consistent_keyword_and_skill_classification(self):
        """Area 11: No skill in both matched and missing; substring 'sql' in 'mysql' does not trigger SQL keyword found."""
        resume_text = "Experienced in MySQL database management."
        jd_title = "Backend Developer"
        jd_desc = """
Required Skills:
Python
Django
SQL
"""
        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        # SQL is absent from resume (only MySQL is present)
        self.assertIn("SQL", result["missing_skills"])
        self.assertNotIn("SQL", result["matched_skills"])

        # SQL must NOT appear in keywords_found
        self.assertNotIn("SQL", result["keywords_found"])
        self.assertNotIn("sql", [k.lower() for k in result["keywords_found"]])

    def test_insufficient_jd_behavior_preserved(self):
        """Area 12: Existing insufficient-JD behavior preserved."""
        resume_text = "Experienced Developer with skills in Python, Django, PostgreSQL, and React."
        jd_title = "Full Stack Developer"
        jd_desc = ""

        agent = ResumeAgent()
        result = agent.analyze(resume_text=resume_text, job_title=jd_title, job_description=jd_desc)

        self.assertEqual(result["analysis_status"], "insufficient_jd")
        self.assertIsNone(result["match_score"])
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["learning_roadmap"], [])


class Phase2ADashboardAndHistoryTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="p2user1", password="Password123!")
        self.user2 = User.objects.create_user(username="p2user2", password="Password123!")
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

        self.resume1 = Resume.objects.create(
            user=self.user1,
            filename="user1_resume.pdf",
            extracted_text="Python, Django, MySQL, Git"
        )
        self.resume2 = Resume.objects.create(
            user=self.user2,
            filename="user2_resume.pdf",
            extracted_text="Java, Spring Boot"
        )

        self.job1 = JobDescription.objects.create(
            user=self.user1,
            title="Backend Developer",
            description="Required: Python, Django, MySQL, Git. Preferred: Docker"
        )

        self.analysis1 = Analysis.objects.create(
            user=self.user1,
            resume=self.resume1,
            job_description=self.job1,
            match_score=62,
            result={
                "analysis_status": "complete",
                "match_score": 62,
                "scoring_formula": "match_score = round((5 / 8) * 100)",
                "required_skills_total": 8,
                "required_skills_matched": ["Django", "Git", "MySQL", "Python", "REST APIs"],
                "required_skills_missing": ["API Development", "Django REST Framework", "SQL"],
                "preferred_skills_total": 5,
                "preferred_skills_matched": [],
                "preferred_skills_missing": ["Docker", "FastAPI", "Linux", "PostgreSQL", "Redis"],
                "skills_demonstrated": ["Django", "Python"],
                "skills_mentioned": ["Git", "MySQL", "REST APIs"],
                "skills_breakdown": [
                    {"skill": "Python", "category": "required", "status": "matched", "mentioned": True, "demonstrated": "Yes"},
                    {"skill": "Django", "category": "required", "status": "matched", "mentioned": True, "demonstrated": "Yes"},
                    {"skill": "Git", "category": "required", "status": "matched", "mentioned": True, "demonstrated": "Unclear"},
                ]
            }
        )

    def test_analysis_history_retrieval(self):
        """1. Analysis history retrieval returns correct structure and counts."""
        response = self.client1.get('/api/analysis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        item = response.data[0]
        self.assertEqual(item["id"], self.analysis1.id)
        self.assertEqual(item["job_title"], "Backend Developer")
        self.assertEqual(item["resume_filename"], "user1_resume.pdf")
        self.assertEqual(item["match_score"], 62)
        self.assertEqual(item["analysis_status"], "complete")
        self.assertEqual(item["required_skills_matched_count"], 5)
        self.assertEqual(item["required_skills_missing_count"], 3)
        self.assertEqual(item["required_skills_total_count"], 8)

    def test_analysis_detail_retrieval(self):
        """2. Analysis detail retrieval returns full stored analysis data."""
        response = self.client1.get(f'/api/analysis/{self.analysis1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.analysis1.id)
        self.assertEqual(response.data["job_title"], "Backend Developer")
        self.assertEqual(response.data["resume_filename"], "user1_resume.pdf")
        self.assertEqual(response.data["result"]["match_score"], 62)
        self.assertEqual(len(response.data["result"]["required_skills_matched"]), 5)

    def test_user_cannot_access_another_user_analysis(self):
        """3. User A cannot view User B's analyses (detail and list)."""
        # Detail view isolation
        response = self.client2.get(f'/api/analysis/{self.analysis1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # List view isolation
        response_list = self.client2.get('/api/analysis/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 0)

    def test_user_cannot_access_another_user_resume(self):
        """4. User A cannot view User B's resumes (detail and list)."""
        # Detail view isolation
        response = self.client2.get(f'/api/resumes/{self.resume1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # List view isolation: user2 only sees resume2
        response_list = self.client2.get('/api/resumes/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)
        self.assertEqual(response_list.data[0]["id"], self.resume2.id)

    def test_score_breakdown_uses_stored_backend_values(self):
        """5. Score breakdown is retrieved strictly from stored DB JSON values."""
        response = self.client1.get(f'/api/analysis/{self.analysis1.id}/')
        res = response.data["result"]
        self.assertEqual(res["match_score"], 62)
        self.assertEqual(res["scoring_formula"], "match_score = round((5 / 8) * 100)")
        self.assertEqual(res["required_skills_total"], 8)
        self.assertEqual(len(res["required_skills_matched"]), 5)
        self.assertEqual(len(res["required_skills_missing"]), 3)

    def test_required_and_preferred_skills_stored_separately(self):
        """6. Required and preferred skills are stored and served in distinct fields."""
        response = self.client1.get(f'/api/analysis/{self.analysis1.id}/')
        res = response.data["result"]
        self.assertIn("required_skills_matched", res)
        self.assertIn("required_skills_missing", res)
        self.assertIn("preferred_skills_matched", res)
        self.assertIn("preferred_skills_missing", res)
        for pref in res["preferred_skills_missing"]:
            self.assertNotIn(pref, res["required_skills_missing"])

    def test_existing_analysis_does_not_trigger_new_gemini_request(self):
        """7. Accessing analysis history or detail must never invoke Gemini / AIService."""
        from unittest.mock import patch
        with patch('services.ai_service.AIService.analyze_resume') as mock_ai:
            # Fetch list
            res_list = self.client1.get('/api/analysis/')
            self.assertEqual(res_list.status_code, status.HTTP_200_OK)
            # Fetch detail
            res_detail = self.client1.get(f'/api/analysis/{self.analysis1.id}/')
            self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
            # Ensure AI service was never called
            mock_ai.assert_not_called()

    def test_resume_deletion_respects_ownership(self):
        """8. Resume deletion respects user ownership; cross-user deletion is forbidden."""
        # User2 tries to delete User1's resume
        del_resp = self.client2.delete(f'/api/resumes/{self.resume1.id}/')
        self.assertEqual(del_resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Resume.objects.filter(id=self.resume1.id).exists())

        # User1 deletes own resume
        del_resp1 = self.client1.delete(f'/api/resumes/{self.resume1.id}/')
        self.assertEqual(del_resp1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resume.objects.filter(id=self.resume1.id).exists())

    def test_empty_states(self):
        """9. Empty states for new user with zero records."""
        new_user = User.objects.create_user(username="newbie", password="Password123!")
        client = APIClient()
        client.force_authenticate(user=new_user)

        res_resumes = client.get('/api/resumes/')
        self.assertEqual(res_resumes.status_code, status.HTTP_200_OK)
        self.assertEqual(res_resumes.data, [])

        res_analyses = client.get('/api/analysis/')
        self.assertEqual(res_analyses.status_code, status.HTTP_200_OK)
        self.assertEqual(res_analyses.data, [])

    def test_existing_insufficient_jd_behavior_persists(self):
        """10. Insufficient JD analysis persists null score and insufficient_jd status."""
        insufficient_analysis = Analysis.objects.create(
            user=self.user1,
            resume=self.resume1,
            job_description=self.job1,
            match_score=None,
            result={
                "analysis_status": "insufficient_jd",
                "match_score": None,
                "status_message": "The job description does not contain specific requirements.",
                "matched_skills": [],
                "missing_skills": [],
                "learning_roadmap": []
            }
        )
        response = self.client1.get(f'/api/analysis/{insufficient_analysis.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["match_score"])
        self.assertEqual(response.data["analysis_status"], "insufficient_jd")
        self.assertEqual(response.data["result"]["analysis_status"], "insufficient_jd")
        self.assertIsNone(response.data["result"]["match_score"])


class Phase2BInterviewQuestionsAndRoadmapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="p2buser", password="Password123!")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.resume_text = """
RITHESHWARAN
ritheshwaran@example.com | github.com/Ritheshwaran22

CAREER OBJECTIVE
Enthusiastic software developer proficient in Python, Django, REST APIs, and relational databases (MySQL, SQLite).

TECHNICAL SKILLS
Languages: Python, Git
Frameworks: Django, REST APIs
Databases: MySQL, SQLite
Libraries: OpenCV, MediaPipe, NumPy, pathlib, shutil

PROJECTS
Smart File Organiser | Python, Django, pathlib, shutil, SQLite
Automated desktop file classifier organizing files by extension with transaction history stored in SQLite.

Virtual Hand Gesture Mouse | Python, OpenCV, MediaPipe, NumPy
Computer vision based cursor controller translating hand landmarks into mouse movements and clicks.
"""

        self.backend_jd = """
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

    def test_1_resume_based_questions_use_actual_evidence(self):
        """1. Resume-based questions use actual resume evidence (Django, Python, Git) and do not invent Docker."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        questions = res["interview_questions"]["Resume-Based Questions"]
        self.assertTrue(3 <= len(questions) <= 5)

        q_texts = [q["question"] if isinstance(q, dict) else q for q in questions]
        all_q_text = " ".join(q_texts)

        # Must reference actual resume skills
        self.assertTrue(any(skill in all_q_text for skill in ["Django", "Python", "Git", "SQLite", "Smart File Organiser"]))
        # Must NOT ask about unverified skills like Docker in resume-based questions
        self.assertNotIn("Docker", all_q_text)
        self.assertNotIn("Kubernetes", all_q_text)

    def test_2_project_questions_reference_actual_projects(self):
        """2. Project questions reference actual projects (Smart File Organiser, Virtual Hand Gesture Mouse)."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        proj_q = res["interview_questions"]["Project Questions"]
        self.assertTrue(4 <= len(proj_q) <= 6)

        q_texts = [q["question"] if isinstance(q, dict) else q for q in proj_q]
        all_text = " ".join(q_texts)

        self.assertIn("Smart File Organiser", all_text)
        self.assertIn("Virtual Hand Gesture Mouse", all_text)
        self.assertTrue("MediaPipe" in all_text or "OpenCV" in all_text or "gesture" in all_text)

    def test_3_missing_skills_not_described_as_existing_experience(self):
        """3. Missing skills do not get described as existing experience."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        job_q = res["interview_questions"]["Job-Specific Questions"]
        q_texts = [q["question"] if isinstance(q, dict) else q for q in job_q]

        for q in q_texts:
            if "Django REST Framework" in q:
                self.assertTrue("Have you worked" in q or "approach learning" in q or "[Preparation" in q)
                self.assertNotIn("In your production Django REST Framework project", q)
            if "SQL" in q and "MySQL" not in q:
                self.assertTrue("Have you worked" in q or "transition" in q or "[Preparation" in q or "approach" in q)

    def test_4_job_specific_questions_use_actual_jd(self):
        """4. Job-specific questions use the actual JD."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        job_q = res["interview_questions"]["Job-Specific Questions"]
        self.assertTrue(5 <= len(job_q) <= 7)

        q_texts = [q["question"] if isinstance(q, dict) else q for q in job_q]
        all_text = " ".join(q_texts)

        self.assertTrue(any(s in all_text for s in ["Django REST Framework", "SQL", "API development", "Python", "MySQL"]))

    def test_5_preferred_skills_clearly_distinguished(self):
        """5. Preferred skills are clearly distinguished in questions and roadmap."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        # In questions:
        job_q = res["interview_questions"]["Job-Specific Questions"]
        preferred_skills = ["Docker", "FastAPI", "Redis", "Linux", "PostgreSQL"]
        for q in job_q:
            text = q["question"] if isinstance(q, dict) else q
            for pref in preferred_skills:
                if pref in text:
                    self.assertIn("[Preferred Skill]", text)

        # In roadmap:
        roadmap = res["learning_roadmap"]
        for item in roadmap:
            if item.get("skill") in preferred_skills:
                self.assertEqual(item.get("priority"), "preferred")

    def test_6_insufficient_jd_no_fabricated_job_specific_roadmap(self):
        """6. Insufficient JD produces no fabricated job-specific roadmap or job-specific questions."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Software Developer", job_description="")

        self.assertEqual(res["analysis_status"], "insufficient_jd")
        self.assertIsNone(res["match_score"])
        self.assertEqual(res["learning_roadmap"], [])
        self.assertNotIn("Job-Specific Questions", res["interview_questions"])
        self.assertIn("Resume-Based Questions", res["interview_questions"])

    def test_7_required_missing_skills_receive_roadmap_priority(self):
        """7. Required missing skills receive roadmap priority before preferred skills."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        roadmap = res["learning_roadmap"]
        self.assertTrue(len(roadmap) > 0)

        priorities = [item["priority"] for item in roadmap]
        # All 'required' items must appear before any 'preferred' item
        saw_preferred = False
        for p in priorities:
            if p == "preferred":
                saw_preferred = True
            if saw_preferred:
                self.assertNotEqual(p, "required", "Found a required skill after a preferred skill!")

        # First skills should be SQL / DRF / API Development
        first_skills = [item.get("skill") for item in roadmap[:3]]
        self.assertIn("SQL", first_skills)
        self.assertIn("Django REST Framework", first_skills)

    def test_8_preferred_skills_do_not_silently_become_mandatory(self):
        """8. Preferred skills do not silently become mandatory."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        # Match score must reflect strictly required skills (5/8 = 62%)
        self.assertEqual(res["match_score"], 62)
        for pref in ["Docker", "FastAPI", "Linux", "PostgreSQL", "Redis"]:
            self.assertNotIn(pref, res["required_skills_missing"])
            self.assertIn(pref, res["preferred_skills_missing"])

    def test_9_roadmap_uses_existing_projects(self):
        """9. Roadmap connects tasks to existing candidate projects as suggested practice / future enhancement."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        tasks = [item.get("practical_task", "") for item in res["learning_roadmap"]]
        all_tasks = " ".join(tasks)

        self.assertIn("Smart File Organiser", all_tasks)
        self.assertTrue("Suggested Practice" in all_tasks or "Future Project Enhancement" in all_tasks)

    def test_10_no_fabricated_project_technologies(self):
        """10. No fabricated project technologies in project analysis."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        file_org_proj = next((p for p in res["project_analysis"] if "Smart File Organiser" in p["project"]), None)
        self.assertIsNotNone(file_org_proj)
        self.assertIn("Django", file_org_proj["technologies"])
        self.assertIn("SQLite", file_org_proj["technologies"])
        self.assertNotIn("Docker", file_org_proj["technologies"])
        self.assertNotIn("MySQL", file_org_proj["technologies"])

    def test_11_historical_analyses_without_new_fields_still_render(self):
        """11. Historical analyses with plain string questions and legacy roadmap items still validate and serve."""
        legacy_data = {
            "analysis_status": "complete",
            "match_score": 75,
            "overview": "Legacy analysis output",
            "required_skills_matched": ["Python", "Django"],
            "required_skills_missing": ["Docker"],
            "interview_questions": {
                "Resume-Based Questions": [
                    "Can you explain your experience with Python?"
                ]
            },
            "learning_roadmap": [
                {
                    "week": "Week 1",
                    "title": "Mastering Docker Fundamentals",
                    "description": "Learn containerization basics.",
                    "skills": ["Docker"]
                }
            ]
        }
        output = ResumeAnalysisOutput(**legacy_data)
        dumped = output.model_dump()
        self.assertEqual(dumped["match_score"], 75)
        self.assertEqual(dumped["interview_questions"]["Resume-Based Questions"], ["Can you explain your experience with Python?"])
        self.assertEqual(dumped["learning_roadmap"][0]["title"], "Mastering Docker Fundamentals")

    def test_12_duplicate_questions_are_avoided(self):
        """12. Duplicate questions are avoided across all categories."""
        agent = ResumeAgent()
        res = agent.analyze(resume_text=self.resume_text, job_title="Backend Developer", job_description=self.backend_jd)

        seen = set()
        for cat, q_list in res["interview_questions"].items():
            for q in q_list:
                text = q["question"] if isinstance(q, dict) else q
                cleaned = re.sub(r'[^a-z0-9]', '', text.lower())
                self.assertNotIn(cleaned, seen, f"Duplicate question detected: {text}")
                seen.add(cleaned)




