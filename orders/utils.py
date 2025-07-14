import random
from products.models import ProductVariant
from django.db import transaction
from django.utils.timezone import now


def generate_unique_product_code():
    from .models import Order
    while True:
        code = random.randint(10000, 99999)
        if not Order.objects.filter(code=code).exists():
            return code


def update_stocks(order, result):
    with transaction.atomic():
        order.paid = True
        order.authority = None
        order.ref_id = result['data']['ref_id']
        order.updated = now()

        for item in order.items.select_related('product'):
            product = item.product
            product.stock -= item.quantity
            product.save()

        order.save(update_fields=['paid', 'ref_id', 'updated', 'authority'])


def update_gifts(request):
    gift_data = request.session.get('gift')
    if not gift_data:
        return

    gift_code = gift_data.get('code')
    if not gift_code:
        return

    from account.models import Gift
    try:
        gift = Gift.objects.get(gift_code=gift_code)
        if gift.max_uses and gift.max_uses > 0:
            gift.used_count += 1
            gift.save(update_fields=['used_count'])
    except Gift.DoesNotExist:
        pass
