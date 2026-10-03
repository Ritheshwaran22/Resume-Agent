import re
from typing import Dict, Any, List, Set, Tuple
from .skill_normalization import extract_skills_from_text, extract_meaningful_keywords

REQUIRED_HEADER_PATTERNS = [
    r'^\s*required\s+skills',
    r'^\s*required\s+qualifications',
    r'^\s*basic\s+qualifications',
    r'^\s*minimum\s+qualifications',
    r'^\s*core\s+requirements',
    r'^\s*core\s+skills',
    r'^\s*requirements\b',
    r'^\s*what\s+you\s+need',
    r'^\s*what\s+you\'ll\s+need',
    r'^\s*must\s+have',
    r'^\s*must-have',
    r'^\s*required\b',
]

PREFERRED_HEADER_PATTERNS = [
    r'^\s*preferred\s+skills',
    r'^\s*preferred\s+qualifications',
    r'^\s*nice\s+to\s+have',
    r'^\s*nice-to-have',
    r'^\s*good\s+to\s+have',
    r'^\s*desired\s+skills',
    r'^\s*bonus\s+points',
    r'^\s*bonus\b',
    r'^\s*plusses\b',
    r'^\s*plus\b',
    r'^\s*preferred\b',
]

OTHER_SECTION_PATTERNS = [
    r'^\s*responsibilities\b',
    r'^\s*what\s+you\'ll\s+do',
    r'^\s*duties\b',
    r'^\s*about\s+us\b',
    r'^\s*about\s+the\s+role\b',
    r'^\s*company\s+overview\b',
    r'^\s*benefits\b',
    r'^\s*compensation\b',
    r'^\s*who\s+we\s+are\b',
]

INLINE_PREFERRED_CUES = [
    r'\bis\s+a\s+plus\b',
    r'\bwould\s+be\s+a\s+plus\b',
    r'\bnice\s+to\s+have\b',
    r'\bis\s+preferred\b',
    r'\bpreferred\b',
    r'\bbonus\b',
    r'\bgood\s+to\s+have\b',
]

def extract_job_requirements(job_title: str, job_description: str) -> Dict[str, Any]:
    """
    Extracts required technical skills, preferred technical skills, and domain keywords
    directly from the job title and description.
    Strictly separates REQUIRED from PREFERRED skills so preferred skills do not penalize
    the required skill match score.
    """
    full_text = f"{job_title}\n{job_description}"
    lines = [line.strip() for line in job_description.split('\n') if line.strip()]

    current_section = 'general'
    required_lines = []
    preferred_lines = []
    general_lines = []
    explicit_sections_found = False

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower().rstrip(':')

        # Check for Preferred headers
        is_pref_header = any(re.search(pat, line_lower) for pat in PREFERRED_HEADER_PATTERNS)
        if is_pref_header and (len(line_clean) < 40 or line_clean.endswith(':')):
            current_section = 'preferred'
            explicit_sections_found = True
            continue

        # Check for Required headers
        is_req_header = any(re.search(pat, line_lower) for pat in REQUIRED_HEADER_PATTERNS)
        if is_req_header and (len(line_clean) < 40 or line_clean.endswith(':')):
            current_section = 'required'
            explicit_sections_found = True
            continue

        # Check for other sections
        is_other_header = any(re.search(pat, line_lower) for pat in OTHER_SECTION_PATTERNS)
        if is_other_header and (len(line_clean) < 40 or line_clean.endswith(':')):
            current_section = 'other'
            continue

        if current_section == 'required':
            required_lines.append(line_clean)
        elif current_section == 'preferred':
            preferred_lines.append(line_clean)
        else:
            general_lines.append(line_clean)

    required_skills_set: Set[str] = set()
    preferred_skills_set: Set[str] = set()

    if explicit_sections_found:
        req_text = '\n'.join(required_lines)
        pref_text = '\n'.join(preferred_lines)

        req_extracted = extract_skills_from_text(req_text)
        pref_extracted = extract_skills_from_text(pref_text)

        required_skills_set.update(req_extracted)
        preferred_skills_set.update(pref_extracted)

        # Include any skills in job title as required
        title_skills = extract_skills_from_text(job_title)
        required_skills_set.update(title_skills)
    else:
        # No explicit section headers: parse sentences with inline preferred cues
        sentences = re.split(r'[.\n;]', full_text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue
            sent_skills = extract_skills_from_text(sent_clean)
            if not sent_skills:
                continue
            is_preferred_sent = any(re.search(cue, sent_clean, re.IGNORECASE) for cue in INLINE_PREFERRED_CUES)
            if is_preferred_sent:
                preferred_skills_set.update(sent_skills)
            else:
                required_skills_set.update(sent_skills)

    # Any skill in required takes precedence over preferred
    preferred_skills_set.difference_update(required_skills_set)

    required_skills = sorted(list(required_skills_set))
    preferred_skills = sorted(list(preferred_skills_set))

    # Fallback: if no required skills were found but full_text has skills, treat them as required
    if not required_skills and not preferred_skills:
        all_skills = extract_skills_from_text(full_text)
        required_skills = sorted(all_skills)

    # Extract meaningful domain keywords excluding ALL skills (both required & preferred)
    all_known_skills = set(required_skills) | set(preferred_skills)
    domain_keywords = extract_meaningful_keywords(full_text, exclude_skills=all_known_skills)

    return {
        'title': job_title,
        'required_skills': required_skills,
        'preferred_skills': preferred_skills,
        'domain_keywords': domain_keywords,
        'word_count': len(job_description.split()),
        'character_count': len(full_text),
    }
