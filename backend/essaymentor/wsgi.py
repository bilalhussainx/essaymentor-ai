"""
WSGI config for EssayMentor AI backend.
Used by Gunicorn for HTTP requests.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'essaymentor.settings')

application = get_wsgi_application()
