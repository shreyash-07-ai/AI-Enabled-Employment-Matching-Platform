from rest_framework import serializers
from .models import JobPosting

class JobPostingSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(source='recruiter.company_name', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ('recruiter',)
