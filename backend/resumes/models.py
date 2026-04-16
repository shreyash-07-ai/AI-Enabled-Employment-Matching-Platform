from django.db import models
from accounts.models import JobSeekerProfile
from jobs.models import JobPosting

class UploadedResume(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True)
    extracted_skills = models.TextField(blank=True)
    extracted_education = models.TextField(blank=True)
    extracted_experience = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume - {self.job_seeker.user.username}"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('HIRED', 'Hired'),
    )
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(UploadedResume, on_delete=models.SET_NULL, null=True, blank=True)
    match_score_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    missing_skills = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='APPLIED')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job_posting', 'job_seeker')
        
    def __str__(self):
        return f"{self.job_seeker.user.username} -> {self.job_posting.title}"
