# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
from time import time
import urllib
import urllib2
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.crypto import random
from exhibit.models import Item
import settings
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib import messages
from django.core.validators import MaxValueValidator


class Profile(AbstractUser):
    location = models.CharField(_(u"location"), max_length=40, null=True, blank=True)

    bids = models.PositiveIntegerField(default=0)
    bonus_bids = models.PositiveIntegerField(default=3)
    funding_credits = models.PositiveIntegerField(default=0)

    phone = models.CharField(max_length=30, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, help_text="for example: 1980-7-9")

    referer = models.ForeignKey('self', null=True, blank=True, editable=False)
    referer_activated = models.BooleanField(default=False, help_text='True if referer got bonus for invite')
    win_limited_x2 = models.BooleanField(default=False, help_text='2x winlimit')

    is_banned = models.BooleanField(default=False, help_text='Banned for chat or not')
    points = models.PositiveIntegerField(default=0)

    # payed exhibits can be deleted, so we need to store wins count in user model + less requests
    wins_number = models.PositiveIntegerField(default=0, help_text='Number of user wins')

    # last time when user wins in bidding
    last_win_unixtime = models.FloatField(blank=True, null=True)

    # last time when user wins in bidding (for additional 2x winlimit)
    last_win_unixtime_additional = models.FloatField(blank=True, null=True)

    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    img = models.ImageField(upload_to='users', null=True, blank=True, verbose_name='Profile image')
    facebook_img = models.ImageField(upload_to='users', null=True, blank=True)
    google_img = models.ImageField(upload_to='users', null=True, blank=True)

    last_payment_id = models.CharField(max_length=50, null=True, blank=True, editable=False)
    last_transaction_id = models.CharField(max_length=50, null=True, blank=True, editable=False)

    def __unicode__(self):
        return self.username

    def incr_bids(self, bids):
        self.bids += bids
        self.save()

    @property
    def is_newbie(self):
        return not self.is_winner

    @property
    def is_winner(self):
        return self.wins_number

    def is_on_win_limit(self, giveaway=False):
        result = (self.last_win_unixtime + settings.WIN_LIMIT_TIME) >= time() if self.last_win_unixtime else False

        if giveaway:
            return result

        if self.win_limited_x2 and result:
            result = (self.last_win_unixtime_additional + settings.WIN_LIMIT_TIME) >= time() if self.last_win_unixtime_additional else False

        return result

    @property
    def win_limit_time_left(self):
        if self.win_limited_x2:
            last_win_time = min((self.last_win_unixtime or 0), (self.last_win_unixtime_additional or 0))
        else:
            last_win_time = (self.last_win_unixtime or 0)

        return float(last_win_time) + settings.WIN_LIMIT_TIME - time()

    @property
    def avatar(self):
        if self.img:
            url = str(self.img)
        elif self.facebook_img:
            url = str(self.facebook_img)
        elif self.google_img:
            url = str(self.google_img)
        else:
            url = Profile.defaul_avatar()

        return url

    @staticmethod
    def defaul_avatar():
        return 'img/user-no-image.jpg'

    def social_notify(self, exhibit):
        """
        notify user when item in his wish list was fully funded
        """
        message = 'Item "%s" was fully funded. Exhibit will start in %s minutes' \
                  % (exhibit.item.name, settings.FULL_FUND_PAUSE_TIME/60)

        providers = set(i.type for i in self.wishlist.filter(item=exhibit.item))  # filter by item

        if 'facebook' in providers:
            params = {
                'access_token': settings.FACEBOOK_APP_TOKEN,
                'template': message,
                'href': '#'
            }
            try:
                req = urllib2.Request(
                    "https://graph.facebook.com/%s/notifications" % self.social_auth.filter(provider='facebook')[0].uid,
                    urllib.urlencode(params), {})
                urllib2.urlopen(req).read()
            except (urllib2.HTTPError, KeyError):
                pass
        elif 'twitter' in providers:
            pass

        elif 'google' in providers:
            pass
        else:
            pass

    def is_facebook_verified(self):
        return self.social_auth.filter(provider='facebook').exists()

    def is_google_verified(self):
        return self.social_auth.filter(provider='google-oauth2').exists()


class Address(models.Model):

    TYPE_CHOICES = (
        ('billing', "Billing"),
        ('shipping', "Shipping"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses')
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    country = CountryField()
    postal_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)

    def __unicode__(self):
        return u"{} {}, {} {} {}".format(self.first_name, self.last_name, self.country, self.city, self.phone)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)


