"""
URL patterns for essays app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EssayGenerationViewSet, UniversityViewSet

router = DefaultRouter()
router.register('', EssayGenerationViewSet, basename='essay')
router.register('universities', UniversityViewSet, basename='university')

urlpatterns = [
    path('', include(router.urls)),
]
