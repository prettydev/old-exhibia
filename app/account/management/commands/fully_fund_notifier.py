import urllib, urllib2, settings
from mailqueue.models import MailerMessage
import twilio
from account.models import Profile, SmsMessage
from django.core.management.base import BaseCommand, CommandError
from time import time
from exhibit.models import Exhibit
from twilio.rest import TwilioRestClient


class Command(BaseCommand):
    help = 'Notify all users via facebook/email/sms that some item was fully funded'
    # create public log directory /var/log/exhibia
    # add this one to crontab

    def handle(self, *args, **options):
        # get all fresh funded exhibits
        exhibits = Exhibit.objects.full_fund_pause().filter(funded_unixtime__gte=time() - 5 * 60)
        users = Profile.objects.all()
        for exhibit in exhibits:
            # send email
            message = 'Item "%s" was fully funded. Bidding will be opened in few minutes. ' \
                      'Join the bidding at http://www.exhibia.com' % exhibit.item.name

            params = {
                'access_token': settings.FACEBOOK_APP_TOKEN,
                'template': message,
                'href': '#'
            }

            for user in users:

                if user.email:
                    email = MailerMessage()
                    email.subject = 'Bidding Alert'
                    email.from_address = settings.DEFAULT_FROM_EMAIL
                    email.html_content = message
                    email.to_address = user.email
                    try:
                        email.save()
                    except Exception as e:
                        self.stdout.write('Can\'t send email to %s %s' % (email.to_address, e))

                # check if user have fb accociation
                if user.is_facebook_verified():
                    try:
                        req = urllib2.Request(
                            "https://graph.facebook.com/%s/notifications" % user.social_auth.filter(provider='facebook')[0].uid,
                            urllib.urlencode(params), {})
                        urllib2.urlopen(req).read()
                    except (urllib2.HTTPError, KeyError) as error_message:
                        self.stdout.write('FAcebook error while sending message to user %s %s' % (user.username, error_message))

                if user.phone:
                    sms = SmsMessage()
                    client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                    try:
                        client.sms.messages.create(body=message,
                                                   to=user.phone,
                                                   from_=settings.FROM_NUMBER)
                    except twilio.TwilioRestException as error_message:
                        sms.status = 'error'
                        sms.error_message = str(error_message)[:500]
                        self.stdout.write('TwilioRestExceptionr for user %s %s' % (user.username, error_message))
                    else:
                        sms.status = 'success'

                    sms.save()
