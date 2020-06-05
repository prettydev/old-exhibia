import os
import urllib, urllib2, settings
from account.models import Profile, SmsMessage
from django.core.management.base import BaseCommand, CommandError
from time import time
from exhibit.models import Exhibit
from screen_capture.models import ExhibitWinnerPost
from utils.facebook_posts import facebook_public_winner_post, facebook_public_winner_post_at_exhibia


class Command(BaseCommand):
    help = 'Run phantomjs to save exhibit winner images'
    # there should be folder ./media/winner_posts
    # run it by crontab every 2 minutes

    def handle(self, *args, **options):
        # get all fresh won exhibits
        exhibits = Exhibit.objects.after_win_pause()

        for exhibit in exhibits:
            try:
                ExhibitWinnerPost.objects.get(exhibit=exhibit)
            except ExhibitWinnerPost.DoesNotExist:

                # run phantomjs to get and save winner post image
                phantomjs_script_path = '%s/phantomjs_scripts/generate_winner_post_image.js' \
                        % os.path.dirname(os.path.abspath(__file__))

                os.system("phantomjs %s %s" % (phantomjs_script_path, exhibit.id))

                # check if file was saved correctly
                filename = 'winner_posts/%s_exhibit_winner.png' % exhibit.id

                if os.path.isfile('%s/%s' % (settings.MEDIA_ROOT, filename)):
                    user = exhibit.last_bidder_member
                    exhibit_post = ExhibitWinnerPost(exhibit=exhibit, image=filename)
                    exhibit_post.save()

                    # create FB post on user's feed
                    if user.is_facebook_verified():
                        facebook_public_winner_post(user, 'http://%s%s%s' 
                            % (settings.SITE, settings.MEDIA_URL, filename), exhibit.item.name)

                    # create post on exhibia wall
                    facebook_public_winner_post_at_exhibia(user, 'http://%s%s%s' 
                        % (settings.SITE, settings.MEDIA_URL, filename), exhibit.item.name)