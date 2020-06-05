# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('payment.views',
    url(r'^append-buy-now-form/$', 'append_buy_now_form'),
    url(r'^append-buy-shipping-form/$', 'append_buy_shipping_form'),
    url(r'^append-bids-return-form/$', 'append_bids_return_form'),
    url(r'^buy-now/$', 'buy_now', name='buy_now'),
    url(r'^buy-shipping/$', 'buy_shipping', name='buy_shipping'),
    url(r'^buy-and-return-bids/$', 'buy_and_return_bids', name='buy_and_return_bids'),
    url(r'^buy-bids/$', 'buy_bids', name='buy_bids'),
    url(r'^buy-now/paypal$', 'buy_now_paypal', name='buy_now_paypal'),
    url(r'^buy-shipping/paypal$', 'buy_shipping_paypal', name='buy_shipping_paypal'),
    url(r'^buy-bids/paypal$', 'buy_bids_paypal', name='buy_bids_paypal'),
    url(r'^buy-and-return-bids/paypal$', 'buy_and_return_bids_paypal', name='buy_and_return_bids_paypal'),
    url(r'^cancel-order/$', 'cancel_order', name='cancel_order'),
)
