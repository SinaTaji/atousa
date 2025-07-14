from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import WishList
from products.models import Product
from django.db.models.signals import post_save
from django.core.cache import cache
from django.utils import timezone


@receiver(user_logged_in)
def merge_session_wishlist(sender, user, request, **kwargs):
    wishlist = request.session.get('wishlist', [])
    for product_id in wishlist:
        try:
            product = Product.objects.get(id=product_id)
            if not WishList.objects.filter(user=user, product=product).exists():
                WishList.objects.create(user=user, product=product)
        except Product.DoesNotExist:
            continue

        if 'wishlist' in request.session:
            del request.session['wishlist']


@receiver(post_save, sender=Product)
def apply_discount_to_variants(sender, instance, **kwargs):
    if instance.has_discount and instance.discount > 0 and instance.discount_expiry and instance.discount_expiry > timezone.now():
        instance.variants.filter(has_discount=False).update(
            discount=instance.discount,
            has_discount=True
        )

        cache_key_status = f'discount_product_{instance.id}'
        cache_key_expiry = f'discount_expiry_{instance.id}'

        expire_seconds = int((instance.discount_expiry - timezone.now()).total_seconds())
        cache.set(cache_key_status, True, timeout=expire_seconds)
        cache.set(cache_key_expiry, instance.discount_expiry, timeout=expire_seconds)

    else:
        instance.variants.filter(has_discount=True).update(
            discount=0,
            has_discount=False
        )
        cache.delete(f'discount_product_{instance.id}')
        cache.delete(f'discount_expiry_{instance.id}')
