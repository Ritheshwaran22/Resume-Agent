from django.contrib import admin
from .models import Analysis

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'job_title_display', 'resume_name_display', 'match_score', 'created_at')
    list_filter = ('created_at', 'match_score', 'user')
    search_fields = ('user__username', 'job_description__title', 'resume__filename')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'match_score', 'result')

    def job_title_display(self, obj):
        return obj.job_description.title
    job_title_display.short_description = 'Job Title'

    def resume_name_display(self, obj):
        return obj.resume.filename
    resume_name_display.short_description = 'Resume'
