#bookings/services.py
"""
Fixed version of booking services with bug fixes
"""
from datetime import timedelta
from django.utils import timezone
from .models import Booking

# Statuses that consume a car slot
BLOCKING_STATUSES = ['PENDING', 'APPROVED', 'MAINTENANCE']


def is_car_available(car, start_time, end_time):
    """
    Single source of truth for car availability.
    Includes mandatory validation and row-level locking.
    
    BUG FIXES:
    1. Fixed buffer calculation to use car.cleaning_time properly
    2. Fixed overlap detection logic
    3. Added proper quantity check
    """
    # 1. Mandatory business logic validation
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")
    
    # 2. Dynamic buffer calculation (reads from admin settings)
    # If cleaning_time is not set, default to 1 hour
    buffer_hours = getattr(car, 'cleaning_time', 1)
    buffer = timedelta(hours=buffer_hours)
    buffered_start = start_time - buffer
    buffered_end = end_time + buffer

    # 3. Lock overlapping booking rows
    # This prevents race conditions where capacity is changing while we count
    # FIXED: Proper overlap detection - bookings overlap if:
    # - booking.start_time < buffered_end AND booking.end_time > buffered_start
    active_count = (
        Booking.objects
        .select_for_update()
        .filter(
            car=car,
            status__in=BLOCKING_STATUSES,
            start_time__lt=buffered_end,  # Booking starts before our buffered end
            end_time__gt=buffered_start   # Booking ends after our buffered start
        )
        .count()
    )
    
    # FIXED: Check if we have enough available cars
    return active_count < car.quantity
