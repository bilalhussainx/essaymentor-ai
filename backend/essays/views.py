"""
Views for Essay generation API.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import University, EssayGeneration, EssayVersion
from .serializers import (
    UniversitySerializer,
    EssayGenerationSerializer,
    EssayGenerationListSerializer,
    EssayGenerationCreateSerializer,
    EssayStatusSerializer,
    EssayVersionSerializer,
)
from .tasks import generate_essay_task


class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/essays/universities/
    GET /api/essays/universities/{code}/
    List and retrieve universities.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'


class EssayGenerationViewSet(viewsets.ModelViewSet):
    """
    Essay Generation API endpoints.

    POST   /api/essays/              - Start new generation
    GET    /api/essays/              - List user's essays
    GET    /api/essays/{id}/         - Get essay details
    DELETE /api/essays/{id}/         - Delete essay
    GET    /api/essays/{id}/status/  - Poll generation status
    POST   /api/essays/{id}/regenerate/ - Regenerate essay
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EssayGeneration.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return EssayGenerationCreateSerializer
        if self.action == 'list':
            return EssayGenerationListSerializer
        if self.action == 'status':
            return EssayStatusSerializer
        return EssayGenerationSerializer

    def create(self, request, *args, **kwargs):
        """Start a new essay generation - triggers Celery task."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        generation = serializer.save()

        # Start async generation task
        task = generate_essay_task.delay(str(generation.id))
        generation.celery_task_id = task.id
        generation.save()

        return Response(
            {
                'id': str(generation.id),
                'status': generation.status,
                'message': 'Essay generation started',
                'websocket_url': f'/ws/essays/{generation.id}/',
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Poll endpoint for generation status."""
        generation = self.get_object()
        serializer = EssayStatusSerializer(generation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate essay with same parameters."""
        generation = self.get_object()

        # Create new generation with same params
        new_generation = EssayGeneration.objects.create(
            user=request.user,
            profile=generation.profile,
            prompt=generation.prompt,
            target_university=generation.target_university,
            essay_type=generation.essay_type,
            word_count_target=generation.word_count_target,
        )

        # Start async task
        task = generate_essay_task.delay(str(new_generation.id))
        new_generation.celery_task_id = task.id
        new_generation.save()

        return Response(
            {
                'id': str(new_generation.id),
                'status': new_generation.status,
                'message': 'Essay regeneration started',
                'websocket_url': f'/ws/essays/{new_generation.id}/',
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history for an essay."""
        generation = self.get_object()
        versions = generation.versions.all()
        serializer = EssayVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel ongoing generation."""
        generation = self.get_object()

        if generation.status not in ['pending', 'profile', 'rag', 'research', 'brainstorm', 'outline', 'draft', 'critique']:
            return Response(
                {'error': 'Cannot cancel - generation is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )

        generation.status = 'cancelled'
        generation.save()

        return Response({'status': 'cancelled', 'message': 'Generation cancelled'})
