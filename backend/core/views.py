from django.shortcuts import render

# Create your views here.
# core/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bookings.models import Booking


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Get dashboard data for authenticated user
    """
    # Fetch active bookings
    active_bookings = Booking.objects.filter(
        user=request.user,
        status__in=['PENDING', 'APPROVED']
    ).select_related('car').order_by('start_time')
    
    # Count history
    history_count = Booking.objects.filter(
        user=request.user,
        status__in=['COMPLETED', 'CANCELLED']
    ).count()
    
    from bookings.serializers import BookingSerializer
    
    return Response({
        'active_bookings': BookingSerializer(active_bookings, many=True).data,
        'history_count': history_count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_history(request):
    """
    Get booking history for authenticated user
    """
    past_bookings = Booking.objects.filter(
        user=request.user,
        status__in=['COMPLETED', 'CANCELLED']
    ).select_related('car').order_by('-created_at')
    
    from bookings.serializers import BookingSerializer
    
    return Response({
        'bookings': BookingSerializer(past_bookings, many=True).data
    })
