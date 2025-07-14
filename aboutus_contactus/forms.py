from django.forms import ModelForm
from .models import ContactUs
from django import forms


class ContactUsForm(ModelForm):
    class Meta:
        model = ContactUs
        fields = ('ticket', 'text')
        widgets = {
            'ticket': forms.Select(attrs={
                'class': 'form-c',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-c',
                'placeholder': 'متن پیام',
                'rows': 4,
            }),
        }
