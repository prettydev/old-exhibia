# -*- coding: utf-8 -*-
from account.models import Address, Coupon
from django.db import models
from exhibit.models import Item, Exhibit
from settings import AUTH_USER_MODEL


class TransactionManager(models.Manager):

    def item_transaction(self):
        return self.get_query_set().exclude(type='buy_bids')

    def processing_item_transaction(self):
        return self.item_transaction().exclude(status__in=['new', 'fail', 'expired'])

    def shipped(self):
        return self.item_transaction().filter(status='shipped')

    def processing(self):
        return self.item_transaction().exclude(status__in=['shipped', 'fail', 'new', 'expired'])

    def deletable(self):
        return self.get_query_set().filter(status__in=['new', 'fail', 'expired'])


class Transaction(models.Model):
    """
    There will be just 3 types. User pays when he
      1) Wins an exhibit, he's paying just for shipping
      2) Buying now, he paying the whole retail price of an item
      3) Purchases bids
    """

    TRANSACTION_STATUS = (
        ('new', 'Transaction just created'),
        ('paid', 'Transaction paid'),
        ('fail', 'Transaction fail'),
        ('shipped', 'Order shipped'),
        ('expired', 'Expired'),
    )

    PAYMENT_METHOD = (
        ('paypal', 'Paypal'),
        # ('dalpay', 'Dalpay')
    )

    SHIPPING_METHOD = (
        ('standard', 'Standard'),
        ('priority', 'Priority'),
    )

    TRANSACTION_TYPE = (
        ('buy_bids', 'Buy bids'),
        ('buy_item', 'Buy item'),
        ('buy_item_return_bids', 'Buy item and return bids back'),
        ('buy_shipping', 'Buy shipping for won exhibit'),
    )

    objects = TransactionManager()

    payment_id = models.CharField(max_length=255, editable=False)
    payment_token = models.CharField(max_length=255, editable=False)
    payment_payer_id = models.CharField(max_length=255, editable=False, blank=True)
    payment_url = models.URLField(help_text="Payment URL on payment system site", null=True, blank=True)
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD,  default='paypal')
    exhibit = models.ForeignKey(Exhibit, blank=True, null=True, related_name='payments')
    item = models.ForeignKey(Item, blank=True, null=True)
    shipping_method = models.CharField(max_length=25, choices=SHIPPING_METHOD, default='standard')
    shipping_address = models.ForeignKey(Address, related_name="shipping_transaction", blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name="billing_transaction", blank=True, null=True)
    status = models.CharField(max_length=25, choices=TRANSACTION_STATUS, default='new')
    type = models.CharField(max_length=25, choices=TRANSACTION_TYPE, blank=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    user = models.ForeignKey(AUTH_USER_MODEL, related_name="payments")
    coupon = models.ForeignKey(Coupon, blank=True, null=True, related_name="payments")
    ip = models.IPAddressField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    delivery_service = models.CharField(max_length=25, blank=True, null=True)
    delivery_number = models.CharField(max_length=100, blank=True, null=True)
    amount_for_fund = models.PositiveIntegerField(blank=True, null=True)

    def get_item(self):
        if self.item:
            return self.item
        elif self.exhibit:
            return self.exhibit.item

    def is_not_payed(self):
        return self.status not in ['paid', 'shipped']

    def is_won(self):
        return True if self.type == 'buy_shipping' else False


class BuyBid(Transaction):
    class Meta:
        proxy = True


class BuyItem(Transaction):
    class Meta:
        proxy = True


class BuyItemAndReturnBid(Transaction):
    class Meta:
        proxy = True


class BuyShipping(Transaction):
    class Meta:
        proxy = True