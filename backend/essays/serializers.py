"""
Serializers for Essay generation models.
"""

from rest_framework import serializers
from .models import University, EssayGeneration, EssayVersion, ChatMessage
from profiles.serializers import StudentProfileSerializer


class UniversitySerializer(serializers.ModelSerializer):
    """Serializer for University model."""

    class Meta:
        model = University
        fields = ['code', 'name', 'location', 'values', 'culture', 'essay_preferences', 'prompts']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""

    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'agent_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class EssayVersionSerializer(serializers.ModelSerializer):
    """Serializer for essay versions."""

    class Meta:
        model = EssayVersion
        fields = ['id', 'version_number', 'content', 'changes_description', 'created_at']
        read_only_fields = ['id', 'created_at']


class EssayGenerationSerializer(serializers.ModelSerializer):
    """Full serializer for EssayGeneration with all details."""
    profile = StudentProfileSerializer(read_only=True)
    target_university = UniversitySerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    versions = EssayVersionSerializer(many=True, read_only=True)

    class Meta:
        model = EssayGeneration
        fields = [
            'id', 'user', 'profile', 'prompt', 'target_university',
            'essay_type', 'word_count_target', 'status', 'current_agent',
            'progress_percent', 'profile_analysis', 'rag_context',
            'prompt_analysis', 'ideas', 'essay_outline', 'essay_draft',
            'critique', 'final_essay', 'word_count_actual',
            'generation_time_seconds', 'error_message',
            'messages', 'versions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'current_agent', 'progress_percent',
            'profile_analysis', 'rag_context', 'prompt_analysis', 'ideas',
            'essay_outline', 'essay_draft', 'critique', 'final_essay',
            'word_count_actual', 'generation_time_seconds', 'error_message',
            'created_at', 'updated_at'
        ]


class EssayGenerationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing essays."""
    target_university_code = serializers.CharField(
        source='target_university.code',
        read_only=True
    )
    target_university_name = serializers.CharField(
        source='target_university.name',
        read_only=True
    )

    class Meta:
        model = EssayGeneration
        fields = [
            'id', 'prompt', 'target_university_code', 'target_university_name',
            'essay_type', 'status', 'progress_percent', 'word_count_actual',
            'created_at'
        ]


class EssayGenerationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new essay generation."""
    target_university_code = serializers.CharField(write_only=True)

    class Meta:
        model = EssayGeneration
        fields = [
            'prompt', 'target_university_code', 'essay_type', 'word_count_target'
        ]

    def validate_target_university_code(self, value):
        try:
            University.objects.get(code=value)
        except University.DoesNotExist:
            raise serializers.ValidationError(f"University '{value}' not found.")
        return value

    def create(self, validated_data):
        university_code = validated_data.pop('target_university_code')
        university = University.objects.get(code=university_code)

        user = self.context['request'].user

        # Get user's student profile
        profile = getattr(user, 'student_profile', None)

        generation = EssayGeneration.objects.create(
            user=user,
            profile=profile,
            target_university=university,
            **validated_data
        )

        return generation


class EssayStatusSerializer(serializers.ModelSerializer):
    """Lightweight serializer for status polling."""

    class Meta:
        model = EssayGeneration
        fields = ['id', 'status', 'current_agent', 'progress_percent', 'error_message']
