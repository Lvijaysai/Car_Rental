#users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/logout/', views.logout, name='logout'),
    path('api/current-user/', views.current_user, name='current_user'),
]
