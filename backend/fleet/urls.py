#fleet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'cars', views.CarViewSet, basename='car')

app_name = 'fleet'

urlpatterns = [
    path('api/', include(router.urls)),
]
