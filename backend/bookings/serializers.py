#bookings/serializers.py
from rest_framework import serializers
from .models import Booking
from fleet.serializers import CarSerializer
from fleet.models import Car  # <--- 1. Import Car model here

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
            'total_price', 'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'created_at']
    
    def validate(self, data):
        """Validate booking times"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
            
            from django.utils import timezone
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
    
    def validate(self, data):
        booking_type = data.get('booking_type')
        
        if booking_type == 'hourly':
            if not data.get('hourly_start') or not data.get('hourly_end'):
                raise serializers.ValidationError(
                    'Please provide both hourly_start and hourly_end for hourly bookings.'
                )
            
            start = data['hourly_start']
            end = data['hourly_end']
            
            # Check minimum 12 hours
            duration_hours = (end - start).total_seconds() / 3600
            if duration_hours < 12:
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
        
        return data
    
    def create(self, validated_data):
        """Create booking from validated data"""
        from django.utils import timezone
        from datetime import datetime, time
        from fleet.models import Car
        
        booking_type = validated_data['booking_type']
        car = Car.objects.get(slug=validated_data['car_slug'])
        
        if booking_type == 'hourly':
            start_time = timezone.make_aware(validated_data['hourly_start'])
            end_time = timezone.make_aware(validated_data['hourly_end'])
        else:  # daily
            start_date = validated_data['daily_start']
            end_date = validated_data['daily_end']
            now_local = timezone.localtime(timezone.now())
            
            if start_date == now_local.date():
                start_dt = datetime.combine(start_date, now_local.time())
            else:
                start_dt = datetime.combine(start_date, time(9, 0, 0))
            
            end_dt = datetime.combine(end_date, start_dt.time())
            start_time = timezone.make_aware(start_dt)
            end_time = timezone.make_aware(end_dt)
        
        booking = Booking.objects.create(
            user=self.context['request'].user,
            car=car,
            start_time=start_time,
            end_time=end_time,
            status='PENDING'
        )
        
        return booking