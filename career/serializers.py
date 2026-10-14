from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'resume_file', 'target_role', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']