"""
URL configuration for EssayMentor AI backend.

API Endpoints:
- /api/auth/        - Authentication (login, register, refresh)
- /api/profiles/    - User profiles
- /api/essays/      - Essay generation
- /api/universities/- University data
- /api/vectordb/    - Vector database search
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('profiles.urls_auth')),

    # API endpoints
    path('api/profiles/', include('profiles.urls')),
    path('api/essays/', include('essays.urls')),
    path('api/vectordb/', include('vectordb.urls')),

    # Health check
    path('health/', lambda request: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]