class ProfileItemNotification(models.Model):

    NOTIFICATION_CHOICES = (
        ('facebook', "Facebook message"),
        # ('google', "Google+ message"),
        # ('twitter', "Twitter tweet"),
        ('email', "Email"),
        ('sms', "Text message"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wishlist')
    item = models.ForeignKey(Item, related_name='notifications')
    type = models.CharField(max_length=15, choices=NOTIFICATION_CHOICES)


class VerificationManager(models.Manager):

    def verify_user(self, user, verification_key, request):

        profile = self.get(user=user, verification_key=verification_key)

        if profile.is_email():
            if user.is_email_verified:
                raise VerificationProfile.NotVerifedException('Email was already verified')

            user.is_email_verified = True

            if user.is_phone_verified and user.is_facebook_verified() and user.is_google_verified():
                user.points += settings.REWARD_FOR_FULL_SOCIAL_ASSOCIATE
                user.bonus_bids += 1
                user.win_limited_x2 = True
                msg = "Congratulations, your profile is now complete."
            else:
                msg = "Successful Email association. Verify Phone, Facebook, Google to get 3 bids, 2x winlimit and 4000 points"

        else:
            if user.is_phone_verified:
                raise VerificationProfile.NotVerifedException('Phone was already verified')

            user.is_phone_verified = True
            user.phone = profile.phone

            if user.is_email_verified and user.is_facebook_verified() and user.is_google_verified():
                user.points += settings.REWARD_FOR_FULL_SOCIAL_ASSOCIATE
                user.bonus_bids += 1
                user.win_limited_x2 = True
                msg = "Congratulations, your profile is now complete."
            else:
                msg = "Successful Phone association. Verify Email, Facebook, Google to get 3 bids, 2x winlimit and 4000 points"

        user.save()
        profile.verification_key = self.model.ACTIVATED
        profile.save()

        messages.add_message(request, 999, msg)

        return profile

    def create_profile(self, user, verification_type):
        """
        Create a VerificationProfile for a given User
        """
        if verification_type == 'email':
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            username = user.username
            if isinstance(username, unicode):
                username = username.encode('utf-8')
            verification_key = hashlib.sha1(salt+username).hexdigest()
        else:
            # for phone, random 4-digit codes
            verification_key = random.randint(1000, 9999)

        return self.model(user=user,
                          verification_key=verification_key,
                          type=verification_type,
                          )


class IpAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ip_addresses')
    ip_address = models.IPAddressField()
    last_login = models.DateField(default=datetime.now)

    class Meta:
        unique_together = ('user', 'ip_address')
        ordering = ('-last_login', )
        verbose_name_plural = 'IP addresses'


class VerificationProfile(models.Model):
    """
    A simple profile which stores an verification key for use during
    user account email and mobile verification.
    """
    ACTIVATED = u"ALREADY_VERIFICATED"

    TYPE_CHOICES = (
        ('email', "Email"),
        ('phone', "Phone"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    verification_key = models.CharField(_('verification key'), max_length=40)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True, validators=[RegexValidator
                                                                   (
                                                                       regex='^\+?[0-9]{3,15}$',
                                                                       message='Wrong phone number',
                                                                   ),
                                                                   ])

    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    attempts = models.SmallIntegerField(default=0)

    objects = VerificationManager()

    def is_email(self):
        return self.type == 'email'

    def is_phone(self):
        return self.type == 'phone'

    class Meta:
        verbose_name = _('verification profile')
        verbose_name_plural = _('verification profiles')
        unique_together = ('user', 'type',)

    class NotVerifedException(Exception):
        pass

    def __unicode__(self):
        return u"Verification information for %s" % self.user


class SmsMessage(models.Model):

    TYPE_CHOICES = (
        ('success', "Success"),
        ('error', "Error"),
    )

    error_message = models.TextField(max_length=500, null=True, blank=True)
    verification = models.ForeignKey(VerificationProfile, null=True, blank=True)
    status = models.CharField(max_length=15, choices=TYPE_CHOICES)


class Coupon(models.Model):

    PERCENT_CHOICES = (
        ('200', "x2"),
        ('300', "x3"),
    )

    code = models.PositiveIntegerField(unique=True, db_index=True, primary_key=True, editable=False)
    expired_time = models.DateTimeField(blank=True, null=True)  # expired_time [from one minute up to 30 days]
    expired_after_uses = models.PositiveIntegerField(blank=True, null=True)
    bonus_bids_amount = models.PositiveIntegerField(blank=True, null=True)
    bonus_bids_percent = models.CharField(max_length=15, choices=PERCENT_CHOICES, blank=True, null=True)
    min_package_amount = models.PositiveIntegerField(blank=True, null=True)
    funding_percent = models.PositiveIntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])

    def clean(self):
        super(Coupon, self).clean()
        # check that only one of "expire time" or "expire after uses" field is filled
        if self.expired_time and self.expired_after_uses:
            raise ValidationError('Please use only one expire parameter')
        if not self.expired_time and not self.expired_after_uses:
            raise ValidationError('Expires parameter is empty')

        # check that only one of "bonus_bids_amount" or "bonus_bids_percent" field is filled
        if self.bonus_bids_amount and self.bonus_bids_percent:
            raise ValidationError('Please use only one bonus bids parameter')
        if not self.bonus_bids_amount and not self.bonus_bids_percent:
            raise ValidationError('Bonus bids parameter is empty')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.code:
            # generate unique 5 digit (or more) code
            code = random.randint(10000, 999999999)
            # check that generated code is unique
            while Coupon.objects.filter(code=code).count() > 0:
                code = random.randint(10000, 999999999)
            self.code = code

        super(Coupon, self).save(force_insert, force_update, using, update_fields)

    def view_type(self):
        if self.bonus_bids_amount:
            return '%s bonus bids' % self.bonus_bids_amount
        else:
            for key, label in Coupon.PERCENT_CHOICES:
                if key == self.bonus_bids_percent:
                    return '%s bonus' % label
        return ''

    def is_expired(self):
        if self.expired_time:
            return timezone.now() > self.expired_time
        else:
            return self.payments.filter(status__in=['shipped', 'paid']).count() > self.expired_after_uses

    def is_already_used_by(self, user):
        return self.payments.filter(status__in=['shipped', 'paid'], user=user).exists()

    def __unicode__(self):
        return '%s code #%s' % (self.view_type(), self.code)
