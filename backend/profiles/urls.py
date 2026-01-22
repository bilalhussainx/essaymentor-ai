"""
URL patterns for profiles app.
"""

from django.urls import path
from .views import StudentProfileView, StudentProfileCreateView

urlpatterns = [
    path('me/', StudentProfileView.as_view(), name='profile-me'),
    path('', StudentProfileCreateView.as_view(), name='profile-create'),
]
