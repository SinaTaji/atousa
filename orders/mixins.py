from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from .cart import Cart


class CartRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect(reverse('product_list_page'))
        return super().dispatch(request, *args, **kwargs)
