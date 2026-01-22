"""
WebSocket consumers for real-time essay generation streaming.

Provides ChatGPT-like streaming updates as each agent processes.
"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class EssayGenerationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time essay generation updates.

    Client connects to: ws://localhost:8000/ws/essays/{generation_id}/

    Messages from server:
    {
        "type": "connected",
        "status": "pending|profile|rag|...",
        "current_agent": "profile",
        "progress": 0
    }

    {
        "type": "agent_start",
        "agent": "profile|rag|research|brainstorm|outline|draft|critique",
        "message": "Analyzing student profile...",
        "progress": 0-100
    }

    {
        "type": "agent_progress",
        "agent": "draft",
        "content": "streaming text...",
        "progress": 75
    }

    {
        "type": "agent_complete",
        "agent": "profile",
        "content": "Full agent output...",
        "progress": 14
    }

    {
        "type": "generation_complete",
        "final_essay": "...",
        "critique": "...",
        "word_count": 650
    }

    {
        "type": "error",
        "message": "Error description",
        "agent": "draft"
    }

    Messages from client:
    {
        "type": "cancel"
    }
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.generation_id = self.scope['url_route']['kwargs']['generation_id']
        self.room_group_name = f'essay_{self.generation_id}'
        self.user = self.scope.get('user')

        # Verify user has access to this generation
        if not await self.user_has_access():
            await self.close(code=4003)
            return

        # Join room group for this generation
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current status
        generation = await self.get_generation()
        if generation:
            await self.send_json({
                'type': 'connected',
                'status': generation.status,
                'current_agent': generation.current_agent,
                'progress': generation.progress_percent,
            })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        """Handle messages from client."""
        msg_type = content.get('type')

        if msg_type == 'cancel':
            await self.cancel_generation()
            await self.send_json({
                'type': 'cancelled',
                'message': 'Generation cancelled'
            })

    # Event handlers - called from Celery via channel layer

    async def agent_start(self, event):
        """Agent started processing."""
        await self.send_json({
            'type': 'agent_start',
            'agent': event['agent'],
            'message': event.get('message', f'{event["agent"]} agent started'),
            'progress': event['progress'],
        })

    async def agent_progress(self, event):
        """Streaming content from agent (like ChatGPT typing)."""
        await self.send_json({
            'type': 'agent_progress',
            'agent': event['agent'],
            'content': event['content'],
            'progress': event['progress'],
        })

    async def agent_complete(self, event):
        """Agent finished processing."""
        await self.send_json({
            'type': 'agent_complete',
            'agent': event['agent'],
            'content': event['content'],
            'progress': event['progress'],
        })

    async def generation_complete(self, event):
        """Full generation complete."""
        await self.send_json({
            'type': 'generation_complete',
            'final_essay': event['final_essay'],
            'critique': event['critique'],
            'word_count': event['word_count'],
        })

    async def generation_error(self, event):
        """Error occurred during generation."""
        await self.send_json({
            'type': 'error',
            'message': event['message'],
            'agent': event.get('agent'),
        })

    # Database helpers

    @database_sync_to_async
    def user_has_access(self):
        """Check if user has access to this generation."""
        if not self.user or not self.user.is_authenticated:
            return False

        from .models import EssayGeneration
        return EssayGeneration.objects.filter(
            id=self.generation_id,
            user=self.user
        ).exists()

    @database_sync_to_async
    def get_generation(self):
        """Get the generation object."""
        from .models import EssayGeneration
        try:
            return EssayGeneration.objects.get(id=self.generation_id)
        except EssayGeneration.DoesNotExist:
            return None

    @database_sync_to_async
    def cancel_generation(self):
        """Cancel the generation."""
        from .models import EssayGeneration
        try:
            generation = EssayGeneration.objects.get(id=self.generation_id)
            generation.status = 'cancelled'
            generation.save()
        except EssayGeneration.DoesNotExist:
            pass
