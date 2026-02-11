#backend/api_urls.py
"""
Main API URL configuration
Include this in your main urls.py
"""
from django.urls import path, include

urlpatterns = [
    path('', include('fleet.urls')),
    path('', include('bookings.urls')),
    path('', include('core.urls')),
    path('', include('users.urls')),
    path('', include('notifications.urls')),
]
