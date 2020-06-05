# -*- coding: utf-8 -*-
from time import time
import exhibit
from settings import STANDARD_SHIPPING_PRICE, PRIORITY_SHIPPING_PRICE, AUTH_USER_MODEL, DEFAULT_MIN_BIDS_AMOUNT
import settings
from tinymce.models import HTMLField
from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
import random
import decimal
import datetime


class ExhibitManager(models.Manager):
    def funding(self):
        return self.get_query_set().filter(status='funding')

    def full_fund_pause(self):
        return self.get_query_set().filter(status='full_fund_pause')

    def bidding(self):
        return self.get_query_set().filter(status__in=['bidding', 'paused', 'auto_paused'])

    def after_win_pause(self):
        return self.get_query_set().filter(status='after_win_pause')

    def paused(self):
        return self.get_query_set().filter(status__in=['paused', 'auto_paused'])

    def auto_paused_last(self):
        return self.get_query_set().filter(status='auto_paused_last')

    def relisted(self):
        return self.get_query_set().filter(status='relisted')

    def ended(self):
        return self.get_query_set().filter(status__in=['after_win_pause', 'waiting_payment', 'paid'])

    def ended_but_not_paid(self):
        return self.get_query_set().filter(status__in=['after_win_pause', 'waiting_payment'])

    def create_from_item(self, item):
        """
        automatically creates exhibit object with funding status when admin adds new item
        :param item:
        :return: exhibit
        """
        # if amount = 0 or item was marked as giveaway don't create new exhibit
        if item.giveaway or item.amount == 0:
            return False

        exhibit = Exhibit.objects.create(item=item, status='funding', _min_bids_amount=item.min_bids_amount)

        # item amount is None means that item is unlimited
        if item.amount is not None:
            item.amount -= 1
            item.save()

        print '>> create new exhibit %s in status funding' % item.pk

        return exhibit

    def create_giveaway(self, newbie=False):
        """
        creates giveaway exhibit object with bidding status when active exhibits count is less than allowed minimum
        :return: exhibit
        """
        # select giveaway item with amount, which isn't in bidding list, as well as not in funding
        # TODO looks weird, find the way to do it better
        items = Item.objects.filter(giveaway=True, newbie=newbie)\
            .exclude(amount=0)\
            .exclude(pk__in=(Exhibit.objects.filter(status__in=['funding',
                                                                'full_fund_pause',
                                                                'bidding',
                                                                'paused',
                                                                'auto_paused',
                                                                'auto_paused_last',
                                                                'after_win_pause',
                                                                'relisted'])
                                            .values_list('item', flat=True)))

        # return False if can't create giveaway exhibit
        if not items:
            return False

        # take random item
        item = random.choice(items)

        if item.amount is not None:
            item.amount -= 1
            item.save()

        exhibit = Exhibit.objects.create(item=item, status='bidding', _min_bids_amount=item.min_bids_amount)

        print '>> create new giveaway exhibit %s in status bidding' % exhibit

        return exhibit


class ItemManager(models.Manager):
    pass


class ItemBrand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique=True)
    sort = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Item brand '
        verbose_name_plural = u'Item brands'


class ItemCategory(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique=True)
    sort = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Item category '
        verbose_name_plural = u'Item categories'


class Item(models.Model):
    code = models.CharField(max_length=30,
                            primary_key=True,
                            validators=[RegexValidator('^[a-zA-Z0-9-]+$')],
                            help_text="""This field is used to identify p, make sure its value is UNIQUE,\
                            it is NOT allowed to modify after the first time you add it.\
                            Only letters, numbers or hyphens are valid""")

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    our_cost = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    amount = models.SmallIntegerField(null=True, blank=True)
    brand = models.ForeignKey(ItemBrand)
    categories = models.ManyToManyField(ItemCategory)

    # displaying as "m:ss", and "H:mm:ss" for giveaways (max is 23:59:59)
    bidding_time = models.PositiveIntegerField(default=600, validators=[MaxValueValidator(86399), MinValueValidator(1)])
    description = HTMLField(default='', blank=True)
    notes = models.TextField(default='', blank=True, null=True)

    objects = ItemManager()

    image = models.ImageField(upload_to=u'items')

    giveaway = models.BooleanField()
    funding_credits = models.PositiveIntegerField(null=True, blank=True)

    standard_shipping_price = models.SmallIntegerField(blank=True, null=True, default=STANDARD_SHIPPING_PRICE)
    priority_shipping_price = models.SmallIntegerField(blank=True, null=True, default=PRIORITY_SHIPPING_PRICE)

    # lock item after X bids
    lock_after = models.PositiveIntegerField(blank=True, null=True, verbose_name='Lock item after how many bids?')
    # item is only for new users (which have never been winners)
    newbie = models.BooleanField()

    # minimum bids amount to declare winner (only for non-giveaway items)
    min_bids_amount = models.PositiveIntegerField(default=DEFAULT_MIN_BIDS_AMOUNT)

    def __unicode__(self):
        return self.name

    def categories_inline(self):
        return ', '.join([i.name for i in self.categories.all()])
    categories_inline.short_description = "categories"


