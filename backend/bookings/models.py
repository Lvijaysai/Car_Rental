# bookings/models.py
"""
Fixed version of Booking model with corrected save() method
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from fleet.models import Car
import math



class Booking(models.Model):
    # Tuple defining the possible states of a booking
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),      # default state
        ('APPROVED', 'Approved'),    # admin has confirmed
        ('COMPLETED', 'Completed'),  # trip finished
        ('CANCELLED', 'Cancelled'),  # trip aborted
        ('MAINTENANCE', 'Maintenance')
    ]
    
    BLOCKING_STATUSES = [
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_MAINTENANCE,
    ]
    
    # Link to the user model (who made booking)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Link to the car model. 'related_name' allows us to do car.bookings.all()
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')

    # The actual duration of the rental 
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Store price in DB so it doesn't change if car rates change later
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Status of booking default to pending
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)  # timestamp for when booking was made
    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("End time must be after start time.")
            if not self.pk and self.start_time < timezone.now():
                raise ValidationError("Cannot book a car in the past.")
    # Override the default save method to calculate price automatically
    def save(self, *args, **kwargs):
        """
        BUG FIXES:
        1. Fixed indentation - total_price calculation was inside wrong block
        2. Fixed logic flow - only calculate if times are set
        3. Fixed multi-day calculation
        """
        self.clean()

        # Only calculate if we have both times and a car
        if self.start_time and self.end_time and self.car:
            # Calculate the difference between end and start
            diff = self.end_time - self.start_time
            # Convert that difference into total hours
            total_hours = diff.total_seconds() / 3600

            # Validation: Ensure duration is at least 1 hour
            if total_hours <= 0:
                total_hours = 1

            # 2. Apply pricing logic
            # FIXED: Proper indentation and logic flow
            if total_hours <= 12:
                # Case A: use the 12 hour price from DB
                self.total_price = self.car.twelve_hour_rate
            elif total_hours <= 24:
                # Case B: use the 24 hours price from DB
                self.total_price = self.car.daily_rate
            else:
                # Case C: multi-day 
                days = math.ceil(total_hours / 24)
                self.total_price = days * self.car.daily_rate
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.car.name}"


# Proxy model for admin panel
# 1. Active bookings manager
class ActiveBookingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['PENDING', 'APPROVED', 'MAINTENANCE'])


# 2. History manager
class HistoryBookingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['COMPLETED', 'CANCELLED'])


# 3. Active Booking Proxy
class ActiveBooking(Booking):
    objects = ActiveBookingManager()
    
    class Meta:
        proxy = True
        verbose_name = "Active Booking"
        verbose_name_plural = "Active Bookings"


# 4. History Booking Proxy
class BookingHistory(Booking):
    objects = HistoryBookingManager()
    
    class Meta:
        proxy = True
        verbose_name = "Archived Booking"
        verbose_name_plural = "Archived Bookings (Completed/Cancelled)"
