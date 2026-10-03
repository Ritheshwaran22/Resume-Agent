"""
Deterministic Skill Normalization & Extraction Engine.
Provides canonical skill mapping, alias resolution, and evidence-based matching.
Enforces strict distinction between technologies (e.g. AWS != Azure, Docker != K8s, PostgreSQL != Redis).
"""
import re
from typing import Dict, List, Optional, Set, Tuple, Any

# Canonical skill name -> list of recognized aliases and regex variants
CANONICAL_SKILL_ALIASES: Dict[str, List[str]] = {
    # Languages
    'Python': ['python', 'python3', 'python2', 'py'],
    'JavaScript': ['javascript', 'js', 'es6', 'ecmascript'],
    'TypeScript': ['typescript', 'ts'],
    'Java': ['java', 'core java'],
    'C++': ['c\\+\\+', 'cpp'],
    'C#': ['c#', 'c-sharp', 'csharp', '\\.net c#'],
    'Go': ['golang', 'go language', '\\bgo\\b'],
    'Rust': ['rust', 'rust-lang'],
    'PHP': ['php', 'php7', 'php8'],
    'Ruby': ['ruby', 'ruby on rails'],
    'SQL': ['sql', 'structured query language', 'ansi sql'],
    'HTML': ['html', 'html5'],
    'CSS': ['css', 'css3'],

    # Backend Frameworks
    'Django': ['django', 'django framework'],
    'Django REST Framework': ['django rest framework', 'drf', 'django rest'],
    'FastAPI': ['fastapi', 'fast api'],
    'Flask': ['flask', 'flask framework'],
    'Express': ['express', 'express\\.js', 'expressjs'],
    'Node.js': ['node\\.js', 'nodejs', 'node js'],
    'Spring Boot': ['spring boot', 'springboot', 'spring framework'],
    'Ruby on Rails': ['ruby on rails', 'rails'],
    'ASP.NET': ['asp\\.net', '\\.net core', 'dotnet core'],

    # Frontend Frameworks & Libraries
    'React': ['react', 'react\\.js', 'reactjs', 'react native'],
    'Next.js': ['next\\.js', 'nextjs', 'next js'],
    'Vue': ['vue', 'vue\\.js', 'vuejs', 'vue3'],
    'Angular': ['angular', 'angularjs', 'angular\\.js'],
    'Tailwind CSS': ['tailwind', 'tailwind css', 'tailwindcss'],
    'Redux': ['redux', 'redux toolkit'],

    # Databases & Storage
    'PostgreSQL': ['postgresql', 'postgres', 'psql'],
    'MySQL': ['mysql'],
    'SQLite': ['sqlite', 'sqlite3'],
    'MongoDB': ['mongodb', 'mongo'],
    'Redis': ['redis', 'redis caching'],
    'Elasticsearch': ['elasticsearch', 'elastic search'],
    'Cassandra': ['cassandra', 'apache cassandra'],
    'DynamoDB': ['dynamodb', 'aws dynamodb'],

    # DevOps, Cloud & Infrastructure
    'Docker': ['docker', 'docker container', 'docker containers', 'containerization with docker'],
    'Kubernetes': ['kubernetes', 'k8s'],
    'AWS': ['aws', 'amazon web services', 'amazon ec2', 'aws s3', 'aws rds', 'aws lambda', 'aws ecs'],
    'GCP': ['gcp', 'google cloud', 'google cloud platform'],
    'Azure': ['azure', 'microsoft azure'],
    'CI/CD': ['ci/cd', 'ci-cd', 'cicd', 'continuous integration', 'continuous deployment', 'github actions', 'jenkins', 'gitlab ci'],
    'Linux': ['linux', 'ubuntu', 'debian', 'centos', 'redhat', 'bash'],
    'Git': ['git', 'github', 'gitlab', 'version control'],
    'Terraform': ['terraform', 'infrastructure as code', 'iac'],

    # Architecture, APIs & Concepts
    'REST APIs': ['rest api', 'rest apis', 'restful api', 'restful apis', 'restful', '\\brest\\b'],
    'API Development': ['api development', 'api design', 'apis development', 'building apis', 'developing apis', 'backend apis', 'web apis'],
    'GraphQL': ['graphql', 'graph ql'],
    'Microservices': ['microservices', 'microservice', 'micro-services', 'micro-service architecture'],
    'System Design': ['system design', 'distributed systems', 'system architecture'],
    'Celery': ['celery', 'celery workers', 'distributed task queue'],
    'RabbitMQ': ['rabbitmq', 'rabbit mq'],
    'Kafka': ['kafka', 'apache kafka'],
    'WebSockets': ['websockets', 'websocket'],

    # Testing & Methodologies
    'PyTest': ['pytest', 'py\\.test'],
    'Unit Testing': ['unit testing', 'unit tests', 'unittest', 'automated testing'],
    'Jest': ['jest', 'jestjs'],
    'Agile': ['agile', 'scrum', 'kanban'],

    # Data Science & AI
    'Machine Learning': ['machine learning', '\\bml\\b'],
    'AI': ['artificial intelligence', '\\bai\\b', 'generative ai', 'llm', 'llms'],
    'PyTorch': ['pytorch'],
    'TensorFlow': ['tensorflow'],
    'Pandas': ['pandas'],
    'NumPy': ['numpy'],
    'Scikit-learn': ['scikit-learn', 'sklearn'],
}