class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name="images")
    img = models.ImageField(upload_to="items")

    def __unicode__(self):
        return self.img


class Exhibit(models.Model):

    STATUS_CHOICES = (
        ('funding', "Funding"),
        ('full_fund_pause', "Pause after full fund"),
        ('bidding', "Bidding"),
        ('paused', "Paused by admin"),
        ('auto_paused', "Paused by system, after exhibit bidding time extends"),
        ('auto_paused_last', "Last time pause by system"),
        ('after_win_pause', "Pause after someone win exhibit"),
        ('relisted', "Pause after exhibit was relisted"),
        ('waiting_payment', "Waiting Payment"),
        ('paid', "Paid"),
    )

    NEW_BIDDING_TIME_CHOICES = (
        (600, "10 min"),
        (300, "5 min"),
        (120, "2 min"),
        (60, "1 min"),
        (30, "30 s"),
        (10, "10 s"),
        (5, "5 s"),
    )

    item = models.ForeignKey(Item, related_name='exhibits')
    status = models.CharField(max_length=20, default='funding', choices=STATUS_CHOICES, db_index=True)
    previous_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)

    amount_funded = models.PositiveIntegerField(default=0)

    # new bidding time for specific exhibit, changed by admin
    new_bidding_time = models.PositiveIntegerField(choices=NEW_BIDDING_TIME_CHOICES,
                                                null=True,
                                                blank=True,
                                                validators=[MaxValueValidator(86399), MinValueValidator(5)])

    last_bidder_name = models.CharField(max_length=50, default='', db_index=True, blank=True)
    backers_count = models.PositiveIntegerField(default=0)
    last_bidder_member = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True)

    # time, when exhibit starts, appears when someone make first bid
    started_unixtime = models.FloatField(blank=True, null=True)

    # last bidder before timer was automatically reset due to minimum item time display
    last_bidder_before_reset = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True, related_name='reseted_exhibits')

    # time, when exhibit ends, appears when someone make first bid
    ended_unixtime = models.FloatField(blank=True, null=True)

    # time, when exhibit was paused, appears when admin drop bidding timer
    paused_unixtime = models.FloatField(blank=True, null=True)

    # time, when exhibit has been fully funded
    funded_unixtime = models.FloatField(blank=True, null=True)

    # true if exhibit is active but there are no available positions on the desk
    in_queue = models.BooleanField(default=False)
    # created = models.DateTimeField(auto_now_add=True)
    locked = models.BooleanField(default=False)

    # amount of bids for current exhibia (*denormalization for speed up)
    bids_amount = models.PositiveIntegerField(default=0)

    # amount of auto paused times ('Going', 'Going', 'Gone')
    auto_paused_amount = models.PositiveIntegerField(default=0)

    # new minimum bids amount to declare winner (only for non-giveaway items)
    _min_bids_amount = models.PositiveIntegerField(default=DEFAULT_MIN_BIDS_AMOUNT)

    objects = ExhibitManager()

    class CannotBidException(Exception):
        pass

    def set_status(self, status):  # todo change all status setting by this function
        self.previous_status = self.status
        self.status = status

    def end(self):
        self.status = 'after_win_pause'
        self.save()

        # set last win pause and wins number for user won it
        if self.last_bidder_member.win_limited_x2 and self.last_bidder_member.last_win_unixtime > self.last_bidder_member.last_win_unixtime_additional:
            self.last_bidder_member.last_win_unixtime_additional = time()
        else:
            self.last_bidder_member.last_win_unixtime = time()

        self.last_bidder_member.wins_number += 1
        self.last_bidder_member.points += settings.REWARD_FOR_WON
        self.last_bidder_member.save()

    def is_ended(self):
        return time() >= self.ended_unixtime if self.ended_unixtime else False

    def __unicode__(self):
        return self.item.name

    def in_full_fund_pause(self):
        return self.status == 'full_fund_pause'

    @property
    def in_after_win_pause(self):
        return self.status == 'after_win_pause'

    @property
    def in_auto_paused_last(self):
        return self.status == 'auto_paused_last'

    @property
    def is_relisted(self):
        return self.status == 'relisted'

    @property
    def percent_funded(self):
        percent = float(self.amount_funded * 100 / self.item.price)
        return percent if percent <= 99 else 99

    @property
    def ended_time(self):
        if self.ended_unixtime:
            return datetime.datetime.fromtimestamp(float(self.ended_unixtime))
        else:
            return 'no end date yet'

    def bid_by(self, user):
        if user.bids <= 0 and user.bonus_bids <= 0:
            raise Exhibit.CannotBidException("Not enough credit to bid!")

        if self.last_bidder_member == user:
            raise Exhibit.CannotBidException("Unable to bid. You are already the highest bidder.")

        if self.locked:
            if not Bid.objects.filter(exhibit=self, user=user).exists():
                return Exhibit.CannotBidException("Unable to bid. This exhibit is locked")

        if user.is_on_win_limit(giveaway=self.item.giveaway):
            raise Exhibit.CannotBidException("You're on win limit. Please wait")

        if self.item.newbie:
            if user.is_winner:
                raise Exhibit.CannotBidException("Sorry, current exhibit available only for newbies")

        # update exhibit end time
        self.ended_unixtime = time() + self.bidding_time

        # set start time for exhibit
        if not self.last_bidder_name:
            self.started_unixtime = time()

        if user.bonus_bids > 0:
            user.bonus_bids -= 1
            type = 'bonus'
        else:
            user.bids -= 1
            type = 'paid'

        user.points += settings.REWARD_FOR_BID

        Bid.objects.create(exhibit=self, user=user, type=type)

        self.last_bidder_name = user.username
        self.last_bidder_member = user

        # lock item after "item.lock_after" bids
        if self.item.lock_after and self.item.lock_after == self.bids.count():
            self.locked = True

        # increase bids amount
        self.bids_amount +=1

        self.save()
        user.save()

    def is_locked_by(self, user):

        if not self.locked:
            return False

        return self.bids.filter(user=user).exists()

    def fund(self, user, amount):
        self.amount_funded += amount
        if not Fund.objects.filter(exhibit=self, user=user).exists():
            self.backers_count += 1

        Fund.objects.create(exhibit=self, user=user, amount=amount)

        if self.amount_funded >= self.item.price:
            self.funded_unixtime = time()
            self.status = 'full_fund_pause'

        self.save()
        user.points += settings.REWARD_FOR_FUND
        user.bids += Fund.get_bids_count_by_cost(amount)

        print 'end funding'

    def bonus_fund(self, user, funding_credits):
        """
        Fund with funding credits (increase +1 backers number and +%1 of funding percentage).
        """
        new_percent = int(self.percent_funded + 1)
        self.amount_funded = new_percent * self.item.price / 100

        if not Fund.objects.filter(exhibit=self, user=user).exists():
            self.backers_count += 1

        Fund.objects.create(exhibit=self, user=user, amount=funding_credits)

        if self.amount_funded >= self.item.price:
            self.funded_unixtime = time()
            self.status = 'full_fund_pause'

        self.save()

        user.funding_credits -= funding_credits
        user.points += settings.REWARD_FOR_FUND
        user.bonus_bids += funding_credits

        print 'end bonus funding'

    def is_paused(self):
        return self.status == 'paused'

    def is_auto_paused(self):
        return self.status == 'auto_paused'

    def is_auto_paused_last(self):
        return self.status == 'auto_paused_last'

    def can_be_ended(self):
        if self.bids_amount < self.min_bids_amount:
            print '>>> bids amount is less than minimum ammount'
            return False
        else:
            return True

    def cleanup_relisted_exhibit(self):
        self.set_status('funding')
        self.amount_funded = decimal.Decimal(0.9) * self.item.price
        self.last_bidder_name = ''
        self.backers_count = 1
        self.last_bidder_member = None
        self.started_unixtime = None
        self.last_bidder_before_reset = None
        self.ended_unixtime = None
        self.paused_unixtime = None
        self.funded_unixtime = None
        self.in_queue = False
        self.locked = False
        self.bids_amount = 0
        self.auto_paused_amount = 0

    @property
    def bidding_time(self):
        return self.new_bidding_time if self.new_bidding_time else self.item.bidding_time

    @property
    def min_bids_amount(self):
        return self._min_bids_amount if self._min_bids_amount else self.item.min_bids_amount

    def can_extend_timer(self):
        if self.auto_paused_amount < settings.TIMER_EXTENDING_COUNT:
            return True
        return False


