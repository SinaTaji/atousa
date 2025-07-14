from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from products.models import ProductVariant
from orders.cart import Cart
from orders.models import Order, OrderItem


@login_required
def create_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('orders:cart_detail_page')

    order, create = Order.objects.get_or_create(user=request.user, paid=False)
    order.items.all().delete()
    gift_discount = request.session.get('gift', {}).get('percent', 0)
    for item in cart:
        variant = ProductVariant.objects.get(id=item['variant_id'])
        if not variant.is_active:
            return redirect('/cart/detail/?message=item_out_of_stock')
        else:
            base_price = item['get_discounted_price']
            g_discount = (base_price * (gift_discount / 100)) + item['item_discount']
            final_price = round(base_price * (1 - gift_discount / 100)) * item['quantity']
            OrderItem.objects.create(
                order=order,
                product=variant,
                price=final_price,
                discount=g_discount,
                quantity=item['quantity'],
            )
    return redirect(reverse('orders:cart_information_page'))


@require_http_methods(["GET", "POST"])
def set_shipping_method(request):
    if request.method == 'POST':
        method = request.POST.get('method')
        if method in ['pishteaz', 'tipax']:
            request.session['shipping_method'] = method
    else:
        method = request.session.get('shipping_method', 'pishteaz')

    cart = Cart(request)
    shipping_cost = 0 if method == 'tipax' else (0 if cart.send_free() == 0 else 69000)
    total_price = cart.get_total_price() + shipping_cost

    return JsonResponse({
        'status': 'ok',
        'send_free': None if method == 'tipax' else cart.send_free(),
        'shipping_method': method,
        'shipping_cost': shipping_cost,
        'final_price': total_price,
    })
