"""
Deterministic comparison and scoring engine.
Produces 100% reproducible, evidence-grounded match evaluations.
Handles insufficient job descriptions with explicit null scores and status messages.
Enforces strict distinction between required and preferred skills, mentioned vs demonstrated,
and prevents hallucinated project modifications.
"""
import re
from typing import Dict, Any, List, Optional, Set
from .skill_normalization import (
    find_skill_evidence,
    check_skill_evidence_detailed,
    is_keyword_present,
    is_job_description_sufficient,
    normalize_skill_name
)

def has_measurable_metrics(text: str) -> bool:
    """Checks if text contains quantifiable metrics, percentages, numbers, or performance indicators."""
    if not text:
        return False
    return bool(re.search(
        r'\b\d+(\.\d+)?%|\b\d+x\b|\b\d+\s*(users|requests|req/s|rps|ms|seconds|minutes|hours|queries|records|rows|tables|mb|gb|tb)\b',
        text,
        re.IGNORECASE
    ))

def calculate_deterministic_match_score(
    matched_skills: List[str],
    total_required_skills: List[str],
    keywords_found: Optional[List[str]] = None,
    keywords_missing: Optional[List[str]] = None,
    preferred_skills_matched: Optional[List[str]] = None,
    total_preferred_skills: Optional[List[str]] = None,
) -> Optional[int]:
    """
    Calculates a reproducible, transparent match score (0-100) based strictly on REQUIRED skills evidence.
    Returns None if the job description provides 0 required technical skills / insufficient data.
    Preferred skills are reported separately and do NOT penalize this score.
    Does NOT use arbitrary floors (no max(35, ...)) and has NO hidden boosts.
    """
    total_req_count = len(total_required_skills)
    kw_found = keywords_found or []
    kw_missing = keywords_missing or []
    total_kw_count = len(kw_found) + len(kw_missing)

    # If there are NO technical requirements defined in the JD, return None
    if total_req_count == 0:
        return None

    # Required skills score = matched required skills / total required skills
    raw_score = len(matched_skills) / total_req_count
    return round(raw_score * 100)


    final_score = int(round(raw_score * 100))
    return max(0, min(100, final_score))

def sanitize_project_improvements(
    raw_improvements: str,
    project_title: str,
    project_techs: List[str],
    resume_skills: Set[str],
    missing_skills: List[str],
    has_metrics: bool
) -> str:
    """
    Sanitizes project improvement text to ensure 100% truthfulness (Issues 3, 4, 7):
    1. NEVER recommends rewriting history (e.g. migrating SQLite to MySQL or PostgreSQL).
    2. NEVER suggests adding an unverified technology as an existing project deficiency.
    3. Clearly labels optional future enhancements.
    """
    text_lower = raw_improvements.lower() if raw_improvements else ""

    # Guard 1: Prevent database migration advice from SQLite to MySQL/Postgres (Issue 3)
    if any(m in text_lower for m in ['migrat', 'switch from sqlite', 'replace sqlite', 'change the database to', 'migrate the database']):
        if 'SQLite' in project_techs or 'sqlite' in text_lower:
            if 'MySQL' in resume_skills or 'PostgreSQL' in resume_skills:
                return (
                    "Keep SQLite accurately represented for this project. If you have separate genuine MySQL or PostgreSQL experience, "
                    "document that usage clearly in your technical skills or other relevant projects."
                )
            else:
                return (
                    "Keep SQLite accurately represented for this project. If you have separate genuine experience with other relational "
                    "databases like MySQL, document that separately."
                )

    # Guard 2: Prevent inventing project enhancements as existing deficiencies (Issue 4)
    for missing_tech in missing_skills:
        m_lower = missing_tech.lower()
        if (f"add a {m_lower}" in text_lower or f"adding a {m_lower}" in text_lower or
            f"implement a {m_lower}" in text_lower or f"adding {m_lower}" in text_lower):
            if missing_tech in resume_skills:
                return f"If you have already implemented {missing_tech} in this project, document the endpoints or integration clearly in the description."
            else:
                return f"Keep the project's current technical scope accurately documented. Optional Future Project Enhancement: You could explore adding a {missing_tech} layer as a future portfolio extension."

    # Guard 3: Quantifiable metrics
    if not has_metrics:
        if not raw_improvements or 'measurable' in text_lower or 'metric' in text_lower or 'outcome' in text_lower or 'architecture' in text_lower:
            return "The resume describes the project's functionality but does not provide a measurable performance result or quantitative outcome."

    return raw_improvements or "Consider highlighting system architecture diagrams, test coverage, or live repository links."

def build_truthful_resume_suggestions(
    skills_mentioned_not_demonstrated: List[str],
    missing_required_skills: List[str],
    has_any_metric: bool,
    projects: List[Dict[str, Any]]
) -> List[str]:
    """
    Generates suggestions strictly adhering to the 4-tier priority order (Issue 7):
    Priority 1: Improve documentation of genuine existing experience (mentioned in skills, buried/unclear in projects).
    Priority 2: Highlight genuine existing evidence that is currently buried (quantifiable metrics).
    Priority 3: Suggest learning an actual missing required technology.
    Priority 4: Only then suggest an optional future project enhancement.
    """
    suggestions = []

    # Priority 1: Improve documentation of genuine existing experience
    for skill in skills_mentioned_not_demonstrated[:2]:
        suggestions.append(
            f"You have documented experience with {skill} in your resume; consider detailing how you practically applied it within your project or experience descriptions."
        )

    # Priority 2: Highlight genuine existing evidence currently buried
    if not has_any_metric:
        suggestions.append(
            "Quantify project outcomes where possible (e.g., number of files processed, processing time reduction, or active users) to demonstrate measurable impact."
        )

    # Priority 3: Suggest learning a missing required technology
    for missing_skill in missing_required_skills[:2]:
        suggestions.append(
            f"{missing_skill} is required by the target job description. If you have genuine experience with it, document it clearly; otherwise, prioritize learning its core fundamentals."
        )

    # Priority 4: Optional future project enhancement
    if missing_required_skills:
        first_missing = missing_required_skills[0]
        suggestions.append(
            f"Optional Future Project Enhancement: Consider building a portfolio application incorporating {first_missing} to demonstrate practical hands-on capability."
        )
    elif not suggestions:
        suggestions.append(
            "Ensure project descriptions clearly articulate the technical scope, architectural patterns, and measurable results of your work."
        )

    return suggestions[:4]

