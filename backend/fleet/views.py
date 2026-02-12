
#fleet/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from datetime import datetime, time
from .models import Car, Category
from .serializers import CarSerializer, CarListSerializer, CategorySerializer
from .services import search_cars


def parse_flexible_date(date_str, is_end=False):
    """
    Accepts: YYYY-MM-DD or YYYY-MM-DDTHH:MM
    Returns timezone-aware datetime or None.
    """
    if not date_str:
        return None
    
    dt = parse_datetime(date_str)
    if dt:
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    
    d = parse_date(date_str)
    if d:
        t = time.max if is_end else time.min
        dt = datetime.combine(d, t)
        return timezone.make_aware(dt)
    return None


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing car categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and searching cars
    """
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return CarListSerializer
        return CarSerializer
    
    def get_queryset(self):
        """Apply search and filters"""
        queryset = Car.objects.all()
        
        # Get query parameters
        query = self.request.query_params.get('q', '').strip()
        start_str = self.request.query_params.get('start')
        end_str = self.request.query_params.get('end')
        category = self.request.query_params.get('category')
        transmission = self.request.query_params.get('transmission')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        # Parse dates
        start_time = parse_flexible_date(start_str, is_end=False)
        end_time = parse_flexible_date(end_str, is_end=True)
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError({"detail": "End time must be after start time"})
            
        
        # Apply search and filters using service
        queryset = search_cars(
            queryset=queryset,
            query=query,
            start_time=start_time,
            end_time=end_time,
            category=category,
            transmission=transmission,
            min_price=min_price,
            max_price=max_price
        )
        
        # Optimize queries
        queryset = queryset.prefetch_related('bookings', 'category')
        
        # Calculate live status for each car
        now = timezone.now()
        for car in queryset:
            car.is_available = True
            car.live_status = 'Available'
            car.status_color = 'success'
            
            # Check admin override
            if car.status == 'MAINTENANCE':
                car.is_available = False
                car.live_status = 'Under Maintenance'
                car.status_color = 'danger'
                continue
            elif car.status == 'RENTED':
                car.is_available = False
                car.live_status = 'Sold Out'
                car.status_color = 'secondary'
                continue
            
            # Check real-time availability if no date filter
            if not (start_time and end_time):
                active_now_count = car.bookings.filter(
                    status__in=['PENDING', 'APPROVED'],
                    start_time__lte=now,
                    end_time__gte=now
                ).count()
                
                if active_now_count >= car.quantity:
                    car.is_available = False
                    car.live_status = 'Sold Out'
                    car.status_color = 'secondary'
                elif active_now_count > 0:
                    remaining = car.quantity - active_now_count
                    car.live_status = f'{remaining} Left'
                    car.status_color = 'warning'
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='search')
    def search_autosuggest(self, request):
        """Autosuggest endpoint for search"""
        query = request.query_params.get('term', '').strip()
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        
        start_time = parse_flexible_date(start_str, is_end=False)
        end_time = parse_flexible_date(end_str, is_end=True)
        
        if start_time and end_time and start_time >= end_time:
            start_time = None
            end_time = None
        
        cars = search_cars(
            query=query,
            start_time=start_time,
            end_time=end_time
        )[:5]
        
        results = []
        for car in cars:
            results.append({
                'id': car.id,
                'label': f"{car.brand} {car.name}",
                'url': f"/cars/{car.slug}",
                'image': car.image.url if car.image else None,
                'price': str(car.daily_rate),
            })
        
        return Response(results)
