# -*- coding: utf-8 -*-
from account.models import Address
from django.forms.widgets import RadioSelect, HiddenInput

from django import forms
from payment.models import Transaction


class BuyNowForm(forms.ModelForm):

    # shipping_address = forms.ModelChoiceField(queryset=Address.objects.filter(type='shipping'),
    #                                           empty_label='-------',
    #                                           widget=forms.Select(attrs={'class': 'form-control'}),
    #                                           required=False)
    #
    # billing_address = forms.ModelChoiceField(queryset=Address.objects.filter(type='billing'),
    #                                          empty_label='-------',
    #                                          widget=forms.Select(attrs={'class': 'form-control'}),
    #                                          required=False)

    class Meta:

        exclude = ['payment_url', 'status', 'amount', 'user', 'ip', 'created', 'exhibit', 'shipping_address', 'billing_address']

        widgets = {
            'shipping_method': forms.widgets.RadioSelect(),
            'payment_method': forms.widgets.HiddenInput(),
            'item': forms.widgets.HiddenInput(),
        }

        model = Transaction

    def __init__(self, *args, **kwargs):
        super(BuyNowForm, self).__init__(*args, **kwargs)

        item = self.instance.get_item()

        if self.instance.user and item:

            # billing_addresses = self.instance.user.addresses.filter(type="billing")
            # self.fields['billing_address'].queryset = billing_addresses
            #
            # if billing_addresses:
            #     self.fields['billing_address'].initial = billing_addresses[0]
            #
            # shipping_addresses = self.instance.user.addresses.filter(type="shipping")
            # self.fields['shipping_address'].queryset = shipping_addresses
            #
            # if shipping_addresses:
            #     self.fields['shipping_address'].initial = shipping_addresses[0]

            self.fields['shipping_method'].choices = [
                ('standard', 'Standard shipping $%.2f' % item.standard_shipping_price),
                ('priority', 'Priority shipping $%.2f' % item.priority_shipping_price),
            ]


class BuyShippingForm(BuyNowForm):
    class Meta:
        exclude = ['payment_url', 'status', 'amount', 'user', 'ip', 'created', 'item']

        widgets = {
            'shipping_method': forms.widgets.RadioSelect(),
            'payment_method': forms.widgets.RadioSelect(),
            'exhibit': forms.widgets.HiddenInput(),
        }

        model = Transaction


class BuyWithBidsReturnForm(BuyNowForm):
    class Meta:
        exclude = ['payment_url', 'status', 'amount', 'user', 'ip', 'created', 'item']

        widgets = {
            'shipping_method': forms.widgets.RadioSelect(),
            'payment_method': forms.widgets.RadioSelect(),
            'exhibit': forms.widgets.HiddenInput(),
        }

        model = Transaction


class ExhibitFundingForm(forms.Form):
    pass
