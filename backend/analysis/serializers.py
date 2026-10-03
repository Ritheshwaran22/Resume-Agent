from rest_framework import serializers
from .models import Analysis
from resumes.models import Resume
from jobs.models import JobDescription

class AnalysisSerializer(serializers.ModelSerializer):
    resume_filename = serializers.CharField(source='resume.filename', read_only=True)
    job_title = serializers.CharField(source='job_description.title', read_only=True)
    analysis_status = serializers.SerializerMethodField()
    required_skills_matched_count = serializers.SerializerMethodField()
    required_skills_total_count = serializers.SerializerMethodField()
    required_skills_missing_count = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = (
            'id', 'resume', 'resume_filename', 'job_description',
            'job_title', 'match_score', 'result', 'created_at',
            'analysis_status', 'required_skills_matched_count',
            'required_skills_total_count', 'required_skills_missing_count'
        )
        read_only_fields = ('id', 'created_at')

    def get_analysis_status(self, obj):
        if isinstance(obj.result, dict):
            return obj.result.get('analysis_status', 'complete')
        return 'complete'

    def get_required_skills_matched_count(self, obj):
        if isinstance(obj.result, dict):
            return len(obj.result.get('required_skills_matched', []))
        return 0

    def get_required_skills_total_count(self, obj):
        if isinstance(obj.result, dict):
            matched = len(obj.result.get('required_skills_matched', []))
            missing = len(obj.result.get('required_skills_missing', []))
            return obj.result.get('required_skills_total', matched + missing)
        return 0

    def get_required_skills_missing_count(self, obj):
        if isinstance(obj.result, dict):
            return len(obj.result.get('required_skills_missing', []))
        return 0


class AnalysisStartSerializer(serializers.Serializer):
    resume_id = serializers.IntegerField(required=True)
    job_description_id = serializers.IntegerField(required=False, allow_null=True)
    job_title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    job_description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('job_description_id') and not (attrs.get('job_title') and attrs.get('job_description')):
            raise serializers.ValidationError(
                "Either 'job_description_id' or both 'job_title' and 'job_description' must be provided."
            )
        return attrs
