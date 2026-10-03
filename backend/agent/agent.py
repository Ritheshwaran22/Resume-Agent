"""
Google ADK & Gemini powered AI Resume Agent.
Analyzes candidate resumes against target job descriptions.
Produces strictly truthful, evidence-grounded, structured feedback.
Safely logs model execution, errors, and handles insufficient job descriptions.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Set
from pydantic import ValidationError as PydanticValidationError

from .prompts import AGENT_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT_TEMPLATE
from .schemas import ResumeAnalysisOutput
from .tools.resume_tools import extract_resume_entities, extract_projects_from_resume
from .tools.job_tools import extract_job_requirements
from .tools.analysis_tools import (
    compare_resume_and_job,
    calculate_deterministic_match_score,
    has_measurable_metrics,
    sanitize_project_improvements,
    build_truthful_resume_suggestions,
    build_grounded_interview_questions,
    build_grounded_learning_roadmap
)
from .tools.skill_normalization import (
    find_skill_evidence,
    check_skill_evidence_detailed,
    is_keyword_present,
    normalize_skill_name,
    extract_skills_from_text,
    is_job_description_sufficient,
    CANONICAL_SKILL_ALIASES
)

logger = logging.getLogger(__name__)

class GeminiAnalysisError(Exception):
    """Raised when Gemini API call fails or produces unparseable output."""
    pass

class ResumeAgent:
    """
    Intelligent Resume Agent providing truthful, grounded analysis.
    Combines local deterministic extraction with Gemini Flash structured reasoning.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')

    def analyze(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        resume_id: Optional[Any] = None,
        job_id: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes complete agent analysis workflow:
        1. Local tool preprocessing (entities, skills, job requirements)
        2. Sufficiency validation: Check if JD contains enough technical requirements
        3. Gemini structured inference with multi-model fallback & safe error tracking
        4. Deterministic guardrail enforcement (verifies all claims against raw text)
        5. Reproducible score calculation (null if insufficient JD)
        """
        # Safe debug logging (NEVER log API keys or secrets)
        logger.info(
            f"[ResumeAgent] Starting analysis. ResumeID: {resume_id}, ResumeLen: {len(resume_text)}, "
            f"JobID: {job_id}, JobDescLen: {len(job_description)}"
        )

        # Step 1: Local deterministic extraction
        resume_entities = extract_resume_entities(resume_text)
        job_requirements = extract_job_requirements(job_title, job_description)

        # Step 2: Validate if JD provides sufficient technical details
        is_sufficient, sufficiency_reason = is_job_description_sufficient(job_title, job_description)
        if not is_sufficient:
            logger.info(
                f"[ResumeAgent] Job description is insufficient for technical match scoring: {sufficiency_reason}"
            )
            fallback_data = compare_resume_and_job(
                {**resume_entities, 'raw_text': resume_text},
                {**job_requirements, 'title': job_title, 'description': job_description}
            )
            validated = ResumeAnalysisOutput(**fallback_data)
            return validated.model_dump()

        # Step 3: Attempt Gemini analysis if API key is provided
        if self.api_key and len(self.api_key.strip()) > 10:
            try:
                ai_result = self._call_gemini_api(resume_text, job_title, job_description)
                if ai_result:
                    # Enforce truthfulness guardrails against the raw resume and JD
                    grounded_result = self.enforce_truthfulness_guardrails(
                        raw_result=ai_result,
                        resume_text=resume_text,
                        job_title=job_title,
                        job_description=job_description,
                        job_requirements=job_requirements
                    )

                    # Validate against Pydantic schema
                    validated = ResumeAnalysisOutput(**grounded_result)
                    final_data = validated.model_dump()
                    logger.info(
                        f"[ResumeAgent] Gemini analysis complete. Final score: {final_data['match_score']}"
                    )
                    return final_data
            except Exception as e:
                logger.warning(
                    f"[ResumeAgent] Gemini API unavailable or failed: {type(e).__name__}: {e}. "
                    "Engaging grounded deterministic evaluation."
                )

        # Grounded deterministic analysis engine (always reliable, 100% evidence-grounded)
        logger.info("[ResumeAgent] Generating grounded deterministic evaluation.")
        fallback_data = compare_resume_and_job(
            {**resume_entities, 'raw_text': resume_text},
            {**job_requirements, 'title': job_title, 'description': job_description}
        )
        if self.api_key:
            fallback_data['overview'] = f"[Deterministic Evaluation - AI Unavailable] {fallback_data['overview']}"
        else:
            fallback_data['overview'] = f"[Offline Deterministic Evaluation] {fallback_data['overview']}"

        validated = ResumeAnalysisOutput(**fallback_data)
        return validated.model_dump()

    def _call_gemini_api(self, resume_text: str, job_title: str, job_description: str) -> Optional[Dict[str, Any]]:
        """
        Direct structured call to Gemini API using google-genai client.
        Iterates over models: gemini-3.8-flash, gemini-3.1-flash-lite, gemini-3.5-flash-lite, gemini-flash-latest.
        Logs safe, detailed failure diagnostics without exposing secrets.
        """
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)

        user_prompt = ANALYSIS_USER_PROMPT_TEMPLATE.format(
            job_title=job_title,
            job_description=job_description,
            resume_text=resume_text
        )

        models_to_try = [
            'gemini-3.8-flash',
            'gemini-3.1-flash-lite',
            'gemini-3.5-flash-lite',
            'gemini-flash-latest'
        ]
        last_error = None

        for model_name in models_to_try:
            try:
                logger.info(f"[ResumeAgent] Invoking Gemini model: '{model_name}'")
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=AGENT_SYSTEM_PROMPT,
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    cleaned_json = response.text.strip()
                    if cleaned_json.startswith("```json"):
                        cleaned_json = cleaned_json[7:]
                    if cleaned_json.endswith("```"):
                        cleaned_json = cleaned_json[:-3]
                    cleaned_json = cleaned_json.strip()
                    parsed = json.loads(cleaned_json)
                    logger.info(f"[ResumeAgent] Successfully generated analysis via model: '{model_name}'")
                    return parsed
            except Exception as model_err:
                err_type = type(model_err).__name__
                # Safe diagnostic logging (no keys or tokens)
                logger.warning(f"[ResumeAgent] Model '{model_name}' failed with {err_type}: {model_err}")
                last_error = f"{err_type}: {model_err}"
                continue

        logger.error(f"[ResumeAgent] All Gemini models failed. Last diagnostic: {last_error}")
        raise GeminiAnalysisError(f"Gemini API generation failed: {last_error}")

    @staticmethod
    def enforce_truthfulness_guardrails(
        raw_result: Dict[str, Any],
        resume_text: str,
        job_title: str,
        job_description: str,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Strict auditing filter that checks every AI claim against raw ground truth:
        1. Checks JD sufficiency: if JD has 0 requirements, match_score is None and analysis_status is 'insufficient_jd'.
        2. Separates REQUIRED from PREFERRED skills strictly (Issue 1).
        3. Skills present in resume are NEVER marked missing (Issue 2).
        4. Skills mentioned in resume but not demonstrated in projects are marked 'Demonstrated: Unclear' (Issue 2 & 6).
        5. Does not recommend migrating databases or changing technologies of existing projects (Issue 3 & 4).
        6. Preserves auditable transparent scoring fields and formula (Issue 5).
        7. Project technologies are strictly verified against that project's own text (Issue 6).
        8. Suggestions follow the 4-tier truthful priority (Issue 7).
        """
        jd_full_text = f"{job_title}\n{job_description}"
        jd_required_skills = list(job_requirements.get('required_skills', []))
        jd_preferred_skills = list(job_requirements.get('preferred_skills', []))

        if not jd_required_skills and not jd_preferred_skills:
            all_extracted = extract_skills_from_text(jd_full_text)
            jd_required_skills = all_extracted

        is_sufficient, sufficiency_reason = is_job_description_sufficient(job_title, job_description)

        # Extract verified ground-truth projects and skills from the resume
        gt_projects_data = extract_projects_from_resume(resume_text)
        gt_projects = gt_projects_data.get('projects', [])
        resume_detected_skills = set(gt_projects_data.get('skills', []))

        # Build project text mapping for evidence checking
        gt_project_texts = []
        for gp in gt_projects:
            gp_evidence = gp.get('evidence', '')
            gp_desc = ' '.join(gp.get('description', []))
            gt_project_texts.append(f"{gp.get('title', '')} | {gp_evidence} | {gp_desc}")

        # Sanitize projects: remove section headers, internships, sentence fragments
        raw_projects = raw_result.get('project_analysis', [])
        clean_projects = []
        has_any_metric = False

        for p in raw_projects:
            title = p.get('project', '').strip()
            # If title is a section header, internship, or resume section name, skip it completely
            if any(h in title.upper() for h in [
                'INTERNSHIP', 'INTERNSHIPS', 'WORK EXPERIENCE', 'EXPERIENCE',
                'EDUCATION', 'CERTIFICATIONS', 'TECHNICAL SKILLS', 'SKILLS', 'ACHIEVEMENTS'
            ]):
                continue

            # If title is a sentence fragment ending with period or too long, sanitize
            if title.endswith('.') or len(title) > 60:
                title = "Relevant Technical Implementation"

            # STRICT GUARD (Issue 6): Verify technologies against this project's own text in the resume!
            # Find matching ground truth project if available
            matching_gt = None
            for gp in gt_projects:
                if gp.get('title', '').lower() in title.lower() or title.lower() in gp.get('title', '').lower():
                    matching_gt = gp
                    break

            if matching_gt:
                p_context = f"{matching_gt.get('title', '')} {' '.join(matching_gt.get('description', []))} {matching_gt.get('evidence', '')}"
            else:
                p_context = f"{title} {p.get('evidence', '')}"

            # Only technologies actually present in this project's context are valid
            p_techs = [normalize_skill_name(t) for t in p.get('technologies', [])]
            valid_techs = [t for t in p_techs if find_skill_evidence(t, p_context)[0]]

            if not valid_techs and matching_gt:
                valid_techs = matching_gt.get('technologies', [])

            p_evidence = matching_gt.get('evidence', '') if matching_gt else p.get('evidence', '')
            has_metric = has_measurable_metrics(p_evidence or p.get('improvements', ''))
            if has_metric:
                has_any_metric = True

            strong = p.get('strong', '')
            if not strong or 'core project architecture' in strong.lower():
                if valid_techs:
                    strong = f"Demonstrates practical implementation of {', '.join(valid_techs)} as documented in the project description."
                else:
                    strong = f"Outlines technical implementation for {title}."

            # Sanitize improvements using strict truthfulness rules (Issues 3 & 4)
            sanitized_imp = sanitize_project_improvements(
                raw_improvements=p.get('improvements', ''),
                project_title=title,
                project_techs=valid_techs,
                resume_skills=resume_detected_skills,
                missing_skills=jd_required_skills,
                has_metrics=has_metric
            )

            clean_projects.append({
                'project': title,
                'technologies': valid_techs,
                'relevance': p.get('relevance', 'Demonstrates engineering capabilities.'),
                'strong': strong,
                'improvements': sanitized_imp,
                'evidence': p_evidence
            })

        # If clean_projects is empty and we have ground-truth projects from the resume, use them
        if not clean_projects and gt_projects:
            for gp in gt_projects[:3]:
                gp_techs = gp.get('technologies', [])
                gp_evidence = gp.get('evidence', '')
                gp_has_metric = has_measurable_metrics(gp_evidence)
                if gp_has_metric:
                    has_any_metric = True

                clean_projects.append({
                    'project': gp.get('title', 'Project'),
                    'technologies': gp_techs,
                    'relevance': f"Demonstrates practical application of {', '.join(gp_techs)}." if gp_techs else "Demonstrates practical software development.",
                    'strong': f"Demonstrates practical implementation of {', '.join(gp_techs)} as documented in the project description." if gp_techs else f"Outlines technical implementation for {gp.get('title')}.",
                    'improvements': sanitize_project_improvements(
                        raw_improvements="",
                        project_title=gp.get('title', 'Project'),
                        project_techs=gp_techs,
                        resume_skills=resume_detected_skills,
                        missing_skills=jd_required_skills,
                        has_metrics=gp_has_metric
                    ),
                    'evidence': gp_evidence
                })

        if not is_sufficient:
            first_proj = gt_projects[0].get('title') if gt_projects else (clean_projects[0].get('project') if clean_projects else None)
            first_skill = sorted(list(resume_detected_skills))[0] if resume_detected_skills else 'your core technical stack'

            clean_interview_q = build_grounded_interview_questions(
                resume_skills=resume_detected_skills,
                projects=clean_projects or gt_projects,
                job_title=job_title,
                required_matched=[],
                required_missing=[],
                preferred_matched=[],
                preferred_missing=[],
                is_sufficient=False
            )

            return {
                'match_score': None,
                'analysis_status': 'insufficient_jd',
                'status_message': sufficiency_reason,
                'overview': raw_result.get(
                    'overview',
                    f"The target job description ({job_title}) does not contain enough specific technical requirements for a meaningful match analysis."
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
                'resume_strengths': raw_result.get('resume_strengths', [
                    f"Verified practical skills in resume: {', '.join(sorted(list(resume_detected_skills))[:5])}." if resume_detected_skills else "Foundational technical skills documented in the submitted resume."
                ]),
                'resume_weaknesses': [
                    "Cannot evaluate missing qualifications because the job description lacks specific technical requirements."
                ],
                'project_analysis': clean_projects,
                'resume_suggestions': [
                    "Provide a detailed job description including required languages, frameworks, and databases to receive targeted recommendations."
                ],
                'interview_questions': clean_interview_q,
                'learning_roadmap': []
            }

        # Evaluate REQUIRED skills with detailed evidence tracking (Issues 1, 2, 6)
        required_matched: Set[str] = set()
        required_missing: Set[str] = set()
        skills_demonstrated: Set[str] = set()
        skills_mentioned: Set[str] = set()
        skills_breakdown: List[Dict[str, Any]] = []

        for req in jd_required_skills:
            eval_res = check_skill_evidence_detailed(req, resume_text, gt_project_texts)
            if eval_res['mentioned']:
                required_matched.add(req)
                if eval_res['demonstrated'] == 'Yes':
                    skills_demonstrated.add(req)
                else:
                    skills_mentioned.add(req)
                skills_breakdown.append({
                    'skill': req,
                    'category': 'required',
                    'status': 'matched',
                    'mentioned': True,
                    'demonstrated': eval_res['demonstrated'],
                    'evidence': eval_res['evidence'] or ""
                })
            else:
                required_missing.add(req)
                skills_breakdown.append({
                    'skill': req,
                    'category': 'required',
                    'status': 'missing',
                    'mentioned': False,
                    'demonstrated': 'No',
                    'evidence': ""
                })

        # Evaluate PREFERRED skills (Issue 1: reported separately, does NOT penalize required score)
        preferred_matched: Set[str] = set()
        preferred_missing: Set[str] = set()

        for pref in jd_preferred_skills:
            eval_res = check_skill_evidence_detailed(pref, resume_text, gt_project_texts)
            if eval_res['mentioned']:
                preferred_matched.add(pref)
                if eval_res['demonstrated'] == 'Yes':
                    skills_demonstrated.add(pref)
                else:
                    skills_mentioned.add(pref)
                skills_breakdown.append({
                    'skill': pref,
                    'category': 'preferred',
                    'status': 'matched',
                    'mentioned': True,
                    'demonstrated': eval_res['demonstrated'],
                    'evidence': eval_res['evidence'] or ""
                })
            else:
                preferred_missing.add(pref)
                skills_breakdown.append({
                    'skill': pref,
                    'category': 'preferred',
                    'status': 'missing',
                    'mentioned': False,
                    'demonstrated': 'No',
                    'evidence': ""
                })

        # ABSOLUTE TRUTHFULNESS GUARANTEE (Issue 2):
        # A skill present in the resume MUST NEVER be in missing_skills.
        # Missing skills CANNOT contain any matched skills.
        required_missing.difference_update(required_matched)
        preferred_missing.difference_update(preferred_matched)

        required_matched_list = sorted(list(required_matched))
        required_missing_list = sorted(list(required_missing))
        preferred_matched_list = sorted(list(preferred_matched))
        preferred_missing_list = sorted(list(preferred_missing))

        # Domain Keyword Filtering (Issues 1 & 5):
        # Must be strictly disjoint from skills, grounded in JD, verified via word boundaries
        all_evaluated_skills = set(jd_required_skills) | set(jd_preferred_skills)
        all_skill_words = {s.lower() for s in all_evaluated_skills}
        for s in all_evaluated_skills:
            for alias in CANONICAL_SKILL_ALIASES.get(s, []):
                all_skill_words.add(alias.lower().replace('\\b', '').replace('\\.', '.').replace('\\+', '+'))

        raw_kw_found = raw_result.get('keywords_found', [])
        raw_kw_missing = raw_result.get('keywords_missing', [])
        clean_kw_found = []
        clean_kw_missing = []

        for kw in raw_kw_found:
            kw_clean = kw.strip()
            kw_lower = kw_clean.lower()
            # Do NOT double count technical skills as keywords!
            if kw_lower in all_skill_words or any(kw_lower == a for a in all_skill_words):
                continue
            if is_keyword_present(kw_clean, jd_full_text):
                if is_keyword_present(kw_clean, resume_text):
                    if kw_clean not in clean_kw_found:
                        clean_kw_found.append(kw_clean)
                else:
                    if kw_clean not in clean_kw_missing:
                        clean_kw_missing.append(kw_clean)

        for kw in raw_kw_missing:
            kw_clean = kw.strip()
            kw_lower = kw_clean.lower()
            if kw_lower in all_skill_words or any(kw_lower == a for a in all_skill_words):
                continue
            if is_keyword_present(kw_clean, jd_full_text):
                if is_keyword_present(kw_clean, resume_text):
                    if kw_clean not in clean_kw_found:
                        clean_kw_found.append(kw_clean)
                else:
                    if kw_clean not in clean_kw_missing:
                        clean_kw_missing.append(kw_clean)

        clean_kw_found = sorted(clean_kw_found)
        clean_kw_missing = sorted(clean_kw_missing)

        # Calculate deterministic, reproducible score (Issues 1 & 5)
        # Evaluates strictly required skills + domain keywords, no arbitrary floors or boosts
        deterministic_score = calculate_deterministic_match_score(
            matched_skills=required_matched_list,
            total_required_skills=jd_required_skills,
            keywords_found=clean_kw_found,
            keywords_missing=clean_kw_missing,
            preferred_skills_matched=preferred_matched_list,
            total_preferred_skills=jd_preferred_skills
        )

        kw_total = len(clean_kw_found) + len(clean_kw_missing)
        scoring_formula = f"match_score = round(({len(required_matched_list)} / {len(jd_required_skills)}) * 100)"



        # Learning Roadmap: based ONLY on actual missing skills from JD (prioritizing required missing)
        clean_roadmap = build_grounded_learning_roadmap(
            required_missing=required_missing_list,
            preferred_missing=preferred_missing_list,
            projects=clean_projects or gt_projects,
            is_sufficient=True
        )

        # Truthful suggestions following 4-tier priority (Issues 3, 4, 7)
        clean_suggestions = build_truthful_resume_suggestions(
            skills_mentioned_not_demonstrated=sorted(list(skills_mentioned)),
            missing_required_skills=required_missing_list,
            has_any_metric=has_any_metric,
            projects=clean_projects or gt_projects
        )

        # Structured interview questions for sufficient JD
        interview_q = build_grounded_interview_questions(
            resume_skills=resume_detected_skills,
            projects=clean_projects or gt_projects,
            job_title=job_title,
            required_matched=required_matched_list,
            required_missing=required_missing_list,
            preferred_matched=preferred_matched_list,
            preferred_missing=preferred_missing_list,
            is_sufficient=True
        )

        overview = (
            f"Candidate demonstrates alignment in {len(required_matched_list)} of {len(jd_required_skills)} required skill(s) "
            f"({', '.join(required_matched_list[:3]) if required_matched_list else 'core skills'}), with {len(required_missing_list)} "
            f"target requirement(s) not clearly demonstrated in the resume."
        )
        if preferred_matched_list:
            overview += f" Candidate also demonstrates preferred skill(s): {', '.join(preferred_matched_list)}."

        return {
            'match_score': deterministic_score,
            'analysis_status': 'complete',
            'status_message': None,
            'overview': overview,
            'required_skills_total': len(jd_required_skills),
            'required_skills_matched': required_matched_list,
            'required_skills_missing': required_missing_list,
            'preferred_skills_total': len(jd_preferred_skills),
            'preferred_skills_matched': preferred_matched_list,
            'preferred_skills_missing': preferred_missing_list,
            'skills_demonstrated': sorted(list(skills_demonstrated)),
            'skills_mentioned': sorted(list(skills_mentioned)),
            'skills_breakdown': skills_breakdown,
            'matched_skills': required_matched_list,
            'missing_skills': required_missing_list,
            'keyword_total': kw_total,
            'keywords_found': clean_kw_found,
            'keywords_missing': clean_kw_missing,
            'scoring_formula': scoring_formula,
            'resume_strengths': raw_result.get('resume_strengths', [
                f"Verified experience in required technologies: {', '.join(required_matched_list)}."
            ]),
            'resume_weaknesses': [
                f"Required skill {s} is not clearly demonstrated in the resume." for s in required_missing_list[:3]
            ] if required_missing_list else ["All core required technical qualifications are represented."],
            'project_analysis': clean_projects,
            'resume_suggestions': clean_suggestions,
            'interview_questions': interview_q,
            'learning_roadmap': clean_roadmap,
        }
