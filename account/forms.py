from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, Partnership, Withdraw


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=100, label='کلمه عبور')
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=100, label='تکرار کلمه عبور')

    class Meta:
        model = User
        fields = ('phone', 'password1', 'password2')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('کلمه عبور با تکرار آن مغایرت دارد')

        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'password')


class PartnershipForm(forms.ModelForm):
    class Meta:
        model = Partnership
        fields = ['first_name', 'last_name', 'image']

        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'image': 'تصویر پروفایل',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'نام',

            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'نام خانوادگی',
            }),
        }

        error_messages = {
            'first_name': {
                'required': 'لطفاً نام خود را وارد کنید.',
            },
            'last_name': {
                'required': 'لطفاً نام خانوادگی خود را وارد کنید.',
            },
            'image': {
                'required': 'لطفاً تصویر پروفایل خود را بارگذاری کنید.',
            },
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('لطفاً تصویر پروفایل خود را بارگذاری کنید.')
        if image and image.size > 2 * 1024 * 1024:
            raise forms.ValidationError('حجم تصویر نباید بیشتر از ۲ مگابایت باشد.')
        return image


class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = ['card', 'amount']
        labels = {
            'card': 'شماره کارت',
            'amount': 'مبلغ',
        }
        widgets = {
            'card': forms.TextInput(attrs={
                'placeholder': 'شماره کارت',
                'inputmode': 'numeric',

            }),
            'amount': forms.TextInput(attrs={
                'placeholder': 'مبلغ به تومان',
                'inputmode': 'numeric',
            }),
        }

        error_messages = {
            'card': {
                'required': 'لطفاً شماره کارت خود را وارد کنید.',
            },
            'amount': {
                'required': 'مبلغ را وارد کنید.',
            },
        }

    def clean_card(self):
        card = self.cleaned_data.get('card').strip()
        if len(card) != 16:
            raise forms.ValidationError('شماره کارت اشتباه است')
        if not card.isdigit():
            raise forms.ValidationError('شماره کارت معتبر وارد کنید')
        return card

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 500000:
            raise forms.ValidationError('حداقل مبلغ قابل برداشت 500,000 تومان است')
        return amount
