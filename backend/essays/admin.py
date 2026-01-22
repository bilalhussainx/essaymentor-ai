"""
Admin configuration for essays app.
"""

from django.contrib import admin
from .models import University, EssayGeneration, EssayVersion, ChatMessage


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location']
    search_fields = ['code', 'name']


@admin.register(EssayGeneration)
class EssayGenerationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target_university', 'status', 'progress_percent', 'created_at']
    list_filter = ['status', 'target_university', 'essay_type']
    search_fields = ['user__email', 'prompt']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EssayVersion)
class EssayVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'generation', 'version_number', 'created_at']
    list_filter = ['created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'generation', 'role', 'agent_name', 'created_at']
    list_filter = ['role', 'agent_name']
