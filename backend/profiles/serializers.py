"""
Serializers for User and StudentProfile models.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'name', 'age', 'background', 'identity', 'location',
            'family_context', 'socioeconomic', 'languages',
            'major_experiences', 'activities', 'achievements',
            'interests', 'gpa', 'sat_verbal', 'intellectual_profile',
            'voice_characteristics', 'vocabulary_level', 'writing_style',
            'consistent_details', 'experiences_used',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating StudentProfile."""

    class Meta:
        model = StudentProfile
        fields = [
            'name', 'age', 'background', 'identity', 'location',
            'family_context', 'socioeconomic', 'languages',
            'major_experiences', 'activities', 'achievements',
            'interests', 'gpa', 'sat_verbal', 'intellectual_profile',
            'voice_characteristics', 'vocabulary_level', 'writing_style',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        # Check if profile already exists
        profile, created = StudentProfile.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return profile
