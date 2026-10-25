from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, JobSeekerProfileView, RecruiterProfileView, CustomTokenObtainPairView
)
from .dashboard_views import (
    AdminDashboardView, RecruiterDashboardView, JobSeekerDashboardView, AdminUsersListView
)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profiles
    path('profile/job-seeker/', JobSeekerProfileView.as_view(), name='job_seeker_profile'),
    path('profile/recruiter/', RecruiterProfileView.as_view(), name='recruiter_profile'),

    # Dashboards
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('dashboard/recruiter/', RecruiterDashboardView.as_view(), name='recruiter-dashboard'),
    path('dashboard/job-seeker/', JobSeekerDashboardView.as_view(), name='job-seeker-dashboard'),

    # Admin User Management
    path('admin/users/', AdminUsersListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', AdminUsersListView.as_view(), name='admin-user-update'),
]
