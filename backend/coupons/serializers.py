#backend/coupons/serializers.py
from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percentage']
        
class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)