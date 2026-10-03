"""
Pydantic Schemas for AI Resume Agent structured output.
Guarantees validated, crash-proof output formats.
Supports insufficient job descriptions with null scores and status metadata.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator

class ProjectAnalysisItem(BaseModel):
    project: str = Field(description="Name or title of the project identified in the resume")
    technologies: List[str] = Field(default_factory=list, description="Technologies confirmed in the project")
    relevance: str = Field(description="Relevance to the target job description")
    strong: str = Field(description="What is well-demonstrated in this project based on resume text")
    improvements: str = Field(description="Actionable truthful recommendations for outcome clarity")
    evidence: Optional[str] = Field(default="", description="Supporting quote or excerpt from the resume")

class InterviewQuestionItem(BaseModel):
    question: str = Field(description="The interview question text")
    guidance: Optional[str] = Field(default="", description="Actionable preparation guidance for the candidate")

class LearningRoadmapItem(BaseModel):
    week: str = Field(description="Milestone identifier, e.g. 'Week 1'")
    title: str = Field(description="Subject or skill topic to learn")
    description: str = Field(description="Concrete practical learning objective")
    skills: List[str] = Field(default_factory=list, description="Targeted skills being acquired")
    stage: Optional[str] = Field(default=None, description="Stage or phase label, e.g. 'Week 1: Core Required'")
    skill: Optional[str] = Field(default=None, description="Canonical skill name being learned")
    priority: str = Field(default="required", description="'required' or 'preferred'")
    why_it_matters: Optional[str] = Field(default=None, description="Why this skill is relevant to the target role")
    what_to_learn: List[str] = Field(default_factory=list, description="Key concepts and fundamentals to study")
    practical_task: Optional[str] = Field(default=None, description="Hands-on practice task connected to candidate projects")
    expected_outcome: Optional[str] = Field(default=None, description="Demonstrable capability gained")

class SkillEvaluationItem(BaseModel):
    skill: str = Field(description="Canonical name of the skill")
    category: str = Field(default="required", description="'required' or 'preferred'")
    status: str = Field(description="'matched' or 'missing'")
    mentioned: bool = Field(default=False, description="Whether skill is explicitly present in the resume")
    demonstrated: str = Field(default="No", description="'Yes' (demonstrated in projects/work), 'Unclear' (mentioned only), or 'No'")
    evidence: Optional[str] = Field(default="", description="Snippet or context confirming the skill")

class ResumeAnalysisOutput(BaseModel):
    match_score: Optional[int] = Field(default=None, description="Resume-to-job match comparison indicator (0-100), or None if insufficient JD")
    analysis_status: str = Field(default="complete", description="Status: 'complete' | 'insufficient_jd' | 'offline'")
    status_message: Optional[str] = Field(default=None, description="Explanatory message if JD is insufficient or offline")
    overview: str = Field(description="Executive summary of alignment without claiming hiring probability")

    # Required vs Preferred Skills Separation
    required_skills_total: int = Field(default=0, description="Total count of required skills in JD")
    required_skills_matched: List[str] = Field(default_factory=list, description="Required skills confirmed in resume")
    required_skills_missing: List[str] = Field(default_factory=list, description="Required skills missing from resume")

    preferred_skills_total: int = Field(default=0, description="Total count of preferred skills in JD")
    preferred_skills_matched: List[str] = Field(default_factory=list, description="Preferred skills present in resume")
    preferred_skills_missing: List[str] = Field(default_factory=list, description="Preferred skills missing from resume")

    # Evidence grounding: Mentioned vs Demonstrated
    skills_demonstrated: List[str] = Field(default_factory=list, description="Skills backed by project or work experience evidence")
    skills_mentioned: List[str] = Field(default_factory=list, description="Skills mentioned in skills section or summary without project demonstration")
    skills_breakdown: List[SkillEvaluationItem] = Field(default_factory=list, description="Itemized evidence evaluation for each evaluated skill")

    # Backwards-compatible aliases
    matched_skills: List[str] = Field(default_factory=list, description="Skills present in both resume and job description (required matched)")
    missing_skills: List[str] = Field(default_factory=list, description="Core requirements in job description missing from resume")

    # Domain Keywords (Disjoint from skills)
    keyword_total: int = Field(default=0, description="Total domain keywords identified in JD")
    keywords_found: List[str] = Field(default_factory=list, description="Domain keywords present in resume")
    keywords_missing: List[str] = Field(default_factory=list, description="Domain keywords not found in resume")

    # Auditability
    scoring_formula: Optional[str] = Field(default="", description="Explicit deterministic formula used to compute score")

    resume_strengths: List[str] = Field(default_factory=list, description="Factual strengths supported by documented experience")
    resume_weaknesses: List[str] = Field(default_factory=list, description="Factual areas for improvement based on missing job requirements")
    project_analysis: List[ProjectAnalysisItem] = Field(default_factory=list, description="Analysis of identified resume projects")
    resume_suggestions: List[str] = Field(default_factory=list, description="Truthful, conditional improvement suggestions")
    interview_questions: Dict[str, List[Union[str, InterviewQuestionItem, Dict[str, Any]]]] = Field(default_factory=dict, description="Categorized interview practice questions")
    learning_roadmap: List[LearningRoadmapItem] = Field(default_factory=list, description="Week-by-week curriculum for missing skills")

    @field_validator('match_score')
    @classmethod
    def clamp_score(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        return max(0, min(100, v))
