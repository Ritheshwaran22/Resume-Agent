from django.urls import path
from .views import AnalysisStartView, AnalysisListView, AnalysisDetailView

urlpatterns = [
    path('start/', AnalysisStartView.as_view(), name='analysis_start'),
    path('', AnalysisListView.as_view(), name='analysis_list'),
    path('<int:pk>/', AnalysisDetailView.as_view(), name='analysis_detail'),
]
