from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UploadedResume, JobApplication
from .serializers import UploadedResumeSerializer, JobApplicationSerializer
from .matching_engine import compute_match, extract_text_from_file, extract_skills_from_text
from jobs.models import JobPosting

import logging
log = logging.getLogger(__name__)


class UploadedResumeCreateView(generics.CreateAPIView):
    serializer_class = UploadedResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        resume = serializer.save(job_seeker=self.request.user.job_seeker_profile)
        # Synchronous parsing (Celery optional — works without Redis)
        try:
            file_path = resume.file.path
            raw_text = extract_text_from_file(file_path)
            if raw_text.strip():
                resume.parsed_text = raw_text
                skills = extract_skills_from_text(raw_text)
                resume.extracted_skills = ", ".join(skills)
                resume.save()
        except Exception as e:
            log.error(f"Resume parse error: {e}")


class MyResumesView(generics.ListAPIView):
    serializer_class = UploadedResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UploadedResume.objects.filter(
            job_seeker=self.request.user.job_seeker_profile
        ).order_by('-uploaded_at')


class ApplyJobView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        job_id = request.data.get('job_posting')
        resume_id = request.data.get('resume')

        try:
            job = JobPosting.objects.get(id=job_id)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.job_seeker_profile

        # Check duplicate application
        if JobApplication.objects.filter(job_posting=job, job_seeker=profile).exists():
            return Response({"error": "Already applied"}, status=status.HTTP_400_BAD_REQUEST)

        resume = None
        resume_text = ""
        if resume_id:
            try:
                resume = UploadedResume.objects.get(id=resume_id, job_seeker=profile)
                resume_text = resume.parsed_text or ""
            except UploadedResume.DoesNotExist:
                pass

        if not resume_text:
            latest = profile.resumes.order_by('-uploaded_at').first()
            if latest:
                resume = latest
                resume_text = latest.parsed_text or ""

        # Compute match score
        match_result = {"match_score_pct": 0, "missing_skills": []}
        if resume_text:
            try:
                match_result = compute_match(resume_text, job.description)
            except Exception as e:
                log.error(f"Match computation error: {e}")

        application = JobApplication.objects.create(
            job_posting=job,
            job_seeker=profile,
            resume=resume,
            match_score_pct=match_result["match_score_pct"],
            missing_skills=", ".join(match_result.get("missing_skills", [])),
        )

        return Response(JobApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class JobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return JobApplication.objects.filter(
            job_seeker=self.request.user.job_seeker_profile
        ).order_by('-applied_at')


class RecruiterApplicantsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return JobApplication.objects.filter(
            job_posting__id=job_id,
            job_posting__recruiter=self.request.user.recruiter_profile
        ).order_by('-match_score_pct')


class UpdateApplicationStatusView(APIView):
    """Recruiter can shortlist / reject / hire candidates"""
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk):
        new_status = request.data.get('status')
        if new_status not in ['SHORTLISTED', 'REJECTED', 'HIRED']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            application = JobApplication.objects.get(
                id=pk,
                job_posting__recruiter=request.user.recruiter_profile
            )
            application.status = new_status
            application.save()
            return Response(JobApplicationSerializer(application).data)
        except JobApplication.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


class MatchAnalysisView(APIView):
    """Get detailed match analysis for a resume against a job."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, application_id):
        try:
            app = JobApplication.objects.select_related(
                'resume', 'job_posting'
            ).get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        resume_text = app.resume.parsed_text if app.resume else ""
        if not resume_text:
            return Response({"error": "No resume text"}, status=status.HTTP_400_BAD_REQUEST)

        result = compute_match(resume_text, app.job_posting.description)
        result["application_id"] = app.id
        result["job_title"] = app.job_posting.title
        return Response(result)


class RecommendedJobsView(APIView):
    """Get recommended jobs for the current job seeker based on their resume."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = request.user.job_seeker_profile
        latest_resume = profile.resumes.order_by('-uploaded_at').first()

        if not latest_resume or not latest_resume.parsed_text:
            return Response({"jobs": [], "message": "Upload a resume first"})

        resume_text = latest_resume.parsed_text
        active_jobs = JobPosting.objects.filter(status='ACTIVE')[:50]

        recommendations = []
        for job in active_jobs:
            try:
                result = compute_match(resume_text, job.description)
                from jobs.serializers import JobPostingSerializer
                job_data = JobPostingSerializer(job).data
                job_data['match_score_pct'] = result['match_score_pct']
                job_data['matched_skills'] = result['matched_skills']
                job_data['missing_skills'] = result['missing_skills']
                recommendations.append(job_data)
            except Exception:
                pass

        recommendations.sort(key=lambda x: x['match_score_pct'], reverse=True)
        return Response({"jobs": recommendations[:20]})
