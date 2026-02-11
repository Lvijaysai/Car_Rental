from django.shortcuts import render

# Create your views here.
#bookings/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer
from .services import is_car_available
from fleet.models import Car


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return bookings for the current user"""
        queryset = Booking.objects.filter(user=self.request.user).select_related('car')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create booking with availability check"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_booking(self, request):
        """
        Create a booking with flexible input (hourly or daily)
        """
        serializer = BookingCreateSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            car_slug = serializer.validated_data['car_slug']
            booking_type = serializer.validated_data['booking_type']
            
            # Get car with lock
            with transaction.atomic():
                car = get_object_or_404(
                    Car.objects.select_for_update(),
                    slug=car_slug
                )
                
                # Determine start and end times
                if booking_type == 'hourly':
                    start_time = timezone.make_aware(serializer.validated_data['hourly_start'])
                    end_time = timezone.make_aware(serializer.validated_data['hourly_end'])
                else:  # daily
                    from datetime import datetime, time
                    start_date = serializer.validated_data['daily_start']
                    end_date = serializer.validated_data['daily_end']
                    now_local = timezone.localtime(timezone.now())
                    
                    if start_date == now_local.date():
                        start_dt = datetime.combine(start_date, now_local.time())
                    else:
                        start_dt = datetime.combine(start_date, time(9, 0, 0))
                    
                    end_dt = datetime.combine(end_date, start_dt.time())
                    start_time = timezone.make_aware(start_dt)
                    end_time = timezone.make_aware(end_dt)
                
                # Check availability
                if not is_car_available(car, start_time, end_time):
                    return Response(
                        {'error': 'This car is not available for the selected time period.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create booking
                booking = Booking.objects.create(
                    user=request.user,
                    car=car,
                    start_time=start_time,
                    end_time=end_time,
                    status='PENDING'
                )
            
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        
        except Car.DoesNotExist:
            return Response(
                {'error': 'Car not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        if booking.status == 'APPROVED' and booking.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot cancel a trip that has already started.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status in ['PENDING', 'APPROVED']:
            booking.status = 'CANCELLED'
            booking.save()
            return Response({
                'message': 'Booking cancelled successfully.',
                'booking': BookingSerializer(booking).data
            })
        
        return Response(
            {'error': 'This booking cannot be cancelled.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], url_path='active')
    def active_bookings(self, request):
        """Get active bookings (PENDING, APPROVED)"""
        bookings = self.get_queryset().filter(
            status__in=['PENDING', 'APPROVED']
        ).order_by('start_time')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='history')
    def booking_history(self, request):
        """Get booking history (COMPLETED, CANCELLED)"""
        bookings = self.get_queryset().filter(
            status__in=['COMPLETED', 'CANCELLED']
        ).order_by('-created_at')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
