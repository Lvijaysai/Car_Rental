#bookings/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from fleet.serializers import CarSerializer
from fleet.models import Car
from coupons.models import Coupon
from datetime import timedelta

def ensure_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


class BookingSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(),  # <--- 2. Set queryset directly (Fixes AssertionError)
        source='car',
        write_only=True
    )
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'car', 'car_id', 'start_time', 'end_time',
            'total_price', 'discount_amount', 'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'discount_amount', 'created_at']
    
    def validate(self, data):
        """Validate booking times"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
            
            if start_time < timezone.now():
                raise serializers.ValidationError({
                    'start_time': 'Cannot book for a past date/time.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create booking with automatic price calculation"""
        validated_data['user'] = self.context['request'].user
        booking = Booking.objects.create(**validated_data)
        return booking


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for creating bookings with validation"""
    car_slug = serializers.SlugField()
    booking_type = serializers.ChoiceField(choices=['hourly', 'daily'])
    hourly_start = serializers.DateTimeField(required=False)
    hourly_end = serializers.DateTimeField(required=False)
    daily_start = serializers.DateField(required=False)
    daily_end = serializers.DateField(required=False)
    
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        booking_type = data.get('booking_type')
        
        if booking_type == 'hourly':
            if not data.get('hourly_start') or not data.get('hourly_end'):
                raise serializers.ValidationError(
                    'Please provide both hourly_start and hourly_end for hourly bookings.'
                )
            
            start = data['hourly_start']
            end = data['hourly_end']

            grace_period = timezone.now() - timedelta(minutes=5)
            if start < grace_period:
                raise serializers.ValidationError(
                    'Cannot book for a past date/time.'
                )
            
            # FIX 2: Round duration to avoid floating-point precision failures (e.g., 11.999 hours)
            duration_hours = round((end - start).total_seconds() / 3600, 2)
            if duration_hours < 12.00:
                raise serializers.ValidationError(
                    'Minimum booking duration is 12 hours for hourly bookings.'
                )
        
        elif booking_type == 'daily':
            if not data.get('daily_start') or not data.get('daily_end'):
                raise serializers.ValidationError(
                    'Please provide both daily_start and daily_end for daily bookings.'
                )
            
            if data['daily_end'] <= data['daily_start']:
                raise serializers.ValidationError(
                    'End date must be after start date.'
                )
        coupon_code = data.get('coupon_code')
        if coupon_code:
            now = timezone.now()
            exists = Coupon.objects.filter(
                code__iexact=coupon_code,
                active=True,
                valid_from__lte=now,
                valid_to__gte=now
            ).exists()
            
            if not exists:
                raise serializers.ValidationError({
                    'coupon_code': 'Invalid or expired coupon code.'
                })
            
        return data
    
    def create(self, validated_data):
        """Create booking from validated data"""
        from datetime import datetime, time
        from fleet.models import Car
        
        booking_type = validated_data['booking_type']
        car = Car.objects.get(slug=validated_data['car_slug'])
        
        coupon_code = validated_data.get('coupon_code')
        coupon = None
        if coupon_code:
            coupon = Coupon.objects.filter(code__iexact=coupon_code).first()

        if booking_type == 'hourly':
            start_time = ensure_aware(validated_data['hourly_start'])
            end_time = ensure_aware(validated_data['hourly_end'])
        else:  # daily
            start_date = validated_data['daily_start']
            end_date = validated_data['daily_end']
            now_local = timezone.localtime(timezone.now())
            
            if start_date == now_local.date():
                start_dt = datetime.combine(start_date, now_local.time())
            else:
                start_dt = datetime.combine(start_date, time(9, 0, 0))
            
            end_dt = datetime.combine(end_date, start_dt.time())
            start_time = ensure_aware(start_dt)
            end_time = ensure_aware(end_dt)
        
        booking = Booking.objects.create(
            user=self.context['request'].user,
            car=car,
            start_time=start_time,
            end_time=end_time,
            status='PENDING',
            coupon=coupon
        )
        
        return booking
