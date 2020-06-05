# -*- coding: utf-8 -*-
from urllib2 import urlopen
from datetime import datetime
from django.core.files.base import ContentFile
import settings
from django.contrib import messages


def save_profile_picture(strategy, details, backend, user=None, is_new=False, response=dict(), *args, **kwargs):

    # if it's new association store image, birthday, all that can take
    try:
        if backend.name == 'facebook' and not user.facebook_img:
            image_url = 'http://graph.facebook.com/%s/picture?type=square' % response.get('id')
            filename = '%s_%s.jpg' % (backend.name, user.username)
            user.facebook_img.save(filename, ContentFile(urlopen(image_url).read()))

            birthday = response.get('birthday')

            if birthday:
                user.birthday = datetime.strptime(birthday, '%m/%d/%Y')

            # can be also fetched
            # user.location = response.get('location', dict()).get('name')
            # user.address = response.get('birthday')
            # user.hometown = response.get('hometown')
            # user.gender = response.get('gender')

        elif backend.name == 'google-oauth2' and not user.google_img:
            image_url = response.get('image', []).get('url')
            if image_url:
                filename = '%s_%s.jpg' % (backend.name, user.username)
                user.google_img.save(filename, ContentFile(urlopen(image_url).read()))

    except AttributeError:
        print 'No response!'

    else:
        user.save()


def process_verification_bonuses(strategy, details, backend, user=None, is_new=False, response=dict(), *args, **kwargs):
    if kwargs.get('new_association'):
        if backend.name == 'facebook':
            if user.is_google_verified():
                if user.is_email_verified and user.is_phone_verified:
                    msg = "Congratulations, your profile is now complete."
                    # add all bonuses
                    user.points += settings.REWARD_FOR_FULL_SOCIAL_ASSOCIATE
                    user.bonus_bids += 3
                    user.win_limited_x2 = True
                else:
                    msg = "Successful Facebook association. Verify Phone, Email to get 1 bid, 2x win limit and 4000 points"
                    user.bonus_bids += 2
                user.save()
            else:
                msg = "Successful Facebook association. Verify Google, Phone, Email to get 3 bids, 2x winlimit and 4000 points"

        elif backend.name == 'google-oauth2':
            if user.is_facebook_verified():
                if user.is_email_verified and user.is_phone_verified:
                    msg = "Congratulations, your profile is now complete."
                    # add all bonuses
                    user.points += settings.REWARD_FOR_FULL_SOCIAL_ASSOCIATE
                    user.bonus_bids += 3
                    user.win_limited_x2 = True
                else:
                    msg = "Successful Google association. Verify Phone, Email to get 1 bid, 2x winlimit and 4000 points"
                    # add 2 bonuses bids
		    user.bonus_bids += 2
                user.save()
            else:
                msg = "Successful Google association. Verify Facebook, Phone, Email to get 3 bids, 2x winlimit and 4000 points"

        # hardcode level to 999 so we will now this message is for profile
        messages.add_message(kwargs.get('request'), 999, msg)