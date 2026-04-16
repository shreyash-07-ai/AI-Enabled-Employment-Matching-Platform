from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('RECRUITER', 'Recruiter'),
        ('JOB_SEEKER', 'Job Seeker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='JOB_SEEKER')
    
    def __str__(self):
        return f"{self.username} - {self.role}"

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    education = models.TextField(blank=True, help_text="Summary of education")
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    certifications = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    resume_completion_percentage = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.company_name})"
