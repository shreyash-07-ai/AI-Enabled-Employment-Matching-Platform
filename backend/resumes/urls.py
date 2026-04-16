from django.urls import path
from .views import (
    UploadedResumeCreateView, MyResumesView,
    ApplyJobView, JobApplicationsListView,
    RecruiterApplicantsView, UpdateApplicationStatusView,
    MatchAnalysisView, RecommendedJobsView,
)

urlpatterns = [
    path('upload/', UploadedResumeCreateView.as_view(), name='resume-upload'),
    path('my-resumes/', MyResumesView.as_view(), name='my-resumes'),
    path('apply/', ApplyJobView.as_view(), name='job-apply'),
    path('applications/', JobApplicationsListView.as_view(), name='my-applications'),
    path('applicants/<int:job_id>/', RecruiterApplicantsView.as_view(), name='recruiter-applicants'),
    path('application/<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-app-status'),
    path('match-analysis/<int:application_id>/', MatchAnalysisView.as_view(), name='match-analysis'),
    path('recommended-jobs/', RecommendedJobsView.as_view(), name='recommended-jobs'),
]
