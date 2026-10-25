"""
Dashboard & analytics API views for Admin, Recruiter, and Job Seeker dashboards.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, JobSeekerProfile, RecruiterProfile
from jobs.models import JobPosting
from resumes.models import JobApplication, UploadedResume


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'ADMIN' or request.user.is_superuser
        )


class AdminDashboardView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        total_users = User.objects.filter(role='JOB_SEEKER').count()
        total_recruiters = User.objects.filter(role='RECRUITER').count()
        active_jobs = JobPosting.objects.filter(status='ACTIVE').count()
        total_applications = JobApplication.objects.count()

        # Most demanded skills (from job postings)
        all_skills_text = " ".join(
            JobPosting.objects.filter(status='ACTIVE').values_list('required_skills', flat=True)
        )
        skill_counts = {}
        for s in all_skills_text.lower().replace(",", " ").split():
            s = s.strip()
            if len(s) > 1:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Applications by status
        status_counts = dict(
            JobApplication.objects.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # Recent registrations (last 30 days)
        recent_date = timezone.now() - timedelta(days=30)
        recent_users = User.objects.filter(date_joined__gte=recent_date).count()

        # Average match score
        avg_score = JobApplication.objects.aggregate(avg=Avg('match_score_pct'))['avg'] or 0

        return Response({
            "total_users": total_users,
            "total_recruiters": total_recruiters,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
            "application_status_counts": status_counts,
            "recent_registrations": recent_users,
            "average_match_score": round(float(avg_score), 2),
        })


class RecruiterDashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = request.user.recruiter_profile
        jobs = JobPosting.objects.filter(recruiter=profile)

        total_jobs = jobs.count()
        active_jobs = jobs.filter(status='ACTIVE').count()
        total_applications = JobApplication.objects.filter(job_posting__recruiter=profile).count()

        # Top matching candidates across all jobs
        top_candidates = JobApplication.objects.filter(
            job_posting__recruiter=profile
        ).order_by('-match_score_pct').values(
            'id', 'job_seeker__user__username', 'job_posting__title',
            'match_score_pct', 'status'
        )[:10]

        # Applications per job
        apps_per_job = list(jobs.annotate(
            app_count=Count('applications')
        ).values('id', 'title', 'app_count').order_by('-app_count')[:10])

        # Skill demand from my postings
        all_skills_text = " ".join(jobs.values_list('required_skills', flat=True))
        skill_counts = {}
        for s in all_skills_text.lower().replace(",", " ").split():
            s = s.strip()
            if len(s) > 1:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return Response({
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "top_candidates": list(top_candidates),
            "applications_per_job": apps_per_job,
            "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        })


class JobSeekerDashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = request.user.job_seeker_profile

        total_applications = JobApplication.objects.filter(job_seeker=profile).count()
        applications = JobApplication.objects.filter(job_seeker=profile).order_by('-applied_at')

        # Application status breakdown
        status_counts = dict(
            applications.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # Match scores for chart
        match_scores = list(applications.values(
            'job_posting__title', 'match_score_pct', 'status', 'applied_at'
        )[:20])

        # Resume completion
        resume_completion = profile.resume_completion_percentage

        # Latest resume skills
        latest_resume = profile.resumes.order_by('-uploaded_at').first()
        my_skills = []
        if latest_resume and latest_resume.extracted_skills:
            my_skills = [s.strip() for s in latest_resume.extracted_skills.split(',') if s.strip()]

        # Recent notifications (shortlisted/rejected)
        notifications = list(applications.exclude(
            status='APPLIED'
        ).values(
            'job_posting__title', 'status', 'applied_at'
        ).order_by('-applied_at')[:10])

        return Response({
            "total_applications": total_applications,
            "status_counts": status_counts,
            "match_scores": match_scores,
            "resume_completion": resume_completion,
            "my_skills": my_skills,
            "notifications": notifications,
        })


class AdminUsersListView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        users = User.objects.all().values(
            'id', 'username', 'email', 'role', 'is_active', 'date_joined'
        ).order_by('-date_joined')
        return Response(list(users))

    def patch(self, request, pk):
        """Activate/deactivate user"""
        try:
            user = User.objects.get(id=pk)
            user.is_active = request.data.get('is_active', user.is_active)
            user.save()
            return Response({"status": "updated"})
        except User.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
