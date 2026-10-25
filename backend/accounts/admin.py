from django.contrib import admin
from .models import User, JobSeekerProfile, RecruiterProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'location', 'experience_years', 'resume_completion_percentage')
    search_fields = ('user__username',)

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'position', 'phone')
    search_fields = ('user__username', 'company_name')
