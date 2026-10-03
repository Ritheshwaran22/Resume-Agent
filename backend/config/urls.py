"""
URL configuration for Resume Agent backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for Phase 1.
    Verifies that the Django REST API is live and responsive.
    """
    return Response({
        "status": "healthy",
        "service": "AI Resume Agent Backend",
        "phase": "Phase 1 - Project Setup",
        "django_version": "5.2.17",
        "message": "Backend API is up and running successfully."
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/accounts/', include('accounts.urls')),
    path('api/resumes/', include('resumes.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/analysis/', include('analysis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.http import JsonResponse

def custom_500_handler(request):
    return JsonResponse(
        {"detail": "An unexpected error occurred. Please try again later."},
        status=500
    )

def custom_404_handler(request, exception=None):
    return JsonResponse(
        {"detail": "The requested resource was not found."},
        status=404
    )

handler500 = 'config.urls.custom_500_handler'
handler404 = 'config.urls.custom_404_handler'

