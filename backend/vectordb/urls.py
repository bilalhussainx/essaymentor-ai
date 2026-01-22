"""
URL patterns for vectordb app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_essays, name='vectordb-search'),
    path('stats/', views.get_stats, name='vectordb-stats'),
]