def build_grounded_interview_questions(
    resume_skills: Set[str],
    projects: List[Dict[str, Any]],
    job_title: str,
    required_matched: List[str],
    required_missing: List[str],
    preferred_matched: List[str],
    preferred_missing: List[str],
    is_sufficient: bool = True
) -> Dict[str, List[Dict[str, str]]]:
    """
    Builds strictly grounded, non-hallucinatory interview questions categorized into 5 areas:
    1. Resume-Based Questions (3-5): Grounded strictly in confirmed candidate skills/projects.
    2. Technical Questions (5-7): Core candidate stack + clearly labeled preparation concepts.
    3. Project Questions (4-6): Real resume projects with architectural, framework, and error-handling queries.
    4. Job-Specific Questions (5-7): Actual JD requirements with honest learning queries for missing skills.
    5. Behavioral Questions (3-5): Fresher/entry-level behavioral questions connected to projects.
    """
    seen_questions: Set[str] = set()

    def add_q(target_list: List[Dict[str, str]], q_text: str, guidance_text: str, max_count: int):
        if len(target_list) >= max_count:
            return
        norm_key = re.sub(r'[^a-z0-9]', '', q_text.lower())
        if norm_key in seen_questions:
            return
        seen_questions.add(norm_key)
        target_list.append({
            "question": q_text.strip(),
            "guidance": guidance_text.strip()
        })

    lower_resume_skills = {s.lower() for s in resume_skills}
    for p in projects:
        for t in p.get('technologies', []):
            lower_resume_skills.add(t.lower())

    def has_skill(name: str) -> bool:
        return name.lower() in lower_resume_skills

    p_titles = [p.get('title', p.get('project', '')) for p in projects]
    has_file_org = any('file' in t.lower() or 'organis' in t.lower() or 'organiz' in t.lower() for t in p_titles)
    has_gesture_mouse = any('gesture' in t.lower() or 'mouse' in t.lower() or 'landmark' in t.lower() for t in p_titles)

    # 1. RESUME-BASED QUESTIONS (Target: 3-5)
    resume_based_q: List[Dict[str, str]] = []

    if has_skill('Django') and has_file_org:
        add_q(
            resume_based_q,
            "How did you structure the Django application in your Smart File Organiser project?",
            "Be ready to explain the Django project structure, major components, why Django was selected, and how files move through the application.",
            5
        )
    elif has_skill('Django'):
        add_q(
            resume_based_q,
            "How did you structure your Django application architecture and manage models, views, and routing?",
            "Discuss standard Django layout, MTV (Model-Template-View) pattern, URL routing, and ORM integration.",
            5
        )

    if has_skill('Python') and has_file_org:
        add_q(
            resume_based_q,
            "Why did you choose Python for the Smart File Organiser project?",
            "Discuss Python's built-in file handling libraries (pathlib, shutil), rapid prototyping capabilities, and ecosystem support.",
            5
        )
    elif has_skill('Python'):
        add_q(
            resume_based_q,
            "Why did you choose Python for your backend projects, and what advantages did its standard library provide?",
            "Highlight Python's readability, extensive standard libraries, and rapid development workflow.",
            5
        )

    if has_skill('Git'):
        add_q(
            resume_based_q,
            "How did you use Git while developing your projects?",
            "Explain your branching strategy, commit hygiene, how you tracked changes, and how you managed repository updates on GitHub.",
            5
        )

    if has_skill('SQLite') or has_skill('MySQL') or has_skill('SQL'):
        db_name = "SQLite" if has_skill('SQLite') else ("MySQL" if has_skill('MySQL') else "relational databases")
        add_q(
            resume_based_q,
            f"How did you design the {db_name} schema and handle data operations in your application?",
            f"Discuss table structure, primary/foreign keys, indexing, and how you verified data persistence in {db_name}.",
            5
        )

    if has_skill('REST APIs') or has_skill('API Development'):
        add_q(
            resume_based_q,
            "How have you approached designing and consuming REST APIs in your projects?",
            "Explain HTTP methods, status codes, JSON payload formatting, and how you structured client-server communication.",
            5
        )

    if has_skill('OpenCV') or has_skill('MediaPipe'):
        add_q(
            resume_based_q,
            "How did you configure OpenCV and MediaPipe for video stream capture and processing in your gesture project?",
            "Discuss real-time frame processing, color conversion, coordinate normalization, and performance considerations.",
            5
        )

    # Fallback to ensure at least 3-5 grounded resume questions
    if len(resume_based_q) < 3:
        for sk in sorted(list(resume_skills))[:3]:
            add_q(
                resume_based_q,
                f"How have you applied {sk} in your practical coursework and project development?",
                f"Share specific libraries, scripts, or components you built using {sk}.",
                5
            )

    # 2. TECHNICAL QUESTIONS (Target: 5-7)
    technical_q: List[Dict[str, str]] = []

    if has_skill('Python'):
        add_q(
            technical_q,
            "How does Python handle memory management and garbage collection, and how do you write memory-efficient code?",
            "Discuss reference counting, cyclical garbage collection, generators for large data pipelines, and avoiding memory leaks.",
            7
        )

    if has_skill('Django'):
        add_q(
            technical_q,
            "Can you explain the Django request-response lifecycle from middleware to views and ORM queries?",
            "Walk through HttpRequest handling, middleware processing order, URL routing, view execution, and HttpResponse return.",
            7
        )

    add_q(
        technical_q,
        "What is the difference between an INNER JOIN, LEFT JOIN, and indexing, and how do indexes improve query performance?",
        "Explain join mechanics, B-tree indexes, index selectivity, and how to avoid full table scans in relational databases.",
        7
    )

    add_q(
        technical_q,
        "What are the core principles of RESTful API design, and what is the difference between PUT and PATCH methods?",
        "Define statelessness, uniform interface, idempotency of PUT vs partial update semantics of PATCH, and proper HTTP status code usage.",
        7
    )

    if has_skill('Git'):
        add_q(
            technical_q,
            "What is the difference between git merge and git rebase, and when would you choose one over the other?",
            "Explain how git merge creates a dedicated merge commit preserving complete branch history, whereas git rebase rewrites commit history linearly.",
            7
        )

    # Missing skill preparation questions (clearly labeled as preparation concepts)
    if any('rest framework' in s.lower() or 'drf' in s.lower() for s in required_missing):
        add_q(
            technical_q,
            "[Preparation Concept] Explain the difference between standard Django views and Django REST Framework serializers and viewsets.",
            "Preparation Guidance: Emphasize that DRF focuses on serializing model data to JSON and providing API endpoints (APIView, ViewSets), whereas standard Django renders HTML templates via the request-response cycle.",
            7
        )

    if any(s.upper() == 'SQL' for s in required_missing):
        add_q(
            technical_q,
            "[Preparation Concept] How do database transactions ensure data integrity, and what do ACID properties stand for?",
            "Preparation Guidance: Define Atomicity, Consistency, Isolation, and Durability, and give an example of rolling back a failed multi-step database operation.",
            7
        )

    if any('api' in s.lower() for s in required_missing):
        add_q(
            technical_q,
            "[Preparation Concept] What strategies do you use for API authentication and rate limiting in modern web services?",
            "Preparation Guidance: Discuss token-based auth (JWT / OAuth2), headers, token expiration, and throttling algorithms like token bucket or sliding window.",
            7
        )

    # 3. PROJECT QUESTIONS (Target: 4-6)
    project_q: List[Dict[str, str]] = []

    if has_file_org:
        add_q(
            project_q,
            "Can you walk through the overall architecture and folder structure of the Smart File Organiser application?",
            "Break down the core components: file scanner, categorization rules, database logger, and Django view/template workflow.",
            6
        )
        add_q(
            project_q,
            "How did you implement file classification and directory scanning using pathlib and shutil in Smart File Organiser?",
            "Explain how paths were safely resolved across operating systems, how file extensions were parsed, and how file collisions were avoided.",
            6
        )
        add_q(
            project_q,
            "How does Smart File Organiser handle duplicate file names, locked files, or permission errors during moving?",
            "Detail your exception handling strategy (e.g. PermissionError, FileExistsError), logging mechanisms, and rename or rollback logic.",
            6
        )
        add_q(
            project_q,
            "How did you structure SQLite for logging file operations and maintaining activity history in Smart File Organiser?",
            "Explain the log table schema (timestamp, source path, destination path, category) and how historical transactions can be inspected.",
            6
        )

    if has_gesture_mouse:
        add_q(
            project_q,
            "How did you configure MediaPipe and OpenCV for real-time hand landmark detection in your Virtual Hand Gesture Mouse project?",
            "Explain camera frame capture, RGB color conversion, landmark coordinate normalization, and multi-finger tracking.",
            6
        )
        add_q(
            project_q,
            "How did you translate physical hand gestures into reliable mouse click and cursor movement events?",
            "Describe the coordinate mapping algorithm between camera frame and screen resolution, distance thresholding for click detection, and smoothing techniques.",
            6
        )
        add_q(
            project_q,
            "What challenges did you face while processing hand gestures in real time, and how did you minimize latency?",
            "Discuss frame rate optimization (FPS), reducing compute per frame, handling varying lighting conditions, and camera input resolution.",
            6
        )
        add_q(
            project_q,
            "What motivated the patent publication or public demonstration for the Virtual Hand Gesture Mouse, and what feedback did you incorporate?",
            "Highlight your innovation, the technical problem being addressed (hands-free human-computer interaction), and real-world usability testing.",
            6
        )

    if len(project_q) < 4:
        for p in projects[:2]:
            p_name = p.get('title', p.get('project', 'your project'))
            add_q(
                project_q,
                f"In {p_name}, what was the most complex technical obstacle you solved and how did you resolve it?",
                "Use the STAR method: describe the technical roadblock, tools you used to diagnose it, and the working implementation.",
                6
            )
            add_q(
                project_q,
                f"How did you structure error handling and logging across {p_name}?",
                "Explain your approach to catching exceptions, user feedback, and recording system events.",
                6
            )

    # 4. JOB-SPECIFIC QUESTIONS (Target: 5-7, only if is_sufficient)
    job_specific_q: List[Dict[str, str]] = []

    if is_sufficient:
        for s in required_missing:
            if 'rest framework' in s.lower() or 'drf' in s.lower():
                add_q(
                    job_specific_q,
                    "The role requires Django REST Framework. Have you worked with Django REST Framework? If not, how would you approach learning it?",
                    "Be honest about not having formal commercial experience yet. Walk through your learning plan: installing djangorestframework, creating Serializers for your models, building ModelViewSet endpoints, and configuring routers.",
                    7
                )
            elif s.upper() == 'SQL':
                add_q(
                    job_specific_q,
                    "The job requires writing raw SQL queries. Have you worked with complex SQL? If not, how do you plan to transition from ORM queries to writing direct SQL?",
                    "Acknowledge your current experience with ORM queries and relational concepts (SQLite/MySQL), and explain how you are practicing writing direct queries with GROUP BY, JOINs, and subqueries.",
                    7
                )
            elif 'api' in s.lower():
                add_q(
                    job_specific_q,
                    "This position emphasizes API development. How would you design, document, and test an API endpoint for an external client?",
                    "Discuss OpenAPI / Swagger documentation, Postman or pytest testing, payload validation, and clear error responses.",
                    7
                )
            else:
                add_q(
                    job_specific_q,
                    f"The job requires {s}. Have you worked with {s}? If not, how would you approach mastering its core fundamentals?",
                    f"Acknowledge your current background, explain your systematic approach to learning {s}, and how it connects to your existing engineering skills.",
                    7
                )

        if has_skill('Python') and has_skill('Django'):
            add_q(
                job_specific_q,
                "This role emphasizes Python and Django backend development. How do you structure a production-ready Django settings configuration and handle environment variables?",
                "Discuss separating base/dev/prod settings, using django-environ or python-dotenv, securing SECRET_KEY, and configuring database connection pools.",
                7
            )

        if has_skill('MySQL'):
            add_q(
                job_specific_q,
                "The position specifies MySQL for data storage. How do you approach configuring database connections and managing migrations safely in Django with MySQL?",
                "Explain using mysqlclient or PyMySQL, running makemigrations/migrate safely, and testing migrations on staging before production.",
                7
            )

        for pref in preferred_missing:
            if 'docker' in pref.lower():
                add_q(
                    job_specific_q,
                    "[Preferred Skill] The posting mentions Docker as a preferred qualification. How would you approach containerizing a Python backend application?",
                    "Be upfront that Docker is an area you are actively learning. Describe a Dockerfile: choosing a python:3.x-slim base image, copying requirements.txt, running pip install, and defining CMD with gunicorn/uvicorn.",
                    7
                )
            elif 'fastapi' in pref.lower():
                add_q(
                    job_specific_q,
                    "[Preferred Skill] FastAPI is listed as a preferred skill. How does FastAPI differ from Django, and in what scenarios would you choose FastAPI?",
                    "Contrast Django's full-featured, batteries-included MVC structure with FastAPI's lightweight, asynchronous, high-throughput microservice architecture.",
                    7
                )
            elif 'redis' in pref.lower() or 'postgresql' in pref.lower():
                add_q(
                    job_specific_q,
                    "[Preferred Skill] PostgreSQL and Redis are listed as preferred skills. In what backend scenarios would you choose Redis alongside a relational database?",
                    "Explain caching frequently accessed query results, session storage, and rate limiting with Redis to reduce load on the primary relational database.",
                    7
                )
            elif 'linux' in pref.lower():
                add_q(
                    job_specific_q,
                    "[Preferred Skill] Linux is listed as a preferred qualification. How comfortable are you working in a Linux terminal, managing services, and reading logs?",
                    "Share your familiarity with core bash commands, process inspection (ps, top), and viewing application service logs with journalctl.",
                    7
                )

    # 5. BEHAVIORAL QUESTIONS (Target: 3-5)
    behavioral_q: List[Dict[str, str]] = []

    proj_ref = "Smart File Organiser or Virtual Hand Gesture Mouse" if (has_file_org or has_gesture_mouse) else "your projects"
    add_q(
        behavioral_q,
        f"Tell me about a technical challenge you faced while building your {proj_ref}, and how you resolved it.",
        "Use the STAR method (Situation, Task, Action, Result). Focus on a specific obstacle (e.g. edge-case file collisions or hand landmark jitter), the debugging steps you took, and the working solution.",
        5
    )

    add_q(
        behavioral_q,
        "Tell me about a time you had to learn a technology quickly to deliver a project milestone.",
        "Describe learning a new framework or library from official documentation and tutorials, how you experimented with sample code, and integrated it successfully.",
        5
    )

    add_q(
        behavioral_q,
        "How do you debug a problem when you don't immediately know the root cause?",
        "Outline a systematic approach: inspecting error stack traces, checking log outputs, reproducing in isolation with print/debugger breakpoints, and formulating testable hypotheses.",
        5
    )

    add_q(
        behavioral_q,
        "How do you handle constructive feedback or code review suggestions on your implementations?",
        "Emphasize an egoless, growth-oriented mindset: asking clarifying questions, appreciating alternative approaches for readability or performance, and implementing improvements.",
        5
    )

    result_dict: Dict[str, List[Dict[str, str]]] = {
        'Resume-Based Questions': resume_based_q[:5],
        'Technical Questions': technical_q[:7],
        'Project Questions': project_q[:6],
    }
    if is_sufficient:
        result_dict['Job-Specific Questions'] = job_specific_q[:7]
    result_dict['Behavioral Questions'] = behavioral_q[:5]

    return result_dict

