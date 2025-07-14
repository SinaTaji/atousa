from django import forms
from account.models import User
from .mixins import PhoneValidationMixin


class LoginForm(forms.Form, PhoneValidationMixin):
    phone = forms.CharField(max_length=12, required=True, label='شماره موبایل خود را وارد کنید',
                            widget=forms.TextInput(attrs={'class': 'form-inp', 'inputmode': 'numeric' }))
