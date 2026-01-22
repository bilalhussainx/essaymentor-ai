"""
Celery tasks for essay generation.

Runs the 7-agent workflow asynchronously and streams progress via WebSocket.
"""

import os
import sys
import time
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

# Add project root to path to import agents
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# Agent configuration
AGENT_ORDER = ['profile', 'rag', 'research', 'brainstorm', 'outline', 'draft', 'critique']
AGENT_PROGRESS = {
    'profile': (0, 14, 'Analyzing student profile...'),
    'rag': (14, 28, 'Retrieving similar essays...'),
    'research': (28, 42, 'Researching essay prompt...'),
    'brainstorm': (42, 56, 'Brainstorming ideas...'),
    'outline': (56, 70, 'Creating outline...'),
    'draft': (70, 85, 'Writing essay draft...'),
    'critique': (85, 100, 'Critiquing essay...'),
}


def broadcast_to_websocket(generation_id: str, event_type: str, data: dict):
    """Send update to WebSocket clients watching this generation."""
    channel_layer = get_channel_layer()
    room_group_name = f'essay_{generation_id}'

    # Convert event_type to channel layer format (agent_start -> agent.start)
    channel_event_type = event_type.replace('_', '.')

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': channel_event_type,
            **data
        }
    )


@shared_task(bind=True, max_retries=3)
def generate_essay_task(self, generation_id: str):
    """
    Main Celery task that runs the 7-agent workflow.

    Broadcasts progress to WebSocket after each agent completes.
    """
    from essays.models import EssayGeneration, ChatMessage

    generation = EssayGeneration.objects.get(id=generation_id)
    start_time = time.time()

    try:
        # Import the workflow runner
        from agents.workflow import run_essay_generation

        # Build initial state from database
        profile = generation.profile
        student_profile = profile.to_agent_dict() if profile else {
            'name': generation.user.username,
            'background': '',
        }

        university_code = generation.target_university.code if generation.target_university else 'Generic'

        # Run each agent and broadcast progress
        for agent_name in AGENT_ORDER:
            # Check if cancelled
            generation.refresh_from_db()
            if generation.status == 'cancelled':
                return {'status': 'cancelled'}

            # Update status
            start_progress, end_progress, message = AGENT_PROGRESS[agent_name]
            generation.status = agent_name
            generation.current_agent = agent_name
            generation.progress_percent = start_progress
            generation.save()

            # Broadcast agent start
            broadcast_to_websocket(generation_id, 'agent_start', {
                'agent': agent_name,
                'message': message,
                'progress': start_progress,
            })

            # Add chat message
            ChatMessage.objects.create(
                generation=generation,
                role='system',
                content=message,
                agent_name=agent_name
            )

        # Run the complete workflow
        result = run_essay_generation(
            prompt=generation.prompt,
            student_profile=student_profile,
            target_university=university_code,
            essay_type=generation.essay_type,
            word_count=generation.word_count_target,
            other_essays=[]
        )

        # Store results
        generation.profile_analysis = result.get('profile_analysis', '')
        generation.selected_experiences = result.get('selected_experiences', '')
        generation.university_alignment = result.get('university_alignment', '')
        generation.rag_context = result.get('rag_context', '')
        generation.retrieved_essays = result.get('retrieved_essays', [])
        generation.prompt_analysis = result.get('prompt_analysis', '')
        generation.ideas = result.get('ideas', '')
        generation.essay_outline = result.get('essay_outline', '')
        generation.essay_draft = result.get('essay_draft', '')
        generation.critique = result.get('critique', '')
        generation.final_essay = result.get('final_essay', result.get('essay_draft', ''))

        # Calculate word count
        if generation.final_essay:
            generation.word_count_actual = len(generation.final_essay.split())

        generation.status = 'completed'
        generation.progress_percent = 100
        generation.generation_time_seconds = time.time() - start_time
        generation.save()

        # Broadcast completion
        broadcast_to_websocket(generation_id, 'generation_complete', {
            'final_essay': generation.final_essay,
            'critique': generation.critique,
            'word_count': generation.word_count_actual,
        })

        # Add final chat message
        ChatMessage.objects.create(
            generation=generation,
            role='assistant',
            content=generation.final_essay,
            agent_name='draft'
        )

        return {
            'status': 'completed',
            'generation_id': generation_id,
            'word_count': generation.word_count_actual,
            'time_seconds': generation.generation_time_seconds,
        }

    except Exception as e:
        generation.status = 'failed'
        generation.error_message = str(e)
        generation.save()

        # Broadcast error
        broadcast_to_websocket(generation_id, 'generation_error', {
            'message': str(e),
            'agent': generation.current_agent,
        })

        raise


@shared_task
def cleanup_old_generations():
    """
    Periodic task to clean up old failed/cancelled generations.
    Runs daily via Celery Beat.
    """
    from essays.models import EssayGeneration
    from django.utils import timezone
    from datetime import timedelta

    # Delete failed/cancelled generations older than 7 days
    cutoff = timezone.now() - timedelta(days=7)
    deleted, _ = EssayGeneration.objects.filter(
        status__in=['failed', 'cancelled'],
        created_at__lt=cutoff
    ).delete()

    return {'deleted': deleted}
