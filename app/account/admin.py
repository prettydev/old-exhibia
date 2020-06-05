# -*- coding: utf-8 -*-
from account.classes import ReadOnlyAdmin
from django import forms
from django.contrib import admin
from .models import Profile, Address, ProfileItemNotification, VerificationProfile, SmsMessage, IpAddress, Coupon


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    extra = 0


class AdminVerificationProfileItem(ReadOnlyAdmin):
    list_display = ('user', 'type', 'email', 'phone', 'verification_key')
    search_fields = ['email', 'phone', 'verification_key', 'user__username']
    inlines = [SmsMessageInline]


class AdminIpAddress(ReadOnlyAdmin):
    list_display = ('user', 'ip_address', 'last_login')
    search_fields = ['user__username', 'ip_address']


class AdminProfile(ReadOnlyAdmin):
    list_display = ('username', 'first_name', 'last_name', 'phone', 'email', 'is_superuser', 'bids', 'bonus_bids',)
    search_fields = ['username', 'first_name', 'last_name', 'phone', 'email']


class AdminAddress(ReadOnlyAdmin):
     def get_model_perms(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return {
                'add': False,
                'change': False,
                'delete': False,
            }
        else:
            return super(AdminAddress, self).get_model_perms(request)


class AdminProfileItemNotification(ReadOnlyAdmin):
    pass


class AdminCoupon(ReadOnlyAdmin):
    def get_model_perms(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return {
                'add': False,
                'change': False,
                'delete': False,
            }
        else:
            return super(AdminCoupon, self).get_model_perms(request)

admin.site.register(Address, AdminAddress)
admin.site.register(ProfileItemNotification, AdminProfileItemNotification)
admin.site.register(Coupon, AdminCoupon)
admin.site.register(VerificationProfile, AdminVerificationProfileItem)
admin.site.register(IpAddress, AdminIpAddress)
admin.site.register(Profile, AdminProfile)