# Negative distinction groups: skills that must NEVER be conflated or cross-credited
NEGATIVE_DISTINCTIONS = [
    {'AWS', 'GCP', 'Azure'},
    {'Docker', 'Kubernetes'},
    {'PostgreSQL', 'MySQL', 'SQLite', 'MongoDB', 'Redis', 'SQL'},
    {'PostgreSQL', 'MySQL'},
    {'Django', 'FastAPI', 'Flask'},
    {'Django', 'Django REST Framework'},
    {'REST APIs', 'Django REST Framework'},
    {'REST APIs', 'GraphQL'},
    {'Microservices', 'REST APIs'},
    {'React', 'Vue', 'Angular'},
]

def normalize_skill_name(raw_name: str) -> str:
    """
    Returns the canonical skill name if recognized, otherwise returns cleaned title case.
    """
    raw_cleaned = raw_name.strip()
    raw_lower = raw_cleaned.lower()

    for canonical, aliases in CANONICAL_SKILL_ALIASES.items():
        if canonical.lower() == raw_lower:
            return canonical
        for alias in aliases:
            # Check exact match or boundary match
            if alias.startswith('\\b') or alias.endswith('\\b'):
                if re.fullmatch(alias, raw_lower):
                    return canonical
            elif alias.replace('\\.', '.') == raw_lower:
                return canonical

    return raw_cleaned

