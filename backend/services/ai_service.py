import logging
from typing import Dict, Any, Optional
from agent.agent import ResumeAgent, GeminiAnalysisError

logger = logging.getLogger(__name__)

class AIService:
    """
    Service layer providing unified access to the AI Resume Agent.
    """
    _agent_instance = None

    @classmethod
    def get_agent(cls) -> ResumeAgent:
        if cls._agent_instance is None:
            cls._agent_instance = ResumeAgent()
        return cls._agent_instance

    @classmethod
    def analyze_resume(
        cls,
        resume_text: str,
        job_title: str,
        job_description: str,
        resume_id: Optional[Any] = None,
        job_id: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Coordinates analysis of resume against target job description.
        Returns validated structured dictionary.
        """
        agent = cls.get_agent()
        return agent.analyze(
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            resume_id=resume_id,
            job_id=job_id
        )
