from admin_panel.models import Notification


def unseen_notifications_count(request):
    if request.user.is_superuser:
        count = Notification.objects.filter(is_seen=False).count()
    else:
        count = 0
    return {'unseen_notifications_count': count}
