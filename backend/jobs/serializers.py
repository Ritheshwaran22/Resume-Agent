from rest_framework import serializers
from .models import JobDescription

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ('id', 'title', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Job title must be at least 2 characters long.")
        return cleaned

    def validate_description(self, value):
        cleaned = value.strip()
        if len(cleaned) < 20:
            raise serializers.ValidationError("Job description must contain at least 20 characters of requirements.")
        return cleaned
