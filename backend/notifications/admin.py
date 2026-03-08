
# Register your models here.
#notifications/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification


class NotificationAdminForm(forms.ModelForm):
    send_to_all = forms.BooleanField(
        required=False,
        label="Send to all active users",
        help_text="If checked, this notification will be created for every active user."
    )

    class Meta:
        model = Notification
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('send_to_all') and not cleaned_data.get('user'):
            self.add_error('user', 'Select a user or enable "Send to all active users".')
        return cleaned_data


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'booking')

    def save_model(self, request, obj, form, change):
        send_to_all = form.cleaned_data.get('send_to_all', False)
        if change or not send_to_all:
            return super().save_model(request, obj, form, change)

        User = get_user_model()
        users = list(User.objects.filter(is_active=True).values_list('id', flat=True))
        if not users:
            return

        # Save one object so Django admin add flow remains consistent.
        obj.user_id = users[0]
        super().save_model(request, obj, form, change)

        remaining_user_ids = users[1:]
        if not remaining_user_ids:
            return

        now = timezone.now()
        payload = [
            Notification(
                user_id=user_id,
                notification_type=obj.notification_type,
                title=obj.title,
                message=obj.message,
                is_read=obj.is_read,
                booking=obj.booking,
                created_at=now,
            )
            for user_id in remaining_user_ids
        ]
        Notification.objects.bulk_create(payload, batch_size=1000)
