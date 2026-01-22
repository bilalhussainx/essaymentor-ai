"""
Essay generation models.

Tracks essay generation sessions, versions, and chat messages.
"""

import uuid
from django.db import models
from django.conf import settings


class University(models.Model):
    """
    Target universities with their profiles and preferences.
    Data loaded from university_profiles.json.
    """
    code = models.CharField(max_length=50, primary_key=True)  # MIT, Harvard, etc.
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    values = models.JSONField(default=list, help_text="University values")
    culture = models.TextField(blank=True, help_text="Campus culture description")
    essay_preferences = models.JSONField(
        default=dict,
        help_text="What the university looks for in essays"
    )
    prompts = models.JSONField(
        default=dict,
        help_text="Common essay prompts"
    )

    class Meta:
        verbose_name_plural = "Universities"

    def __str__(self):
        return f"{self.code}: {self.name}"


class EssayGeneration(models.Model):
    """
    Tracks a complete essay generation session.
    Stores all agent outputs for transparency and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='essay_generations'
    )
    profile = models.ForeignKey(
        'profiles.StudentProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='essay_generations'
    )

    # Input parameters
    prompt = models.TextField(help_text="Essay prompt/question")
    target_university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    essay_type = models.CharField(
        max_length=50,
        default='common_app',
        help_text="Essay type: common_app, supplement_1, etc."
    )
    word_count_target = models.IntegerField(default=650)

    # Generation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('profile', 'Analyzing Profile'),
        ('rag', 'Retrieving Examples'),
        ('research', 'Researching Prompt'),
        ('brainstorm', 'Brainstorming'),
        ('outline', 'Creating Outline'),
        ('draft', 'Writing Draft'),
        ('critique', 'Critiquing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    current_agent = models.CharField(max_length=50, blank=True)
    progress_percent = models.IntegerField(default=0)

    # Agent outputs (stored for transparency)
    profile_analysis = models.TextField(blank=True)
    selected_experiences = models.TextField(blank=True)
    university_alignment = models.TextField(blank=True)

    # RAG results
    retrieved_essays = models.JSONField(
        default=list,
        help_text="Similar essays retrieved from vector DB"
    )
    rag_context = models.TextField(blank=True)

    # Research & brainstorm
    prompt_analysis = models.TextField(blank=True)
    ideas = models.TextField(blank=True)
    essay_approach = models.TextField(blank=True)

    # Outline & draft
    essay_outline = models.TextField(blank=True)
    essay_draft = models.TextField(blank=True)

    # Final outputs
    critique = models.TextField(blank=True)
    final_essay = models.TextField(blank=True)

    # Metadata
    word_count_actual = models.IntegerField(null=True, blank=True)
    generation_time_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        university = self.target_university.code if self.target_university else 'Generic'
        return f"Essay for {university} - {self.status}"

    def get_agent_progress(self) -> dict:
        """Get progress info for WebSocket updates."""
        agent_order = ['profile', 'rag', 'research', 'brainstorm', 'outline', 'draft', 'critique']
        current_index = agent_order.index(self.current_agent) if self.current_agent in agent_order else -1

        return {
            'status': self.status,
            'current_agent': self.current_agent,
            'progress_percent': self.progress_percent,
            'completed_agents': agent_order[:current_index] if current_index > 0 else [],
        }


class EssayVersion(models.Model):
    """
    Versioned essay edits/revisions.
    Tracks changes made to essays after initial generation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation = models.ForeignKey(
        EssayGeneration,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.IntegerField()
    content = models.TextField()
    changes_description = models.TextField(
        blank=True,
        help_text="Description of changes made in this version"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['generation', 'version_number']

    def __str__(self):
        return f"Version {self.version_number} of {self.generation.id}"


class ChatMessage(models.Model):
    """
    Chat messages for the conversation UI.
    Stores the conversation history for each generation session.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation = models.ForeignKey(
        EssayGeneration,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    agent_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Which agent sent this message"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
