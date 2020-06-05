# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os
from account.classes import ImageUploader
from account.forms import AddressForm, EmailVerificationForm, PhoneVerificationForm
from account.models import ProfileItemNotification, Address, Profile, VerificationProfile, SmsMessage, IpAddress, Coupon
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core import exceptions
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from exhibit.models import Item, Exhibit
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from payment.models import Transaction
import settings
from mailqueue.models import MailerMessage
import twilio
from twilio.rest import TwilioRestClient
from websocket.views import websocket_api
from django.contrib.auth.signals import user_logged_in


def save_ip_after_login(sender, user, request, **kwargs):
    """
    save user IP when he logged in
    """

    ip_address = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')

    # update last login for address if exists
    address, created = IpAddress.objects.get_or_create(ip_address=ip_address, user=user)
    address.last_login = datetime.now()
    address.save()

user_logged_in.connect(save_ip_after_login)


def append_item_wishlist(request):

    if not request.user.is_authenticated():
        return HttpResponse('')

    item_pk = request.GET.get('item_pk')
    notifications = ProfileItemNotification.objects.filter(user=request.user, item=item_pk)
    choosen = [notification.type for notification in notifications]

    return render(request, 'account/modal_wishlist.html', {'types': ProfileItemNotification.NOTIFICATION_CHOICES,
                                                           'choosen': choosen,
                                                           'item_pk': item_pk})


def update_item_wishlist(request):

    item_pk = request.POST.get('item_pk')
    types = request.POST.getlist('types')
    item = Item.objects.get(pk=item_pk)

    # remove old notifications
    ProfileItemNotification.objects.filter(user=request.user, item=item).delete()

    # create new ones
    for type in types:
        ProfileItemNotification.objects.create(user=request.user,
                                               item=item,
                                               type=type)

    callback_js = "$('#ModalWishList').modal('hide');"

    return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))


@login_required
def address_edit(request, type, id=None):

    # NOT USING FOR NOW
    # TODO need to discuss how this form should looks like
    if id:
        address = get_object_or_404(Address, pk=id)
    else:
        address = Address(type=type, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Address was successfully saved')
            return HttpResponse(json.dumps({'result': 'success', 'next': '/'}))
        else:
            response = {}
            for k in form.errors:
                response[k] = form.errors[k][0]

            return HttpResponse(json.dumps({'response': response, 'result': 'error'}))
    else:
        form = AddressForm(instance=address)

    return render(request, 'account/edit_address.html', {'form': form, 'type': type})


@login_required
def social_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def append_verification_popup(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return HttpResponse('not verified')

    response = ''

    user = Profile.objects.get(pk=user_id)

    response = render_to_string('account/verifications.html', {'user': user}, context_instance=RequestContext(request)).strip()

    if response == '':
        response = 'not verified'

    return HttpResponse(response)


@login_required
def orders_list(request):

    # get all won exhibits by user, which aren't in payments yet
    won_exhibits = Exhibit.objects.ended_but_not_paid()\
        .filter(last_bidder_member=request.user) \
        .exclude(payments__in=Transaction.objects
                 .filter(user=request.user)
                 .filter(type='buy_shipping')
                 .exclude(status__in=['new', 'fail'])) \
        .extra(select={'won_date': 'FROM_UNIXTIME(ended_unixtime)'})

    processing_payments = Transaction.objects.processing()\
        .filter(user=request.user)\
        .order_by('-created')

    shipped_payments = Transaction.objects.shipped()\
        .filter(user=request.user)\
        .order_by('-created')

    # exhibits in which user lost, but he still can get his bids back
    exhibits_with_bid_return = (
        Exhibit.objects.ended()
        .filter(bids__user=request.user)
        .exclude(last_bidder_member=request.user)
        # if user have payment for this exhibit exclude it
        .exclude(id__in=[payment.exhibit_id for payment in request.user.payments.processing_item_transaction().all() if payment.exhibit_id])
        .extra(select={'refund_time_left': 'FLOOR({}-(UNIX_TIMESTAMP()-ended_unixtime))'.format(settings.BID_REFUND_TIME)})
        .extra(where=['UNIX_TIMESTAMP() - ended_unixtime < {}'.format(settings.BID_REFUND_TIME)])
        .annotate(bid_refund=Count('id'))
        .select_related('item')
        .order_by('refund_time_left')
        .distinct()
    )

    return render(request, 'account/orders_list.html', {'won_exhibits': won_exhibits,
                                                        'exhibits_with_bid_return': exhibits_with_bid_return,
                                                        'processing_payments': processing_payments,
                                                        'shipped_payments': shipped_payments,
                                                        })


@login_required
def change_password(request):

    if request.method == "POST":
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            callback_js = "$('#ModalChangePassword').modal('hide');"
            return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))
        else:
            response = {}
            for k in form.errors:
                response[k] = form.errors[k][0]

            return HttpResponse(json.dumps({'response': response, 'result': 'error'}))
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'account/modal_change_password.html', {'form': form})


@login_required
def change_avatar(request):

    #todo make it in normal way
    if request.method == "POST":
        image_name = request.POST.get('img')
        if image_name:
            image_path = os.path.join(settings.TEMP_MEDIA_ROOT, image_name)
            request.user.img = File(open(image_path, 'r'))
            print request.user.img
            os.unlink(image_path)
            request.user.save()
            return HttpResponse(json.dumps({'result': 'success'}))
        else:
            return HttpResponse(json.dumps({'result': 'success'}))

    return render(request, 'account/modal_change_avatar.html')


