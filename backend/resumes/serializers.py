from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    text_preview = serializers.SerializerMethodField()
    analysis_count = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ('id', 'filename', 'file', 'file_size', 'text_preview', 'analysis_count', 'extracted_text', 'uploaded_at')
        read_only_fields = ('id', 'filename', 'file_size', 'text_preview', 'analysis_count', 'extracted_text', 'uploaded_at')

    def get_analysis_count(self, obj):
        try:
            return obj.analyses.count()
        except Exception:
            return 0

    def get_file_size(self, obj):
        try:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            return f"{size / (1024 * 1024):.2f} MB"
        except Exception:
            return "N/A"

    def get_text_preview(self, obj):
        if not obj.extracted_text:
            return ""
        return obj.extracted_text[:200] + ('...' if len(obj.extracted_text) > 200 else '')

