from django.contrib import admin
from .models import JobPosting

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter', 'status', 'location', 'experience_requirement', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'required_skills')