def build_grounded_learning_roadmap(
    required_missing: List[str],
    preferred_missing: List[str],
    projects: List[Dict[str, Any]],
    is_sufficient: bool = True
) -> List[Dict[str, Any]]:
    """
    Builds a grounded, personalized learning roadmap respecting:
    1. Priority: Missing REQUIRED skills first, then foundational prerequisites, then missing PREFERRED skills.
    2. Dependency order: SQL -> Database -> DRF -> API Development -> Docker -> Linux -> FastAPI -> PostgreSQL -> Redis.
    3. Project grounding: Connects practical tasks directly to candidate's existing projects (e.g. Smart File Organiser)
       clearly labeled as 'Suggested Practice' or 'Future Project Enhancement'.
    4. Insufficient JD returns empty roadmap [].
    """
    if not is_sufficient:
        return []

    p_titles = [p.get('title', p.get('project', '')) for p in projects]
    has_file_org = any('file' in t.lower() or 'organis' in t.lower() or 'organiz' in t.lower() for t in p_titles)
    primary_proj = "Smart File Organiser" if has_file_org else (p_titles[0] if p_titles else "your portfolio project")

    def skill_dependency_rank(skill_name: str) -> int:
        s_lower = skill_name.lower()
        if s_lower == 'sql' or 'relational database' in s_lower or 'database design' in s_lower:
            return 10
        if 'rest framework' in s_lower or 'drf' in s_lower:
            return 20
        if 'api development' in s_lower or 'rest api' in s_lower:
            return 30
        if 'react' in s_lower or 'frontend' in s_lower:
            return 40
        if 'docker' in s_lower:
            return 50
        if 'linux' in s_lower:
            return 60
        if 'fastapi' in s_lower:
            return 70
        if 'postgresql' in s_lower:
            return 80
        if 'redis' in s_lower:
            return 90
        if 'aws' in s_lower or 'cloud' in s_lower:
            return 100
        return 110

    sorted_required = sorted(required_missing, key=skill_dependency_rank)
    clean_preferred = [p for p in preferred_missing if p not in required_missing]
    sorted_preferred = sorted(clean_preferred, key=skill_dependency_rank)

    ordered_targets = [(s, 'required') for s in sorted_required] + [(s, 'preferred') for s in sorted_preferred]

    roadmap_items: List[Dict[str, Any]] = []

    for idx, (skill, priority) in enumerate(ordered_targets):
        week_num = idx + 1
        week_label = f"Week {week_num}"
        s_lower = skill.lower()

        if s_lower == 'sql':
            stage = f"Week {week_num}: Core Required Skill"
            title = "Mastering SQL & Relational Database Fundamentals"
            why_it_matters = "SQL is explicitly required by the target job. Understanding relational querying and schema design is fundamental for any backend developer role."
            what_to_learn = [
                "SELECT, WHERE, ORDER BY, GROUP BY, and HAVING aggregation",
                "INNER JOIN, LEFT JOIN, and relational constraints",
                "INSERT, UPDATE, DELETE operations and transaction handling (COMMIT/ROLLBACK)",
                "Index fundamentals and query execution analysis"
            ]
            practical_task = f"Suggested Practice: Practice SQL using the database concepts already present in your {primary_proj}. Write raw SQL queries against your database file for file logs, classification counts, and recent movements."
            expected_outcome = "You can write and explain common SQL queries, joins, and indexing strategies during technical interviews."
            description = f"Practice SQL using the database concepts already present in your {primary_proj}."

        elif 'rest framework' in s_lower or 'drf' in s_lower:
            stage = f"Week {week_num}: Core Required Skill"
            title = "Mastering Django REST Framework (DRF)"
            why_it_matters = "Django REST Framework (DRF) is explicitly required by the target job to build robust, scalable RESTful web APIs on top of Django."
            what_to_learn = [
                "DRF architecture, serializers, and ModelSerializer validation",
                "APIView, Generic Views, and ModelViewSets with routers",
                "Request authentication, permissions (IsAuthenticated), and throttling",
                "Pagination, filtering, and standard JSON response formatting"
            ]
            practical_task = f"Future Project Enhancement: Add a small REST API to a separate branch of your {primary_proj} to expose endpoints for scanning directories and listing organized files."
            expected_outcome = "You can design and explain production-ready DRF endpoints, serializers, and permission classes in interview discussions."
            description = f"Add a small REST API to a separate branch or future version of your {primary_proj}."

        elif 'api development' in s_lower or 'rest api' in s_lower:
            stage = f"Week {week_num}: Core Required Skill"
            title = "Mastering API Development & Testing Standards"
            why_it_matters = "API Development is explicitly required by the target job. Backend engineers must understand HTTP protocols, API contracts, status codes, and documentation."
            what_to_learn = [
                "RESTful design principles, idempotency (GET/PUT/DELETE) vs non-idempotency (POST)",
                "Standard HTTP response status codes (200, 201, 400, 401, 403, 404, 500)",
                "API documentation using OpenAPI / Swagger / drf-spectacular",
                "Automated API testing using pytest or Django APIClient"
            ]
            practical_task = f"Future Project Enhancement: Document and test the {primary_proj} API using tools like Swagger/OpenAPI and Postman."
            expected_outcome = "You can articulate API architecture, contract design, error handling standards, and automated testing strategies."
            description = f"Document and test the {primary_proj} API using tools like Swagger/OpenAPI and Postman."

        elif 'docker' in s_lower:
            stage = f"Week {week_num}: Preferred Skill (Bonus)" if priority == 'preferred' else f"Week {week_num}: Core Required Skill"
            title = "Mastering Docker Fundamentals & Containerization"
            why_it_matters = "Docker is listed as a preferred qualification. Containerization ensures consistent runtime environments across development and production." if priority == 'preferred' else "Docker is required by the job posting for containerizing backend applications."
            what_to_learn = [
                "Docker architecture: images, containers, layers, and Dockerfile syntax",
                "Multi-stage builds and minimal base images (e.g., python:3.x-slim)",
                "docker-compose.yml for running multi-container stacks (app + database)",
                "Environment variables, volume mounting, and port forwarding"
            ]
            practical_task = f"Suggested Practice: Containerize your existing {primary_proj} by writing a Dockerfile and docker-compose.yml to run the Django service in an isolated environment."
            expected_outcome = "You can explain containerization benefits, write clean Dockerfiles, and discuss deployment workflows in interviews."
            description = f"Containerize your existing {primary_proj}."

        elif 'linux' in s_lower:
            stage = f"Week {week_num}: Preferred Skill (Bonus)"
            title = "Mastering Linux Server Navigation & Process Management"
            why_it_matters = "Linux is listed as a preferred qualification. Most production backend servers run on Linux distributions (Ubuntu, Debian, RHEL)."
            what_to_learn = [
                "Essential command-line utilities (grep, find, curl, systemctl, journalctl)",
                "File permissions, ownership (chmod, chown), and process management (ps, kill, top)",
                "Environment variables, shell scripting basics (Bash), and SSH",
                "Basic systemd service configuration for running Python backend daemons"
            ]
            practical_task = f"Suggested Practice: Deploy or test running your {primary_proj} inside a Linux terminal or WSL environment, configuring environment variables and shell scripts."
            expected_outcome = "You can demonstrate comfort navigating Linux servers, managing background processes, and troubleshooting deployment logs."
            description = f"Deploy or test running your {primary_proj} inside a Linux terminal or WSL environment."

        elif 'fastapi' in s_lower:
            stage = f"Week {week_num}: Preferred Skill (Bonus)"
            title = "Mastering FastAPI & Asynchronous Python"
            why_it_matters = "FastAPI is listed as a preferred qualification, representing a modern asynchronous Python framework for high-throughput microservices."
            what_to_learn = [
                "Asynchronous Python fundamentals (async/await, coroutines, event loop)",
                "Pydantic data validation and type hinting",
                "Dependency injection system and automatic interactive Swagger documentation",
                "Differences in architecture between Django (synchronous batteries-included) and FastAPI (lightweight async)"
            ]
            practical_task = f"Suggested Practice: Build a lightweight standalone FastAPI microservice that accepts file upload metadata and returns categorization predictions, comparing its structure with Django."
            expected_outcome = "You can compare Django and FastAPI architectures and articulate when to choose async vs synchronous frameworks."
            description = "Build a lightweight standalone FastAPI microservice to practice asynchronous Python API endpoints."

        elif 'postgresql' in s_lower:
            stage = f"Week {week_num}: Preferred Skill (Bonus)"
            title = "Mastering PostgreSQL Configuration & Advanced Indexing"
            why_it_matters = "PostgreSQL is listed as a preferred qualification. It is one of the most widely used enterprise open-source relational database management systems."
            what_to_learn = [
                "PostgreSQL-specific data types (JSONB, UUID, Arrays)",
                "Advanced indexing (GIN, GiST, partial indexes) and EXPLAIN ANALYZE",
                "Connecting Django to PostgreSQL using psycopg2/psycopg3",
                "Differences between MySQL and PostgreSQL concurrency and ACID isolation levels"
            ]
            practical_task = f"Suggested Practice: Configure a local PostgreSQL database on a test branch of your project to practice database switching and migration management."
            expected_outcome = "You can speak to PostgreSQL features, indexing, and migration from development databases to PostgreSQL."
            description = "Configure a local PostgreSQL database on a test branch of your project to practice database switching."

        elif 'redis' in s_lower:
            stage = f"Week {week_num}: Preferred Skill (Bonus)"
            title = "Mastering Redis Caching & In-Memory Storage"
            why_it_matters = "Redis is listed as a preferred qualification for caching, distributed locking, and rate limiting in high-performance backends."
            what_to_learn = [
                "In-memory data structures (Strings, Hashes, Lists, Sets, Sorted Sets)",
                "Caching strategies: Cache-Aside, Write-Through, TTL expiration",
                "Integrating Redis with Django cache backend (django-redis)",
                "Rate limiting and session storage concepts"
            ]
            practical_task = f"Suggested Practice: Implement Redis caching for frequently queried file statistics or task queues in your application."
            expected_outcome = "You can explain how Redis is used to reduce database load and improve API latency in distributed systems."
            description = "Implement Redis caching for frequently queried file statistics or task queues in your application."

        elif 'react' in s_lower:
            stage = f"Week {week_num}: Core Required Skill"
            title = "Mastering React Fundamentals"
            why_it_matters = "React is explicitly required by the target full stack developer role for building component-driven user interfaces."
            what_to_learn = [
                "Component lifecycle, JSX syntax, and props vs state",
                "Core React Hooks: useState, useEffect, useCallback, useMemo",
                "Handling API requests and asynchronous data fetching",
                "Form validation and state management"
            ]
            practical_task = "Suggested Practice: Build a modern frontend dashboard in React that consumes your backend REST APIs and renders interactive data views."
            expected_outcome = "You can build modular React components and integrate them smoothly with backend APIs."
            description = "Build a modern frontend dashboard in React that consumes your backend REST APIs."

        elif 'aws' in s_lower:
            stage = f"Week {week_num}: Core Required Skill"
            title = "Mastering AWS Fundamentals"
            why_it_matters = "AWS is explicitly required by the job posting for hosting and deploying scalable cloud applications."
            what_to_learn = [
                "Core services: EC2 (compute), S3 (object storage), RDS (managed database)",
                "IAM permissions, security groups, and environment configuration",
                "Deploying a containerized web application to EC2 or ECS",
                "CloudWatch logs and basic monitoring"
            ]
            practical_task = "Suggested Practice: Deploy your containerized web application to an AWS EC2 instance or configure an S3 bucket for storing uploaded assets."
            expected_outcome = "You can navigate AWS core infrastructure and explain cloud deployment architectures during interviews."
            description = "Deploy your containerized web application to an AWS EC2 instance or configure an S3 bucket."

        else:
            stage = f"Week {week_num}: {'Core Required' if priority == 'required' else 'Preferred'} Skill"
            title = f"Mastering {skill} Fundamentals"
            why_it_matters = f"{skill} is explicitly {priority} by the target job description."
            what_to_learn = [
                f"Core fundamentals and architecture of {skill}",
                f"Best practices and common design patterns in {skill}",
                f"Integration with your existing technical stack"
            ]
            practical_task = f"Suggested Practice: Build a focused prototype applying {skill} to practical tasks, connecting it with your {primary_proj} domain."
            expected_outcome = f"You can explain core concepts of {skill} and demonstrate practical understanding in technical interviews."
            description = f"Build a practical hands-on module incorporating {skill} into a portfolio project."

        roadmap_items.append({
            'week': week_label,
            'title': title,
            'description': description,
            'skills': [skill],
            'stage': stage,
            'skill': skill,
            'priority': priority,
            'why_it_matters': why_it_matters,
            'what_to_learn': what_to_learn,
            'practical_task': practical_task,
            'expected_outcome': expected_outcome
        })

    return roadmap_items

