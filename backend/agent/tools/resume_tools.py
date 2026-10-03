"""
Resume entity and project extraction tool.
Extracts verifiable skills and genuine project records from resume text.
Strictly avoids treating arbitrary sentences as projects.
"""
import re
from typing import Dict, Any, List
from .skill_normalization import extract_skills_from_text, find_skill_evidence, CANONICAL_SKILL_ALIASES

PROJECT_SECTION_HEADERS = [
    'selected projects', 'academic projects', 'personal projects',
    'relevant projects', 'key projects', 'project experience',
    'technical projects', 'projects'
]

SECTION_STOP_HEADERS = [
    'internship', 'internships', 'work experience', 'professional experience',
    'experience', 'work history', 'employment history', 'employment',
    'education', 'skills', 'technical skills', 'soft skills', 'certifications',
    'achievements', 'awards', 'publications', 'summary', 'profile', 'references',
    'languages known', 'languages'
]

def extract_resume_entities(resume_text: str) -> Dict[str, Any]:
    """
    Extracts verified skills, structured projects, and metadata from resume text.
    Grounded strictly in the document content.
    """
    if not resume_text:
        return {'skills': [], 'projects': [], 'line_count': 0, 'character_count': 0}

    # 1. Deterministic skill extraction with alias awareness
    detected_skills = extract_skills_from_text(resume_text)

    # 2. Extract structured projects strictly from explicit project sections
    projects = []
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]

    in_project_section = False
    current_project = None

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()

        # Check for start of project section
        if not in_project_section:
            if any(line_lower == h or line_lower.startswith(h + ':') or line_lower.startswith(h + ' -') for h in PROJECT_SECTION_HEADERS):
                in_project_section = True
                continue

        # Check for end of project section
        if in_project_section:
            is_section_break = any(
                line_lower == h or line_lower.startswith(h + ':') or line_lower.startswith(h + ' -')
                for h in SECTION_STOP_HEADERS
            ) or (len(line_clean) < 35 and any(h in line_lower for h in [
                'experience', 'education', 'skills', 'employment', 'internship',
                'certifications', 'achievements', 'soft skills', 'languages'
            ]))

            if is_section_break:
                in_project_section = False
                break

            # Inside project section: detect genuine project title
            is_bullet = line_clean.startswith(('-', '*', '•', '–', '—', '+')) or re.match(r'^\d+\.', line_clean)
            ends_with_period = line_clean.endswith('.') or line_clean.endswith(';')
            starts_with_verb = any(line_lower.startswith(v) for v in [
                'developed', 'implemented', 'built', 'created', 'designed', 'managed',
                'worked', 'responsible', 'assisted', 'engineered', 'led', 'architected',
                'vision', 'deployed', 'maintained', 'leveraged', 'utilized'
            ])

            if len(line_clean) < 90 and not is_bullet and not ends_with_period and not starts_with_verb and not (':' in line_clean[:10]):
                # If title contains pipe separator (e.g. "Smart File Organiser | Python, Django, ...")
                if '|' in line_clean:
                    title_part = line_clean.split('|')[0].strip()
                    tech_part = line_clean.split('|', 1)[1].strip()
                else:
                    title_part = line_clean
                    tech_part = ''

                # Filter out accidental non-titles
                if title_part.lower() in [h.lower() for h in SECTION_STOP_HEADERS]:
                    in_project_section = False
                    break

                if current_project:
                    projects.append(current_project)

                current_project = {
                    'title': title_part,
                    'description': [],
                    'technologies': [],
                    'evidence': line_clean
                }

                # Detect technologies in the title/tech line
                check_line = f"{title_part} {tech_part}"
                for skill in detected_skills:
                    present, _ = find_skill_evidence(skill, check_line)
                    if present and skill not in current_project['technologies']:
                        current_project['technologies'].append(skill)
            elif current_project:
                current_project['description'].append(line_clean)
                current_project['evidence'] += f" | {line_clean}"
                # Detect technologies mentioned in this project line
                for skill in detected_skills:
                    present, _ = find_skill_evidence(skill, line_clean)
                    if present and skill not in current_project['technologies']:
                        current_project['technologies'].append(skill)

    if current_project:
        projects.append(current_project)

    # Note: If no explicit project section was identified, we DO NOT invent projects
    # or treat random sentences as projects.

    return {
        'skills': detected_skills,
        'projects': projects,
        'line_count': len(lines),
        'character_count': len(resume_text),
    }

extract_projects_from_resume = extract_resume_entities
