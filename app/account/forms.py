# -*- coding: utf-8 -*-
from account.models import VerificationProfile
from django import forms
from payment.models import Address


class AddressForm(forms.ModelForm):

    class Meta:
        exclude = ['deleted', 'type', 'user']
        model = Address


class EmailVerificationForm(forms.ModelForm):

    class Meta:
        exclude = ['verification_key', 'type', 'user', 'phone', 'attempts']
        model = VerificationProfile
        widgets = {
            'email': forms.TextInput(
                attrs={'placeholder': 'your@mail.com'}),
        }


class PhoneVerificationForm(forms.ModelForm):

    class Meta:
        exclude = ['verification_key', 'type', 'user', 'email', 'attempts']
        model = VerificationProfile
        widgets = {
            'phone': forms.TextInput(
                attrs={'placeholder': '15005550006'}),
        }