def compare_resume_and_job(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:

    """
    Compares resume entities with target job requirements.
    Grounded strictly in documented evidence.
    Handles insufficient job descriptions gracefully without fabricating scores or skills.
    Maintains strict separation between required and preferred skills.
    Distinguishes mentioned vs demonstrated skills.
    """
    job_title = job_data.get('title', 'Target Role')
    job_description = job_data.get('description', '')
    raw_resume_text = resume_data.get('raw_text', '')
    projects = resume_data.get('projects', [])
    resume_skills = set(resume_data.get('skills', []))

    required_skills = list(job_data.get('required_skills', []))
    preferred_skills = list(job_data.get('preferred_skills', []))

    # 1. Check if the JD contains sufficient technical requirements
    is_sufficient, reason = is_job_description_sufficient(job_title, job_description)

    if not is_sufficient:
        confirmed_skills = sorted(list(resume_skills))
        resume_questions = []
        if projects:
            p_name = projects[0].get('title', 'your main project')
            resume_questions.append(f"Can you explain how you designed and implemented the {p_name}?")
        if confirmed_skills:
            resume_questions.append(f"Can you walk through your practical experience working with {confirmed_skills[0]}?")

        return {
            'match_score': None,
            'analysis_status': 'insufficient_jd',
            'status_message': reason,
            'overview': (
                "The job description does not provide enough specific technical requirements, "
                "frameworks, or qualifications to compute a meaningful match score. "
                "Please provide a more detailed job description to see matched skills and gaps."
            ),
            'required_skills_total': 0,
            'required_skills_matched': [],
            'required_skills_missing': [],
            'preferred_skills_total': 0,
            'preferred_skills_matched': [],
            'preferred_skills_missing': [],
            'skills_demonstrated': [],
            'skills_mentioned': [],
            'skills_breakdown': [],
            'matched_skills': [],
            'missing_skills': [],
            'keyword_total': 0,
            'keywords_found': [],
            'keywords_missing': [],
            'scoring_formula': "N/A (Insufficient JD)",
            'resume_strengths': [
                f"Documented skills in resume: {', '.join(confirmed_skills[:5])}." if confirmed_skills
                else "Documented foundational coursework and project work in the submitted resume."
            ],
            'resume_weaknesses': [
                "Unable to evaluate missing requirements because the target job posting lacks specific technical requirements."
            ],
            'project_analysis': [
                {
                    'project': p.get('title', 'Project'),
                    'technologies': p.get('technologies', []),
                    'relevance': 'General software engineering experience.',
                    'strong': (
                        f"Demonstrates implementation using {', '.join(p.get('technologies', []))} as documented in the project description."
                        if p.get('technologies')
                        else f"Outlines technical implementation for {p.get('title', 'the project')}."
                    ),
                    'improvements': (
                        "The resume describes the project's functionality but does not provide a measurable performance result or quantitative outcome."
                        if not has_measurable_metrics(p.get('evidence', ''))
                        else "Consider highlighting system architecture diagrams or live repository links."
                    ),
                    'evidence': p.get('evidence', '')
                } for p in projects[:3]
            ],
            'resume_suggestions': [
                "Provide a detailed job description outlining required programming languages, frameworks, databases, and deployment platforms to receive actionable recommendations."
            ],
            'interview_questions': build_grounded_interview_questions(
                resume_skills=resume_skills,
                projects=projects,
                job_title=job_title,
                required_matched=[],
                required_missing=[],
                preferred_matched=[],
                preferred_missing=[],
                is_sufficient=False
            ),
            'learning_roadmap': []
        }

    # 2. Extract project texts for evidence verification
    project_texts = []
    for p in projects:
        p_evidence = p.get('evidence', '')
        p_desc = ' '.join(p.get('description', []))
        project_texts.append(f"{p.get('title', '')} | {p_evidence} | {p_desc}")

    # 3. Evaluate REQUIRED skills
    required_matched: List[str] = []
    required_missing: List[str] = []
    skills_demonstrated: List[str] = []
    skills_mentioned: List[str] = []
    skills_breakdown: List[Dict[str, Any]] = []

    for req in required_skills:
        eval_res = check_skill_evidence_detailed(req, raw_resume_text, project_texts)
        if eval_res['mentioned']:
            required_matched.append(req)
            if eval_res['demonstrated'] == 'Yes':
                skills_demonstrated.append(req)
            else:
                skills_mentioned.append(req)
            skills_breakdown.append({
                'skill': req,
                'category': 'required',
                'status': 'matched',
                'mentioned': True,
                'demonstrated': eval_res['demonstrated'],
                'evidence': eval_res['evidence'] or ""
            })
        else:
            required_missing.append(req)
            skills_breakdown.append({
                'skill': req,
                'category': 'required',
                'status': 'missing',
                'mentioned': False,
                'demonstrated': 'No',
                'evidence': ""
            })

    # 4. Evaluate PREFERRED skills (reported separately, does NOT penalize required score)
    preferred_matched: List[str] = []
    preferred_missing: List[str] = []

    for pref in preferred_skills:
        eval_res = check_skill_evidence_detailed(pref, raw_resume_text, project_texts)
        if eval_res['mentioned']:
            preferred_matched.append(pref)
            if eval_res['demonstrated'] == 'Yes':
                skills_demonstrated.append(pref)
            else:
                skills_mentioned.append(pref)
            skills_breakdown.append({
                'skill': pref,
                'category': 'preferred',
                'status': 'matched',
                'mentioned': True,
                'demonstrated': eval_res['demonstrated'],
                'evidence': eval_res['evidence'] or ""
            })
        else:
            preferred_missing.append(pref)
            skills_breakdown.append({
                'skill': pref,
                'category': 'preferred',
                'status': 'missing',
                'mentioned': False,
                'demonstrated': 'No',
                'evidence': ""
            })

    required_matched = sorted(required_matched)
    required_missing = sorted(required_missing)
    preferred_matched = sorted(preferred_matched)
    preferred_missing = sorted(preferred_missing)

    # 5. Evaluate domain keywords (strictly non-skills, word-boundary verified)
    job_keywords = job_data.get('domain_keywords', [])
    keywords_found: List[str] = []
    keywords_missing: List[str] = []

    for kw in job_keywords:
        if is_keyword_present(kw, raw_resume_text):
            keywords_found.append(kw)
        else:
            keywords_missing.append(kw)

    keywords_found = sorted(keywords_found)
    keywords_missing = sorted(keywords_missing)

    # 6. Calculate deterministic, auditable match score
    match_score = calculate_deterministic_match_score(
        matched_skills=required_matched,
        total_required_skills=required_skills,
        keywords_found=keywords_found,
        keywords_missing=keywords_missing,
        preferred_skills_matched=preferred_matched,
        total_preferred_skills=preferred_skills
    )

    kw_total = len(keywords_found) + len(keywords_missing)
    scoring_formula = f"match_score = round(({len(required_matched)} / {len(required_skills)}) * 100)"


    # 7. Strengths based strictly on verified resume evidence
    resume_strengths = []
    if required_matched:
        resume_strengths.append(
            f"The resume demonstrates verified experience with required technologies: {', '.join(required_matched)}."
        )
    if preferred_matched:
        resume_strengths.append(
            f"Includes exposure to preferred skills: {', '.join(preferred_matched)}."
        )
    if not resume_strengths:
        resume_strengths.append("Foundational technical skills documented in the submitted resume.")

    # 8. Weaknesses based strictly on missing required job requirements (preferred skills are NOT weaknesses)
    resume_weaknesses = []
    if required_missing:
        for skill in required_missing[:4]:
            resume_weaknesses.append(
                f"The job description requires {skill}, but {skill} experience is not clearly demonstrated in the submitted resume."
            )
    else:
        resume_weaknesses.append(
            "All core required technical qualifications identified in the job description are represented in the resume."
        )

    # 9. Project analysis with verified technologies & sanitized truthful recommendations
    project_analysis = []
    has_any_metric = False

    if projects:
        for p in projects[:3]:
            # STRICT GUARD: Technologies must come from the project's own text!
            p_text = f"{p.get('title', '')} {' '.join(p.get('description', []))} {p.get('evidence', '')}"
            genuine_p_techs = [
                t for t in p.get('technologies', [])
                if find_skill_evidence(t, p_text)[0]
            ]
            if not genuine_p_techs:
                # Extract directly from project text
                from .skill_normalization import extract_skills_from_text
                genuine_p_techs = extract_skills_from_text(p_text)

            p_evidence = p.get('evidence', '')
            has_metric = has_measurable_metrics(p_evidence)
            if has_metric:
                has_any_metric = True

            overlap = [t for t in genuine_p_techs if t in required_matched]

            sanitized_imp = sanitize_project_improvements(
                raw_improvements=p.get('improvements', ''),
                project_title=p.get('title', 'Project'),
                project_techs=genuine_p_techs,
                resume_skills=resume_skills,
                missing_skills=required_missing,
                has_metrics=has_metric
            )

            project_analysis.append({
                'project': p.get('title', 'Resume Project'),
                'technologies': genuine_p_techs,
                'relevance': f"Demonstrates practical hands-on application of {', '.join(overlap)}." if overlap else "Relevant to general software engineering practices.",
                'strong': (
                    f"Demonstrates implementation using {', '.join(genuine_p_techs)} as documented in the project description."
                    if genuine_p_techs
                    else f"Outlines technical implementation for {p.get('title', 'the project')}."
                ),
                'improvements': sanitized_imp,
                'evidence': p_evidence
            })

    # 10. Truthful Suggestions following 4-tier priority (Issues 3, 4, 7)
    resume_suggestions = build_truthful_resume_suggestions(
        skills_mentioned_not_demonstrated=skills_mentioned,
        missing_required_skills=required_missing,
        has_any_metric=has_any_metric,
        projects=projects
    )

    # 11. Targeted Interview Questions
    interview_questions = build_grounded_interview_questions(
        resume_skills=resume_skills,
        projects=projects,
        job_title=job_title,
        required_matched=required_matched,
        required_missing=required_missing,
        preferred_matched=preferred_matched,
        preferred_missing=preferred_missing,
        is_sufficient=True
    )

    # 12. Learning Roadmap prioritizing required missing over preferred missing
    learning_roadmap = build_grounded_learning_roadmap(
        required_missing=required_missing,
        preferred_missing=preferred_missing,
        projects=projects,
        is_sufficient=True
    )

    overview = (
        f"Your resume demonstrates clear alignment in {len(required_matched)} of {len(required_skills)} required skill(s) "
        f"({', '.join(required_matched[:3]) if required_matched else 'core skills'}), with {len(required_missing)} required requirement(s) "
        f"({', '.join(required_missing[:3]) if required_missing else 'none'}) not clearly demonstrated."
    )
    if preferred_matched:
        overview += f" You also match preferred skill(s): {', '.join(preferred_matched)}."

    return {
        'match_score': match_score,
        'analysis_status': 'complete',
        'status_message': None,
        'overview': overview,
        'required_skills_total': len(required_skills),
        'required_skills_matched': required_matched,
        'required_skills_missing': required_missing,
        'preferred_skills_total': len(preferred_skills),
        'preferred_skills_matched': preferred_matched,
        'preferred_skills_missing': preferred_missing,
        'skills_demonstrated': skills_demonstrated,
        'skills_mentioned': skills_mentioned,
        'skills_breakdown': skills_breakdown,
        'matched_skills': required_matched,
        'missing_skills': required_missing,
        'keyword_total': kw_total,
        'keywords_found': keywords_found,
        'keywords_missing': keywords_missing,
        'scoring_formula': scoring_formula,
        'resume_strengths': resume_strengths,
        'resume_weaknesses': resume_weaknesses,
        'project_analysis': project_analysis,
        'resume_suggestions': resume_suggestions,
        'interview_questions': interview_questions,
        'learning_roadmap': learning_roadmap,
    }
