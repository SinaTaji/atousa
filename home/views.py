from xml.etree.ElementTree import Element, SubElement, tostring
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from .models import Banner
from products.models import Product, Category
from .utils import set_discount_flags, check_exp_discount


def home(request):
    banners = cache.get('homepage_banners')
    if not banners:
        banners = Banner.objects.filter(is_active=True)
        cache.set('homepage_banners', banners, 8200)

    products = Product.objects.filter(is_active=True)
    discount_products = products.filter(is_active=True, has_discount=True)

    check_exp_discount(discount_products)

    most_discount = cache.get('homepage_most_discount')
    if not most_discount:
        most_discount = products.filter(has_discount=True).order_by('-discount')[:10]
        cache.set('homepage_most_discount', most_discount, 7200)

    most_recent = cache.get('homepage_most_recent')
    if not most_recent:
        most_recent = products.order_by('-created_at')[:10]
        cache.set('homepage_most_recent', most_recent, 7200)

    most_viewed = cache.get('homepage_most_viewed')
    if not most_viewed:
        most_viewed = products.order_by('-views')[:10]
        cache.set('homepage_most_viewed', most_viewed, 7200)

    set_discount_flags(most_discount)
    set_discount_flags(most_recent)
    set_discount_flags(most_viewed)

    earliest_expiry = None

    for p in most_discount:
        expiry = cache.get(f'discount_expiry_{p.id}')
        if expiry and (earliest_expiry is None or expiry > earliest_expiry):
            earliest_expiry = expiry

    categori = Category.objects.prefetch_related('sub_category').filter(image__isnull=False, is_active=True).order_by(
        '-image')[:4]
    context = {
        'categori': categori,
        'banners': banners,
        'most_discount': most_discount,
        'most_recent': most_recent,
        'most_viewed': most_viewed,
        'global_discount_expiry': earliest_expiry,
    }
    return render(request, 'home/home.html', context)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /account/favorite/toggle/",
        "Disallow: /account/wishlist/",
        "Disallow: /account/partner-ship/",
        "Disallow: /account/dashboard/",
        "Disallow: /account/gift-box/",
        "Disallow: /account/withdraw/",
        "Disallow: /user/register/",
        "Disallow: /user/login/",
        "Disallow: /user/logout/",
        "Disallow: /user/verify/",
        "Disallow: /user/resend_otp/",
        "Disallow: /user/forgot_pass/",
        "Disallow: /user/reset_pass/",
        "Disallow: /product/ajax/search-suggestions/",
        "Disallow: /cart/add-to-cart-ajax/",
        "Disallow: /cart/increase/",
        "Disallow: /cart/decrease/",
        "Disallow: /cart/del/order/",
        "Disallow: /cart/set-shipping-method/",
        "Disallow: /cart/create-order/",
        "Disallow: /cart/detail/",
        "Disallow: /cart/information/",
        "Disallow: /cart/payment/",
        "Disallow: /cart/apply-gift-code/",
        "Disallow: /cart/pay/",
        "Disallow: /cart/verify/",
        "Disallow: /cart/success-payment/",
        "Disallow: /cart/faild-payment/",
        "Disallow: /us/send-contact/",
        "Disallow: /us/user-panel/",
        "Disallow: /us/my-tickets/",
        "Disallow: /us/my-address/",
        "Disallow: /us/my-orders/",
        "Disallow: /us/ajax/orders/",
        "Disallow: /us/ajax/user-counts/",
        "Sitemap: https://example.com/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


