#fleet/serializers.py
from rest_framework import serializers
from .models import Car, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class CarSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    
    # Computed fields for availability
    is_available = serializers.SerializerMethodField()
    live_status = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    next_available_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = [
            'id', 'name', 'brand', 'slug', 'category', 'category_id',
            'quantity', 'cleaning_time', 'transmission', 'seats', 'doors',
            'fuel_type', 'daily_rate', 'twelve_hour_rate', 'status',
            'image', 'is_featured', 'features', 'created_at',
            'is_available', 'live_status', 'status_color', 'next_available_date'
        ]
        read_only_fields = ['slug', 'created_at']
    
    def get_is_available(self, obj):
        """Check if car is available right now"""
        from django.utils import timezone
        from bookings.models import Booking
        
        if obj.status == 'MAINTENANCE':
            return False
        
        now = timezone.now()
        active_count = obj.bookings.filter(
            status__in=['PENDING', 'APPROVED'],
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        return active_count < obj.quantity
    
    def get_live_status(self, obj):
        """Get current status message"""
        from django.utils import timezone
        from bookings.models import Booking
        
        if obj.status == 'MAINTENANCE':
            return 'Under Maintenance'
        elif obj.status == 'RENTED':
            return 'Sold Out'
        
        now = timezone.now()
        active_count = obj.bookings.filter(
            status__in=['PENDING', 'APPROVED'],
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        if active_count >= obj.quantity:
            return 'Sold Out'
        elif active_count > 0:
            remaining = obj.quantity - active_count
            return f'{remaining} Left'
        
        return 'Available'
    
    def get_status_color(self, obj):
        """Get Bootstrap color class for status"""
        if obj.status == 'MAINTENANCE':
            return 'danger'
        elif obj.status == 'RENTED':
            return 'secondary'
        
        from django.utils import timezone
        from bookings.models import Booking
        
        now = timezone.now()
        active_count = obj.bookings.filter(
            status__in=['PENDING', 'APPROVED'],
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        if active_count >= obj.quantity:
            return 'secondary'
        elif active_count > 0:
            return 'warning'
        
        return 'success'
    
    def get_next_available_date(self, obj):
        """Get next available date if fully booked"""
        from django.utils import timezone
        from bookings.models import Booking
        
        now = timezone.now()
        active_count = obj.bookings.filter(
            status__in=['PENDING', 'APPROVED'],
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        if active_count >= obj.quantity:
            # Find the next booking end time
            next_booking = obj.bookings.filter(
                status__in=['PENDING', 'APPROVED'],
                end_time__gt=now
            ).order_by('end_time').first()
            
            if next_booking:
                return next_booking.end_time.date()
        
        return None


class CarListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for car listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Car
        fields = [
            'id', 'name', 'brand', 'slug', 'category_name',
            'daily_rate', 'twelve_hour_rate', 'transmission',
            'fuel_type', 'seats', 'image', 'status'
        ]
