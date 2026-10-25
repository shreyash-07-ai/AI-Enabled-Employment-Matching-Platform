from django.db import models
from accounts.models import RecruiterProfile

class JobPosting(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('DRAFT', 'Draft'),
    )
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma-separated required skills")
    education_requirement = models.CharField(max_length=255, blank=True)
    experience_requirement = models.DecimalField(max_digits=4, decimal_places=1, default=0.0, help_text="Minimum years of experience")
    salary_range = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.recruiter.company_name})"
