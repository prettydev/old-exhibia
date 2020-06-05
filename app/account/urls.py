# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('account.views',
    url(r'^append-item-wishlist/$', 'append_item_wishlist', name='append_item_wishlist'),
    url(r'^update-item-wishlist/$', 'update_item_wishlist', name='update_item_wishlist'),
    url(r'^address/billing/new$', 'address_edit', {'type': 'billing'}, name='add_billing_address'),
    url(r'^address/shipping/new$', 'address_edit', {'type': 'shipping'}, name='add_shipping_address'),
    url(r'^address/(?P<id>\d+)/edit$', 'address_edit', name='edit_address'),
    url(r'^append-verification-popup/$', 'append_verification_popup', name='append_verification_popup'),
    url(r'^social/logout/$', 'social_logout', name='social_logout'),
    url(r'^verify-email/$', 'verify', {'verification_type': 'email'}, name="verify-email"),
    url(r'^verify-phone/$', 'verify', {'verification_type': 'phone'}, name="verify-phone"),
    url(r'^verify/(?P<verification_key>\w+)/$', 'verify_check_key', name='verify-check-key'),
    url(r'^change-password/$', 'change_password', name="user_password_change"),
    url(r'^change-avatar/$', 'change_avatar', name="user_avatar_change"),
    url(r'^upload-avatar/$', 'upload_avatar_ajax', name="upload-avatar-ajax"),
    url(r'^remove-avatar-from-temp/', 'remove_avatar_from_temp', name="remove-avatar-from-temp"),
    url(r'^remove-user-avatar/$', 'remove_user_avatar', name="remove-user-avatar"),
    url(r'^orders/$', 'orders_list', name="orders_list"),
    url(r'^ban-user/$', 'ban_user', name="ban_user"),
    url(r'^check-coupon-code/$', 'check_coupon_code', name="check_coupon_code"),
)
