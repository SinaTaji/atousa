from django import forms
import re

from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class PhoneValidationMixin:
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        if not value:
            raise forms.ValidationError('لطفا شماره تماس خود را وارد کنید')
        if not re.match(r'^09\d{9}$', value):
            raise forms.ValidationError("شماره موبایل معتبر ایرانی وارد کنید."
                                        " شماره باید با 09 شروع شده و 11 رقم داشته باشد.")
        return value


class RedirectAuthenticatedUserMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_panel_page')
        return super().dispatch(request, *args, **kwargs)
