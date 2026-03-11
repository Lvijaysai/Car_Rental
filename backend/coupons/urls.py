from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    path('api/coupons/', views.list_coupons, name='list_coupons'),
    path('api/coupons/apply/', views.apply_coupon, name='apply_coupon'),
]