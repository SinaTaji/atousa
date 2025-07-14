from django.core.cache import cache


def set_discount_flags(products):
    for p in products:
        p.discount_is_active = cache.get(f'discount_product_{p.id}') or False


def check_exp_discount(products):
    needs_cache_clear = False
    for p in products:
        if p.has_discount and not cache.get(f'discount_product_{p.id}'):
            cache.delete(f'discount_expiry_{p.id}')
            cache.delete(f'discount_product_{p.id}')
            p.has_discount = False
            p.discount = 0
            p.discount_expiry = None
            p.save(update_fields=['has_discount', 'discount', 'discount_expiry'])
    if needs_cache_clear:
        cache.delete('homepage_most_discount')
        cache.delete('homepage_most_recent')
        cache.delete('homepage_most_viewed')