"""
Views for User and StudentProfile management.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import StudentProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    StudentProfileSerializer,
    StudentProfileCreateSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    GET /api/auth/me/
    Get current authenticated user.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/profiles/me/
    PUT /api/profiles/me/
    Get or update the current user's student profile.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StudentProfileCreateSerializer
        return StudentProfileSerializer

    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'name': self.request.user.username}
        )
        return profile


class StudentProfileCreateView(generics.CreateAPIView):
    """
    POST /api/profiles/
    Create a new student profile for the current user.
    """
    serializer_class = StudentProfileCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
