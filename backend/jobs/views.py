from rest_framework import generics, permissions
from .models import JobPosting
from .serializers import JobPostingSerializer

class JobPostingListCreateView(generics.ListCreateAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return JobPosting.objects.filter(status='ACTIVE').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user.recruiter_profile)

class JobPostingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return JobPosting.objects.all()

class RecruiterJobsListView(generics.ListAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return JobPosting.objects.filter(recruiter=self.request.user.recruiter_profile).order_by('-created_at')
