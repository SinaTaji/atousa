from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders.utils import update_stocks, update_gifts
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from orders.models import Order
from orders.zarinpal_services import send_payment_request, verify_payment
from account.utils import update_partner_stats, is_partner
from aboutus_contactus.utils import send_message
from admin_panel.utils import update_stats_on_order
from utils.telegram import notify_new_order


@login_required
def order_payment_request(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id, user=user, paid=False)

    if order.authority:
        order.authority = None
        order.save(update_fields=['authority'])
    if order.total_price <= 0:
        messages.error(request, "مبلغ سفارش معتبر نیست.")
        return redirect("user_orders_page")

    try:
        result = send_payment_request(order, user.phone, request)
    except RuntimeError as e:
        messages.error(request, "خطایی پیش آمده دوباره امتحان کنید.")
        return redirect("orders:faild_payment_page")

    if result.get('data') and result['data'].get('code') == 100:
        authority = result['data']['authority']
        order.authority = authority
        order.save(update_fields=['authority'])
        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{authority}')
    else:
        order.authority = None
        order.save(update_fields=['authority'])
        messages.error(request, "خطایی پیش آمده دوباره امتحان کنید.")
        return redirect("orders:faild_payment_page")


@login_required
def order_payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    if not authority or not status:
        return HttpResponseBadRequest("پارامترهای مورد نیاز موجود نیستند.")

    if status != 'OK':
        return redirect(reverse('orders:faild_payment_page'))

    order = get_object_or_404(Order, paid=False, authority=authority)

    try:
        result = verify_payment(order, authority)
    except RuntimeError as e:
        return redirect(reverse('orders:faild_payment_page'))

    data = result.get('data', {})
    if data.get('code') == 100:
        gift_data = request.session.get('gift')
        if gift_data and gift_data.get('code'):
            update_gifts(request)
        if request.session.get('ref_code') or is_partner(request):
            update_partner_stats(request, order)
            request.session.pop('ref_code', None)
        update_stocks(order, result)
        update_stats_on_order(order)
        request.session.pop('cart', None)
        request.session.pop('gift', None)
        request.session.pop('shipping_method', None)
        send_message(request.user, type='welcome')
        notify_new_order(order)
        return redirect(reverse('orders:success_payment_page'))
    else:
        order.authority = None
        order.save(update_fields=['authority'])
        error = result.get('errors', {}).get('message', 'تأیید پرداخت ناموفق بود.')
        return redirect(reverse('orders:faild_payment_page'))


@login_required
def payment_success(request):
    order = Order.objects.filter(user=request.user, paid=True).order_by('-updated').first()
    if not order:
        messages.error(request, "سفارشی برای نمایش پیدا نشد.")
        return redirect("orders:cart_detail_page")
    return render(request, 'cart/partial/success_pay.html', {'order': order})


@login_required
def payment_faild(request):
    order = Order.objects.filter(user=request.user, paid=False).order_by('-updated').first()
    if not order:
        messages.error(request, "سفارشی برای نمایش پیدا نشد.")
        return redirect("orders:cart_detail_page")
    return render(request, 'cart/partial/faild-pay.html', {'order': order})
