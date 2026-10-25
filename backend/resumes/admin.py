from django.contrib import admin
from .models import UploadedResume, JobApplication

@admin.register(UploadedResume)
class UploadedResumeAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'file', 'uploaded_at')
    search_fields = ('job_seeker__user__username',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'job_posting', 'match_score_pct', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('job_seeker__user__username', 'job_posting__title')
