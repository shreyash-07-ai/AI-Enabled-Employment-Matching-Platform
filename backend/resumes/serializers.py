from rest_framework import serializers
from .models import UploadedResume, JobApplication

class UploadedResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedResume
        fields = '__all__'
        read_only_fields = ('job_seeker', 'parsed_text', 'extracted_skills', 'extracted_education', 'extracted_experience')

class JobApplicationSerializer(serializers.ModelSerializer):
    job_seeker_name = serializers.CharField(source='job_seeker.user.username', read_only=True)
    job_title = serializers.CharField(source='job_posting.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('match_score_pct', 'missing_skills', 'status', 'applied_at')
