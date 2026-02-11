#core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('api/dashboard/', views.dashboard, name='dashboard'),
    path('api/history/', views.booking_history, name='history'),
]
