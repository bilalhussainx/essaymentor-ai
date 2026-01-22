"""
Celery configuration for EssayMentor AI backend.

Handles async essay generation tasks.
Each essay generation runs as a Celery task to avoid blocking the API.
"""

import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'essaymentor.settings')

# Create Celery app
app = Celery('essaymentor')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery connection."""
    print(f'Request: {self.request!r}')
