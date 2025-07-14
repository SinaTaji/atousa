from django.core.cache import cache

from account.models import WishList
from .models import ReplyContact
from account.utils import is_partner


def wishlist_count(request):
    if request.user.is_authenticated:
        count = WishList.objects.filter(user=request.user).count()
        cache.set('wishlist_count', count, 60 * 60)
    else:
        count = 0
    return {'wishlist_count': count}


def messages_count(request):
    if request.user.is_authenticated:
        count = ReplyContact.objects.filter(user=request.user, is_read=False).count()
        cache.set('messages_count', count, 60 * 60)
    else:
        count = 0
    return {'messages_count': count}


def partner(request):
    part = is_partner(request)
    return {'part': part}
