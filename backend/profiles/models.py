"""
User and StudentProfile models.

StudentProfile mirrors the structure in agents/state.py to ensure
compatibility with the existing multi-agent system.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model with email as the primary identifier.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    """
    Student profile for essay personalization.
    Structure mirrors agents/state.py StudentProfile TypedDict.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    # Identity
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    background = models.TextField(blank=True, help_text="Student's background story")
    identity = models.TextField(blank=True, help_text="Cultural/personal identity")
    location = models.CharField(max_length=255, blank=True)

    # Family context
    family_context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Family information as key-value pairs"
    )
    socioeconomic = models.CharField(max_length=100, blank=True)
    languages = models.JSONField(
        default=list,
        blank=True,
        help_text="List of languages spoken"
    )

    # Experiences (list of dicts with title, duration, description, skills_developed, impact)
    major_experiences = models.JSONField(
        default=list,
        blank=True,
        help_text="Major experiences/activities"
    )
    activities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of extracurricular activities"
    )
    achievements = models.JSONField(
        default=list,
        blank=True,
        help_text="List of achievements/awards"
    )

    # Academic
    interests = models.JSONField(
        default=dict,
        blank=True,
        help_text="Academic and personal interests"
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    sat_verbal = models.IntegerField(null=True, blank=True)
    intellectual_profile = models.TextField(
        blank=True,
        help_text="Description of intellectual interests and approach"
    )

    # Writing characteristics
    voice_characteristics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Writing style, tone, perspective, etc."
    )
    vocabulary_level = models.CharField(max_length=50, blank=True)
    writing_style = models.CharField(max_length=100, blank=True)

    # Consistency tracking (for multi-essay suites)
    consistent_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details that should remain consistent across essays"
    )
    experiences_used = models.JSONField(
        default=dict,
        blank=True,
        help_text="Track which experiences have been used in which essays"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def to_agent_dict(self) -> dict:
        """
        Convert to dictionary format expected by agents/state.py.
        This ensures compatibility with the existing multi-agent system.
        """
        return {
            'student_id': str(self.id),
            'name': self.name,
            'age': self.age,
            'background': self.background,
            'identity': self.identity,
            'location': self.location,
            'family': self.family_context,
            'socioeconomic': self.socioeconomic,
            'languages': self.languages,
            'major_experiences': self.major_experiences,
            'activities': self.activities,
            'achievements': self.achievements,
            'interests': self.interests,
            'gpa': float(self.gpa) if self.gpa else None,
            'sat_verbal': self.sat_verbal,
            'intellectual_profile': self.intellectual_profile,
            'voice_characteristics': self.voice_characteristics,
            'vocabulary_level': self.vocabulary_level,
            'writing_style': self.writing_style,
            'consistent_details': self.consistent_details,
            'experiences_used': self.experiences_used,
        }

    @classmethod
    def from_agent_dict(cls, data: dict, user: User) -> 'StudentProfile':
        """
        Create a StudentProfile from agent dict format.
        Useful for importing profiles from data/essay_suites/.
        """
        return cls(
            user=user,
            name=data.get('name', ''),
            age=data.get('age'),
            background=data.get('background', ''),
            identity=data.get('identity', ''),
            location=data.get('location', ''),
            family_context=data.get('family', {}),
            socioeconomic=data.get('socioeconomic', ''),
            languages=data.get('languages', []),
            major_experiences=data.get('major_experiences', []),
            activities=data.get('activities', []),
            achievements=data.get('achievements', []),
            interests=data.get('interests', {}),
            gpa=data.get('gpa'),
            sat_verbal=data.get('sat_verbal'),
            intellectual_profile=data.get('intellectual_profile', ''),
            voice_characteristics=data.get('voice_characteristics', {}),
            vocabulary_level=data.get('vocabulary_level', ''),
            writing_style=data.get('writing_style', ''),
            consistent_details=data.get('consistent_details', {}),
            experiences_used=data.get('experiences_used', {}),
        )
