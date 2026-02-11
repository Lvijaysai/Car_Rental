#notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from .models import Notification


@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    """Create notifications when booking status changes"""
    if not created:
        # Booking was updated - check status change
        old_status = None
        if instance.pk:
            try:
                old_instance = Booking.objects.get(pk=instance.pk)
                old_status = old_instance.status
            except Booking.DoesNotExist:
                pass
        
        # Only create notification if status actually changed
        if old_status != instance.status:
            if instance.status == 'APPROVED':
                Notification.objects.create(
                    user=instance.user,
                    notification_type='BOOKING_APPROVED',
                    title='Booking Approved',
                    message=f'Your booking for {instance.car.brand} {instance.car.name} has been approved!',
                    booking=instance
                )
            elif instance.status == 'CANCELLED':
                Notification.objects.create(
                    user=instance.user,
                    notification_type='BOOKING_CANCELLED',
                    title='Booking Cancelled',
                    message=f'Your booking for {instance.car.brand} {instance.car.name} has been cancelled.',
                    booking=instance
                )
            elif instance.status == 'COMPLETED':
                Notification.objects.create(
                    user=instance.user,
                    notification_type='BOOKING_COMPLETED',
                    title='Rental Completed',
                    message=f'Your rental of {instance.car.brand} {instance.car.name} has been completed.',
                    booking=instance
                )