@login_required
def verify(request, verification_type):

    verification_profile = VerificationProfile.objects.create_profile(request.user, verification_type=verification_type)
    initial = dict()

    if verification_profile.is_email():

        if request.user.is_email_verified:
            return render(request, 'account/modal_already_verified.html', {'verification_type': verification_type})

        form_class = EmailVerificationForm
        form_action = reverse('verify-email')

        if request.user.email:
            initial['email'] = request.user.email

    else:

        if request.user.is_phone_verified:
            return render(request, 'account/modal_already_verified.html', {'verification_type': verification_type})

        form_class = PhoneVerificationForm
        form_action = reverse('verify-phone')

        if request.user.phone:
            initial['phone'] = request.user.phone

    if request.method == "POST":
        form = form_class(data=request.POST, instance=verification_profile)
        if form.is_valid():
            # if there were old verification entry replace its verification code and other params with the new ones
            try:
                verification_profile = VerificationProfile.objects.get(user=request.user, type=verification_type)
                verification_profile.email = form.instance.email
                verification_profile.phone = form.instance.phone
                verification_profile.verification_key = form.instance.verification_key
                verification_profile.attempts += 1
                verification_profile.save()

            except VerificationProfile.DoesNotExist:
                verification_profile = form.save()

            # don't send message if user send too many attemps
            if verification_profile.attempts > 6:
                msg = "You have exceeded your attemps. Please contact administrator"
                response = dict(phone=msg, email=msg)
                return HttpResponse(json.dumps({'response': response, 'result': 'error'}))

            # send email verification
            if verification_profile.is_email():
                subject = 'Verification email from %s' % settings.SITE
                link = reverse('verify-check-key', kwargs={'verification_key': verification_profile.verification_key})
                html_message = render_to_string('account/verification_email.txt', {'link': link, 'site': settings.SITE})
                new_message = MailerMessage()
                new_message.subject = subject
                new_message.to_address = verification_profile.email
                new_message.from_address = settings.DEFAULT_FROM_EMAIL
                new_message.html_content = html_message
                new_message.save()

            # send phone verification
            else:
                client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                sms = SmsMessage(verification=verification_profile)

                try:
                    client.sms.messages.create(body='Verification code is %s' % verification_profile.verification_key,
                                               to=verification_profile.phone,
                                               from_=settings.FROM_NUMBER)
                except twilio.TwilioRestException as error_message:
                    response = dict(phone="Can't send message. Please contact administrator")
                    sms.status = 'error'
                    sms.error_message = str(error_message)[:500]
                    sms.save()
                    return HttpResponse(json.dumps({'response': response, 'result': 'error'}))
                else:
                    sms.status = 'success'
                    sms.save()

            callback_js = "$('#ModalVerify').modal('hide');"
            return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))

        else:
            response = {}
            for k in form.errors:
                response[k] = form.errors[k][0]

            return HttpResponse(json.dumps({'response': response, 'result': 'error'}))
    else:
        form = form_class(initial=initial)

    return render(request, 'account/modal_verify.html', {'form': form, 'verification_type': verification_type, 'form_action': form_action})


@login_required
def verify_check_key(request, verification_key):
    try:
        verification_profile = VerificationProfile.objects.verify_user(request.user, verification_key, request)
    except (VerificationProfile.NotVerifedException, VerificationProfile.DoesNotExist) as e:
        messages.add_message(request, messages.ERROR, 'Verification of your profile failed')
    else:
        messages.add_message(request, messages.SUCCESS, 'You have successfully verified you %s' % verification_profile.type)

    return HttpResponseRedirect('/')


@login_required
@csrf_exempt
def upload_avatar_ajax(request):
    allowed_extension = ['.jpeg', '.jpg', '.gif', '.png']
    uploader = ImageUploader(allowed_extension)
    return HttpResponse(uploader.handle_upload(request, settings.MEDIA_ROOT + "/temp/"))


@login_required
@csrf_exempt
def remove_avatar_from_temp(request):
    if request.META["REQUEST_METHOD"] == 'DELETE':
        if request.GET.get('filename', False):
            path = os.path.join(settings.MEDIA_ROOT, u"temp", request.GET['filename'])
            print path
            if os.path.isfile(path):
                os.unlink(path)
                return HttpResponse(json.dumps(True))


@login_required
@csrf_exempt
def remove_user_avatar(request):
    request.user.img = None
    request.user.save()
    return HttpResponse(json.dumps(True))


@staff_member_required
@csrf_exempt
def ban_user(request):
    user_id = request.POST.get('user_id')
    user = Profile.objects.get(pk=user_id)
    status = 1 - int(request.POST.get('status'))
    user.is_banned = status
    user.save()

    # send message to websocket server
    websocket_api(action='UPDATE_USER_STATUS', params=dict(user_id=user_id, status=status), request=request)
    return HttpResponse('OK')


@login_required
@csrf_exempt
def check_coupon_code(request):

    try:
        coupon = Coupon.objects.get(pk=int(request.POST.get('coupon_code')))
    except (Coupon.DoesNotExist, ValueError):
        return HttpResponse(json.dumps(dict(result='error', msg='wrong code')))

    if coupon.is_expired():
        return HttpResponse(json.dumps(dict(result='error', msg='coupon is expired')))

    if coupon.is_already_used_by(request.user):
        return HttpResponse(json.dumps(dict(result='error', msg='coupon code can be used only once')))

    if coupon.is_already_used_by(request.user):
        return HttpResponse(json.dumps(dict(result='error', msg='coupon code can be used only once')))

    return HttpResponse(json.dumps(dict(result='success', msg='Success! %s coupon was accepted' % coupon.view_type())))