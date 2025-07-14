from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from .models import Partnership


class ActivePartnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('user_login_page'))

        try:
            partner = Partnership.objects.get(user=request.user)
        except Partnership.DoesNotExist:
            raise Http404("شما همکار ثبت‌نام‌شده نیستید.")

        if not partner.is_active:
            messages.info(request,
                          'کاربر گرامی شما قبلا ثبت نام کرده اید لطفا منتظر نتیجه بمانید')
            return redirect(reverse('user_panel_page'))

        self.partner = partner
        return super().dispatch(request, *args, **kwargs)
