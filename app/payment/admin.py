from account.classes import ReadOnlyAdmin
from django.contrib import admin
from .models import Transaction, BuyBid, BuyItem, BuyShipping, BuyItemAndReturnBid


class AdminTransaction(ReadOnlyAdmin):
    list_display = ('type', 'status', 'payment_method', 'exhibit', 'item', 'user', 'amount')
    readonly_fields = ('payment_id', 'payment_payer_id')
    search_fields = ('user__username', 'item__name', 'payment_id', 'payment_payer_id')

    def queryset(self, request):
        # first we need to display paid transactions with priority shipping
        qs = super(AdminTransaction, self).queryset(request).exclude(status='expired')
        qs = qs.extra(
            select={'sort_by_status': 'IF(status="paid", 1, 2)',
                    'sort_by_shipping': 'IF(shipping_method="priority", 1, 2)'
            }
        )
        qs = qs.order_by('sort_by_status', 'sort_by_shipping')
        return qs


class AdminBuyBids(AdminTransaction):
    list_display = ('status', 'payment_method', 'exhibit', 'user', 'amount')

    def queryset(self, request):
        return super(AdminBuyBids, self).queryset(request).filter(type='buy_bids')


class AdminBuyItem(AdminTransaction):
    list_display = ('status', 'payment_method', 'item', 'user', 'amount')

    def queryset(self, request):
        return super(AdminBuyItem, self).queryset(request).filter(type='buy_item')


class AdminBuyShipping(AdminTransaction):
    list_display = ('status', 'payment_method', 'exhibit', 'user', 'amount', 'user_email', 'user_phone')

    def queryset(self, request):
        return super(AdminBuyShipping, self).queryset(request).filter(type='buy_shipping')

    def user_email(self, obj):
        return obj.user.email

    def user_phone(self, obj):
        return obj.user.phone


class AdminBuyItemAndReturnBid(AdminTransaction):
    list_display = ('status', 'payment_method', 'exhibit', 'user', 'amount')

    def queryset(self, request):
        return super(AdminBuyItemAndReturnBid, self).queryset(request).filter(type='buy_item_return_bids')


admin.site.register(Transaction, AdminTransaction)
admin.site.register(BuyBid, AdminBuyBids)
admin.site.register(BuyItem, AdminBuyItem)
admin.site.register(BuyShipping, AdminBuyShipping)
admin.site.register(BuyItemAndReturnBid, AdminBuyItemAndReturnBid)