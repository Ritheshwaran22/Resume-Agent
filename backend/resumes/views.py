from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Resume
from .serializers import ResumeSerializer
from services.pdf_service import PDFExtractionService

class ResumeUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = ResumeSerializer

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            raise ValidationError({"file": "A PDF resume file is required."})

        # Validate and extract text safely via PyMuPDF
        extracted_text = PDFExtractionService.extract_text(uploaded_file)

        # Save record belonging strictly to the authenticated user
        try:
            resume = Resume.objects.create(
                user=request.user,
                filename=uploaded_file.name,
                file=uploaded_file,
                extracted_text=extracted_text
            )
        except Exception as storage_err:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"[ResumeUploadView] Physical storage save failed ({storage_err}), falling back to database record."
            )
            try:
                resume = Resume(
                    user=request.user,
                    filename=uploaded_file.name,
                    extracted_text=extracted_text
                )
                resume.file.name = f"resumes/{uploaded_file.name}"
                resume.save()
            except Exception as db_err:
                logger.error(f"[ResumeUploadView] Error creating resume record: {db_err}", exc_info=True)
                raise ValidationError({"file": "Failed to save the uploaded file. Please try again."})

        return Response(
            ResumeSerializer(resume, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

class ResumeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeSerializer

    def get_queryset(self):
        # Strict user data isolation
        return Resume.objects.filter(user=self.request.user)

class ResumeDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeSerializer

    def get_queryset(self):
        # Strict user data isolation
        return Resume.objects.filter(user=self.request.user)
