#backend/bookings/admin.py
from django.contrib import admin
from django.contrib import messages
from .models import Booking, ActiveBooking, BookingHistory

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_time', 'end_time', 'status', 'total_price']
    list_filter = ['status', 'created_at', 'car']
    search_fields = ['user__username', 'car__brand', 'car__name']
    readonly_fields = ['total_price', 'created_at']
    
    # Register custom actions
    actions = ['approve_bookings', 'cancel_bookings', 'mark_completed']

    @admin.action(description="Approve selected bookings")
    def approve_bookings(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, f"{updated} booking(s) successfully approved.", messages.SUCCESS)

    @admin.action(description="Cancel selected bookings")
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f"{updated} booking(s) successfully cancelled.", messages.WARNING)

    @admin.action(description="Mark selected as Completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f"{updated} booking(s) marked as completed.", messages.SUCCESS)

# Registering the Proxy Models for cleaner admin separation
@admin.register(ActiveBooking)
class ActiveBookingAdmin(BookingAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status__in=['PENDING', 'APPROVED', 'MAINTENANCE'])

@admin.register(BookingHistory)
class BookingHistoryAdmin(BookingAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status__in=['COMPLETED', 'CANCELLED'])
