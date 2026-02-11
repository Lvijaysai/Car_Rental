##notifications/models.py
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification model for user alerts"""
    NOTIFICATION_TYPES = [
        ('BOOKING_APPROVED', 'Booking Approved'),
        ('BOOKING_CANCELLED', 'Booking Cancelled'),
        ('BOOKING_COMPLETED', 'Booking Completed'),
        ('RENTAL_STARTED', 'Rental Started'),
        ('RENTAL_ENDING', 'Rental Ending Soon'),
        ('PAYMENT_REQUIRED', 'Payment Required'),
        ('SYSTEM', 'System Notification'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='SYSTEM'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Link to related booking
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
