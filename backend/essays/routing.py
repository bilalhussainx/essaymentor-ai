"""
WebSocket URL routing for essays app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/essays/(?P<generation_id>[0-9a-f-]+)/$',
        consumers.EssayGenerationConsumer.as_asgi()
    ),
]
