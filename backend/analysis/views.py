import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Analysis
from .serializers import AnalysisSerializer, AnalysisStartSerializer
from resumes.models import Resume
from jobs.models import JobDescription
from services.ai_service import AIService
from agent.agent import GeminiAnalysisError

logger = logging.getLogger(__name__)

class AnalysisStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnalysisStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 1. Verify resume belongs strictly to authenticated user
        resume_id = data['resume_id']
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            raise NotFound("Resume not found or does not belong to your account.")

        if not resume.extracted_text or len(resume.extracted_text.strip()) < 20:
            raise ValidationError(
                "The selected resume does not contain sufficient extracted text for analysis. Please re-upload your resume."
            )

        # 2. Verify or create job description strictly belonging to authenticated user
        job_id = data.get('job_description_id')
        if job_id:
            try:
                job = JobDescription.objects.get(id=job_id, user=request.user)
            except JobDescription.DoesNotExist:
                raise NotFound("Job description not found or does not belong to your account.")
        else:
            job_title = data.get('job_title', 'Target Role').strip()
            job_text = data.get('job_description', '').strip()
            if len(job_text) < 20:
                raise ValidationError("Job description must contain at least 20 characters of requirements.")
            job = JobDescription.objects.create(
                user=request.user,
                title=job_title,
                description=job_text
            )

        # Safe development logging
        logger.info(
            f"[AnalysisStartView] User {request.user.id} requested analysis: "
            f"Resume #{resume.id} ({resume.filename}, {len(resume.extracted_text)} chars), "
            f"Job #{job.id} ({job.title}, {len(job.description)} chars)"
        )

        # 3. Call AI Resume Agent
        try:
            analysis_result = AIService.analyze_resume(
                resume_text=resume.extracted_text,
                job_title=job.title,
                job_description=job.description,
                resume_id=resume.id,
                job_id=job.id
            )
        except GeminiAnalysisError as e:
            logger.error(f"[AnalysisStartView] Gemini analysis error: {e}")
            return Response(
                {"detail": "Analysis could not be completed. Please try again in a moment. Your resume and job description were not modified."},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.error(f"[AnalysisStartView] Unexpected error during analysis: {e}", exc_info=True)
            return Response(
                {"detail": "Analysis could not be completed. Please try again in a moment. Your resume and job description were not modified."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        match_score = analysis_result.get('match_score', 0)

        # 4. Save validated analysis to database
        analysis = Analysis.objects.create(
            user=request.user,
            resume=resume,
            job_description=job,
            match_score=match_score,
            result=analysis_result
        )

        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED
        )

class AnalysisListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        # Strict user isolation
        return Analysis.objects.filter(user=self.request.user)

class AnalysisDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        # Strict user isolation
        return Analysis.objects.filter(user=self.request.user)
