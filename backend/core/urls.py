"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """Lightweight health-check endpoint for Render uptime monitoring."""
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', health_check, name='health-check'),
    path('api/accounts/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/resumes/', include('resumes.urls')),
]
