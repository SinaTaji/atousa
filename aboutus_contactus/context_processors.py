from django.core.cache import cache

from account.models import WishList
from .models import ReplyContact
from account.utils import is_partner


def get_cache_key(request, key_name):
    if request.user.is_authenticated:
        return f'{key_name}_user_{request.user.id}'
    else:
        if not request.session.session_key:
            request.session.save()  # اطمینان از داشتن session_key
        return f'{key_name}_session_{request.session.session_key}'


def wishlist_count(request):
    cache_key = get_cache_key(request, 'wishlist_count')

    count = cache.get(cache_key)
    if count is None:
        if request.user.is_authenticated:
            count = WishList.objects.filter(user=request.user).count()
        else:
            wishlist = request.session.get('wishlist', [])
            count = len(wishlist)
        cache.set(cache_key, count, 60 * 60)

    return {'wishlist_count': count}


def messages_count(request):
    user = request.user

    if not user.is_authenticated:
        return {'messages_count': 0}

    cache_key = f'{user.id}_messages_count'
    count = cache.get(cache_key)
    if count is None:
        count = ReplyContact.objects.filter(user=user, is_read=False).count()
        cache.set(cache_key, count, 60 * 60)
    return {'messages_count': count}


def partner(request):
    part = is_partner(request)
    return {'part': part}
