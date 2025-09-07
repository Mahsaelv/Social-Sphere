from django.utils import timezone
from .models import Comment, Contact, Thread, Message, Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {}
    last_login = request.user.last_login or timezone.now()
    msg_count = Message.objects.filter(
        thread__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    fol_count = Contact.objects.filter(
        user_to=request.user,
        created__gt=last_login
    ).count()
    com_count = Comment.objects.filter(
        post__author=request.user,
        created__gt=last_login
    ).count()
    return {
        'notif_messages': msg_count,
        'notif_followers': fol_count,
        'notif_comments': com_count,
    }


def notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, unread=True).count()
        return {'notifications_count': count}
    return {'notifications_count': 0}


def unread_messages_count(request):
    if not request.user.is_authenticated:
        return {}
    count = Message.objects.filter(
        thread__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return {'unread_messages_count': count}
