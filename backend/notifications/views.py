
#notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user"""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark notifications as read"""
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset().filter(is_read=False)
        
        if serializer.validated_data.get('mark_all'):
            updated = queryset.update(is_read=True)
            return Response({
                'message': f'{updated} notifications marked as read.',
                'updated_count': updated
            })
        else:
            notification_ids = serializer.validated_data.get('notification_ids', [])
            if notification_ids:
                updated = queryset.filter(id__in=notification_ids).update(is_read=True)
                return Response({
                    'message': f'{updated} notifications marked as read.',
                    'updated_count': updated
                })
        
        return Response({
            'message': 'No notifications to mark as read.',
            'updated_count': 0
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_single_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.mark_as_read()
        return Response({
            'message': 'Notification marked as read.',
            'notification': NotificationSerializer(notification).data
        })
