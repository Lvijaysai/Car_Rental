#backend/coupons/admin.py

from django.contrib import admin
from .models import Coupon
# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'active', 'is_valid_now']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']

    @admin.display(boolean=True, description='Currently Valid')
    def is_valid_now(self, obj):
        return obj.is_valid