import json
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from products.models import ProductVariant
from orders.cart import Cart


@require_POST
def add_to_cart_ajax(request):
    try:
        data = json.loads(request.body)

        try:
            product_id = int(data["product_id"])
            size_id = int(data["size_id"])
            color_id = int(data["color_id"])
            quantity = int(data.get("quantity", 1))
        except (KeyError, ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "پارامترها ناقص یا نادرست‌اند."}, status=400)

        variant = ProductVariant.objects.get(
            product_id=product_id,
            size_id=size_id,
            color_id=color_id,
            is_active=True
        )

        cart = Cart(request)
        cart.add(variant, quantity)

        cart_html = render_to_string("cart/cart_items_partial.html", {"cart": cart}, request=request)

        total_items = sum(item['quantity'] for item in cart.cart.values())
        total_price = cart.get_total_price()

        return JsonResponse({
            "status": "ok",
            "total_items": len(cart),
            "total_price": total_price,
            "cart_html": cart_html,
        })

    except ProductVariant.DoesNotExist:
        return JsonResponse({"status": "error", "message": "این ترکیب رنگ و سایز برای این محصول موجود نیست."},
                            status=404)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "خطا در سرور. لاگ‌ها را بررسی کنید."}, status=500)


@require_POST
def increase_quantity(request):
    data = json.loads(request.body)
    key = data.get('variant_key')
    cart = Cart(request)

    if key:
        cart.increase_quantity(key)
        quantity = cart.cart.get(key, {}).get('quantity', 0)
        return JsonResponse({'new_quantity': quantity,
                             'send_free': cart.send_free() or '',
                             'total_discount': cart.get_total_discount(),
                             'total_org_price': cart.get_total_org_price(),
                             'total_items': len(cart),
                             'total_price': cart.get_total_price()})

    return JsonResponse({'error': 'Invalid key'}, status=400)


@require_POST
def decrease_quantity(request):
    data = json.loads(request.body)
    key = data.get('variant_key')
    cart = Cart(request)

    if key:
        cart.decrease_quantity(key)
        quantity = cart.cart.get(key, {}).get('quantity', 0)
        return JsonResponse({'new_quantity': quantity,
                             'send_free': cart.send_free() or '',
                             'total_discount': cart.get_total_discount(),
                             'total_items': len(cart),
                             'total_org_price': cart.get_total_org_price(),
                             'total_price': cart.get_total_price()})

    return JsonResponse({'error': 'Invalid key'}, status=400)


@require_POST
def remove_from_cart(request):
    data = json.loads(request.body)
    key = data.get('variant_key')
    cart = Cart(request)
    if key:
        cart.remove(key)
        total_price = cart.get_total_price()
        return JsonResponse({'status': 'ok',
                             'send_free': cart.send_free() or '',
                             'total_discount': cart.get_total_discount(),
                             'total_org_price': cart.get_total_org_price(),
                             'total_items': len(cart),
                             'total_price': total_price})
    return JsonResponse({'error': 'Invalid key'}, status=400)
