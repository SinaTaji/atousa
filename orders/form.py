import re
from django import forms

from account.models import Gift
from .models import UserAddress
from authentication.mixins import PhoneValidationMixin


class UserAddressForm(forms.ModelForm, PhoneValidationMixin):
    first_name = forms.CharField(
        label='نام',
        max_length=50,
        required=True,
        error_messages={'required': 'لطفا نام را وارد کنید'},
        widget=forms.TextInput(attrs={'placeholder': 'نام گیرنده'})
    )

    last_name = forms.CharField(
        label='نام خانوادگی',
        max_length=50,
        required=True,
        error_messages={'required': 'لطفا نام خانوادگی را وارد کنید'},
        widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی گیرنده'})
    )
    address = forms.CharField(
        label='آدرس',
        max_length=200,
        required=True,
        error_messages={'required': 'لطفا آدرس را وارد کنید'},
        widget=forms.TextInput(attrs={'placeholder': 'خیابان , کوچه , پلاک '})
    )
    postal_code = forms.CharField(
        label='کد پستی',
        max_length=11,
        min_length=10,
        required=True,
        error_messages={
            'required': 'کد پستی الزامی است.',
            'min_length': 'لطفا کد پستی را بدون - و فاصله وارد کنید',
            'max_length': 'لطفا کد پستی را بدون - و فاصله وارد کنید',
        },
        widget=forms.TextInput(attrs={'placeholder': 'کد پستی گیرنده', 'inputmode': 'numeric', })
    )

    class Meta:
        model = UserAddress
        exclude = ['user', 'order']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'شماره موبایل گیرنده'}),
            'province': forms.Select(attrs={'id': 'province-select'}),
            'city': forms.Select(attrs={'id': 'city-select'}),
        }

    def clean_postal_code(self):
        postal = self.cleaned_data.get('postal_code')
        if not re.fullmatch(r'\d{10}', postal):
            raise forms.ValidationError("کد پستی باید دقیقاً ۱۰ رقم عددی باشد (بدون خط تیره یا فاصله)")
        return postal


class GiftCodeForm(forms.Form):
    gift_code = forms.CharField(label='کد تخفیف', max_length=15)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_gift_code(self):
        code = self.cleaned_data['gift_code'].strip()

        if self.request and self.request.session.get('gift', {}).get('code') == code:
            raise forms.ValidationError("این کد تخفیف قبلاً اعمال شده است.")

        try:
            gift = Gift.objects.get(gift_code__iexact=code)
        except Gift.DoesNotExist:
            raise forms.ValidationError("کد تخفیف وارد شده معتبر نیست.")

        if not gift.is_valid():
            if gift.is_active:
                gift.is_active = False
                gift.save(update_fields=['is_active'])
                raise forms.ValidationError("این کد تخفیف منقضی شده یا دیگر قابل استفاده نیست.")

        self.gift = gift
        return code