def find_skill_evidence(skill: str, text: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if a canonical skill or any of its aliases appears in text.
    Returns (True, matching_snippet) if found, (False, None) otherwise.
    Uses strict word boundaries to avoid partial word substring false positives (e.g. 'rest' in 'interest', 'sql' in 'mysql').
    """
    if not text or not skill:
        return False, None

    canonical = normalize_skill_name(skill)
    aliases = CANONICAL_SKILL_ALIASES.get(canonical, [re.escape(skill.lower())])

    # Build regex pattern with strict word boundaries
    pattern_parts = []
    for alias in aliases:
        if alias.startswith('\\b') or alias.endswith('\\b'):
            pattern_parts.append(alias)
        else:
            pattern_parts.append(r'(?<![a-zA-Z0-9_-])' + alias + r'(?![a-zA-Z0-9_-])')

    combined_pattern = re.compile('|'.join(pattern_parts), re.IGNORECASE)
    match = combined_pattern.search(text)
    if match:
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        snippet = text[start:end].replace('\n', ' ').strip()
        return True, f"...{snippet}..."

    return False, None

def check_skill_evidence_detailed(
    skill: str,
    resume_text: str,
    project_texts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Distinguishes whether a skill is:
    - Mentioned (present in skills section, summary, or coursework)
    - Demonstrated (explicitly confirmed in project or work experience text)
    - Missing (absent from resume)
    """
    canonical = normalize_skill_name(skill)
    found_in_resume, snippet = find_skill_evidence(canonical, resume_text)

    if not found_in_resume:
        return {
            'skill': canonical,
            'mentioned': False,
            'demonstrated': 'No',
            'evidence': None
        }

    # Check if evidenced in any project/work experience text
    demonstrated_in_projects = False
    project_snippet = None
    if project_texts:
        for p_text in project_texts:
            has_proj_ev, p_snip = find_skill_evidence(canonical, p_text)
            if has_proj_ev:
                demonstrated_in_projects = True
                project_snippet = p_snip
                break

    return {
        'skill': canonical,
        'mentioned': True,
        'demonstrated': 'Yes' if demonstrated_in_projects else 'Unclear',
        'evidence': project_snippet or snippet
    }

def is_keyword_present(keyword: str, text: str) -> bool:
    """
    Checks if a domain keyword appears in text using word boundaries.
    Prevents false substring matches (e.g. 'sql' matching inside 'mysql' or 'sqlite').
    """
    if not keyword or not text:
        return False
    kw_clean = keyword.strip()
    pattern = r'(?<![a-zA-Z0-9_])' + re.escape(kw_clean) + r'(?![a-zA-Z0-9_])'
    return bool(re.search(pattern, text, re.IGNORECASE))

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts all canonical skills present in the text with verifiable evidence.
    """
    found_skills = []
    if not text:
        return found_skills

    for canonical in CANONICAL_SKILL_ALIASES.keys():
        present, _ = find_skill_evidence(canonical, text)
        if present:
            found_skills.append(canonical)

    return sorted(found_skills)

GENERIC_ROLES_AND_TITLES = {
    'full stack developer', 'full-stack developer', 'fullstack developer',
    'full stack', 'fullstack', 'full-stack',
    'software developer', 'software engineer', 'software architecture',
    'web developer', 'web development', 'backend developer', 'backend development',
    'frontend developer', 'frontend development', 'python developer',
    'data analyst', 'data analysis', 'ai engineer', 'ai developer',
    'developer', 'engineer', 'lead developer', 'senior developer', 'junior developer',
    'intern', 'internship', 'fresher', 'consultant', 'architect', 'specialist',
    'stack', 'backend', 'frontend', 'web', 'applications', 'application'
}

STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
    'will', 'with', 'we', 'our', 'you', 'your', 'candidate', 'developer', 'engineer',
    'looking', 'seeking', 'strong', 'experience', 'experienced', 'must', 'have',
    'plus', 'role', 'team', 'work', 'working', 'ability', 'years', 'preferred',
    'required', 'responsibilities', 'qualifications', 'requirements', 'skills',
    'full', 'stack', 'fullstack', 'software', 'application', 'applications',
    'build', 'maintain', 'develop', 'collaborate', 'engineering', 'both'
}

def extract_meaningful_keywords(text: str, exclude_skills: Optional[Set[str]] = None) -> List[str]:
    """
    Extracts important technical and domain keywords present in the text,
    strictly excluding:
    - Common English stop words
    - Generic role titles
    - ALL recognized technical skills and their aliases (to prevent duplicate counting)
    """
    if not text:
        return []

    # Build comprehensive set of skill terms and aliases to exclude
    all_excluded_skills_lower = {s.lower() for s in (exclude_skills or set())}
    for canonical, aliases in CANONICAL_SKILL_ALIASES.items():
        all_excluded_skills_lower.add(canonical.lower())
        for a in aliases:
            cleaned_alias = a.lower().replace('\\b', '').replace('\\.', '.').replace('\\+', '+')
            all_excluded_skills_lower.add(cleaned_alias)

    # Extract capitalized technical words, acronyms, and domain terms
    words = re.findall(r'\b[A-Za-z][A-Za-z0-9_+#./-]{2,}\b', text)
    candidate_keywords = []

    for w in words:
        w_clean = w.strip('.,/()[]')
        w_lower = w_clean.lower()
        if (
            len(w_clean) < 3
            or w_lower in STOP_WORDS
            or w_lower in all_excluded_skills_lower
            or w_lower in GENERIC_ROLES_AND_TITLES
        ):
            continue

        # Only include technical-looking or domain keywords (e.g. OpenCV, MediaPipe, Microservices)
        if any(c.isupper() for c in w_clean) or any(c in '+#./-' for c in w_clean):
            if w_clean not in candidate_keywords and w_clean.capitalize() not in candidate_keywords:
                candidate_keywords.append(w_clean)

    return candidate_keywords[:15]

def is_job_description_sufficient(job_title: str, job_description: str) -> Tuple[bool, str]:
    """
    Determines whether the job description provides sufficient technical details,
    required skills, or concrete qualifications to perform an accurate match analysis.
    A generic title like 'Full Stack Developer' without explicit technical skills or
    substantive requirements is insufficient.
    """
    combined_text = f"{job_title}\n{job_description}".strip()
    skills = extract_skills_from_text(combined_text)
    if len(skills) >= 1:
        return True, "Sufficient technical requirements found."

    # Check if there are technical domain keywords
    keywords = extract_meaningful_keywords(job_description, exclude_skills=set())

    if len(skills) == 0 and len(keywords) == 0:
        return False, "The job description does not contain enough specific technical requirements for a meaningful match analysis."

    # If 0 technical skills are mentioned and text is very short / generic
    words = [w for w in combined_text.split() if w.lower() not in STOP_WORDS and w.lower() not in GENERIC_ROLES_AND_TITLES]
    if len(skills) == 0 and len(words) < 20:
        return False, "The job description does not contain enough specific technical requirements for a meaningful match analysis."

    return True, "Sufficient requirements found."
