
from EventRecord.models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {
            'unread_notifications': notifications,
            'unread_notifications_count': notifications.count(),
        }
    else:
        return {
            'unread_notifications': [],
            'unread_notifications_count': 0,
        }
