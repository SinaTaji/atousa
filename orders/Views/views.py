from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from orders.cart import Cart
from orders.form import UserAddressForm, GiftCodeForm
from orders.mixins import CartRequiredMixin
from orders.models import Order, OrderItem, UserAddress


class OrderDetail(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'cart/cart_detail.html', {'cart': cart})


class InformationView(CartRequiredMixin, View):
    template_name = 'cart/information.html'

    def get(self, request):
        user = request.user
        addresses = UserAddress.objects.filter(user=user)

        address_form = UserAddressForm()
        cart = Cart(request)
        if 'shipping_method' not in request.session:
            request.session['shipping_method'] = 'pishteaz'
        context = {
            'cart': cart,
            'address_form': address_form,
            'addresses': addresses,
            'shipping_method': request.session['shipping_method'],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        address_form = UserAddressForm(request.POST)

        if address_form.is_valid():
            cd = address_form.cleaned_data
            user = request.user
            order = user.order_set.filter(paid=False).last()
            send_method = request.session.get('shipping_method')
            order.shipping_method = send_method
            order.total_price = order.get_final_price()
            order.save()
            address = UserAddress.objects.filter(
                user=user,
                province=cd['province'],
                city=cd['city'],
                address=cd['address'],
                postal_code=cd['postal_code'],
                phone=cd['phone']
            ).first()
            if not address:
                address = UserAddress.objects.create(
                    user=user,
                    first_name=cd['first_name'],
                    last_name=cd['last_name'],
                    province=cd['province'],
                    city=cd['city'],
                    address=cd['address'],
                    postal_code=cd['postal_code'],
                    phone=cd['phone'],
                    order=order
                )
            order.address = address
            order.save()

            return redirect(reverse('orders:cart_payment_page'))
        cart = Cart(request)
        addresses = UserAddress.objects.filter(user=request.user)
        context = {
            'cart': cart,
            'address_form': address_form,
            'addresses': addresses,
        }

        return render(request, self.template_name, context=context)


class PaymentView(CartRequiredMixin, View):
    template_name = 'cart/payment.html'

    def get(self, request):
        order = Order.objects.filter(user=request.user, paid=False).prefetch_related(
            Prefetch('items',
                     queryset=OrderItem.objects.select_related('product__product', 'product__color', 'product__size'))
        ).last()

        if not order:
            return redirect('orders:cart_detail_page')

        return render(request, self.template_name, {
            'order': order,
            'order_items': order.items.all(),
        })


class ApplyGiftCodeAjaxView(View):
    def post(self, request, *args, **kwargs):
        form = GiftCodeForm(request.POST, request=request)
        if form.is_valid():
            gift = form.gift
            valid = gift.is_valid()
            if valid:
                request.session['gift'] = {
                    'code': gift.gift_code,
                    'percent': gift.percent,
                    'partner_id': gift.partner_id,
                }
                request.session['ref_code'] = gift.partner.code
                request.session.modified = True
                cart = Cart(request)
                return JsonResponse({
                    'success': True,
                    'message': f'کد تخفیف "{gift.gift_code}" با موفقیت اعمال شد.',
                    'percent': gift.percent,
                    'total_price': cart.get_total_price(),
                    'total_discount': cart.get_total_discount(),
                    'send_free': cart.send_free(),
                })
            return JsonResponse({'errors': form.errors.as_json()}, status=400)
        else:
            return JsonResponse({'errors': form.errors.as_json()}, status=400)
