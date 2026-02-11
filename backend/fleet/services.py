#fleet/services.py
from django.db.models import Q, Case, When, IntegerField, OuterRef, Count, F
from .models import Car
from bookings.models import Booking
from datetime import timedelta

def exclude_unavailable(queryset, start_time, end_time):
    """
    Removes cars that have at least one blocking booking
    overlapping the requested time range.
    Uses EXISTS subquery -> no joins, no duplicates, scalable.
    """
    if not start_time or not end_time:
        return queryset
    
    buffer = timedelta(hours=1)
    check_start = start_time - buffer
    check_end = end_time + buffer
    
    #subquery: find bookings that block this specific car
    queryset = queryset.annotate(
        overlapping_count=Count(
            'bookings',
            filter=Q(
                bookings__status__in=['PENDING', 'APPROVED', 'MAINTENANCE'],
                bookings__start_time__lt=check_end,
                bookings__end_time__gt=check_start
            )
        )
    )

    return queryset.filter(overlapping_count__lt=F('quantity'))

def search_cars(queryset=None, query=None, start_time=None, end_time=None, category=None, transmission=None, min_price=None, max_price=None):
    """
    Unified search + availability engine.
    Can be reused with any base queryset.
    """
    if queryset is None:
        queryset = Car.objects.all()

    # 1. Sidebar Filters (Category, Transmission, Price)
    if category and category != 'All':
        queryset = queryset.filter(category__name=category)
    
    if transmission and transmission != 'All':
        queryset = queryset.filter(transmission=transmission)
        
    if min_price:
        queryset = queryset.filter(daily_rate__gte=min_price)
        
    if max_price:
        queryset = queryset.filter(daily_rate__lte=max_price)    

    # 1. Cheap text filter first
    if query:
        queryset = queryset.filter(
            Q(brand__icontains=query) |
            Q(name__icontains=query)
        ).annotate(
            match_priority=Case(
                When(brand__istartswith=query, then=0),
                When(name__istartswith=query, then=1),
                default=2,
                output_field=IntegerField(),
            )
        ).order_by('match_priority', 'brand', 'name')

    # 2. Expensive availability filter after
    if start_time and end_time:
        queryset = exclude_unavailable(queryset, start_time, end_time)

    return queryset