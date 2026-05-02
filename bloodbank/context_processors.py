from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        recent_notifications = request.user.notifications.all()[:5]
        return {
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
