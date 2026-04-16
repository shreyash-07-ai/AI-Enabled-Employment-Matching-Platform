from django.urls import path
from .views import JobPostingListCreateView, JobPostingDetailView, RecruiterJobsListView

urlpatterns = [
    path('', JobPostingListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', JobPostingDetailView.as_view(), name='job-detail'),
    path('recruiter/', RecruiterJobsListView.as_view(), name='recruiter-jobs'),
]
