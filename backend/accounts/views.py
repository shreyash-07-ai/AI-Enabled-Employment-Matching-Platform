from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User, JobSeekerProfile, RecruiterProfile
from .serializers import (
    UserSerializer, JobSeekerProfileSerializer, RecruiterProfileSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class JobSeekerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.job_seeker_profile

class RecruiterProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = RecruiterProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.recruiter_profile