class Bid(models.Model):

    TYPES_CHOICES = (
        ('paid', "Paid"),
        ('bonus', "Bonus"),
    )

    exhibit = models.ForeignKey(Exhibit, related_name='bids')
    user = models.ForeignKey(AUTH_USER_MODEL)
    type = models.CharField(max_length=15, choices=TYPES_CHOICES)

    class Meta:
        ordering = ['-id']


class Fund(models.Model):

    # bids cost => bids count (with bonuses)
    BIDS_COUNT_BY_COST = {
        10: 10,
        20: 22,
        50: 55,
        100: 112,
        200: 230,
        500: 600
    }

    exhibit = models.ForeignKey(Exhibit)
    user = models.ForeignKey(AUTH_USER_MODEL)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    @staticmethod
    def get_bids_count_by_cost(bids_cost, coupon=None):
        """
        Returns bids number by amount payed (takes bonuses into account)
        Here we can also add additional logic to manage bonus percent
        """
        amount = Fund.BIDS_COUNT_BY_COST.get(bids_cost, bids_cost)

        # increase bonuses by coupon
        if coupon:
            if coupon.bonus_bids_amount:
                amount += coupon.bonus_bids_amount
            else:
                bonus = amount - bids_cost
                bonus = bonus * float(coupon.bonus_bids_percent) / 100
                amount = bonus + bids_cost

        return amount



