from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import JobDescription
from .serializers import JobDescriptionSerializer

class JobListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobDescriptionSerializer

    def get_queryset(self):
        # Strict user isolation
        return JobDescription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobDescriptionSerializer

    def get_queryset(self):
        # Strict user isolation
        return JobDescription.objects.filter(user=self.request.user)
