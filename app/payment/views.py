import json
from account.models import Address, Coupon
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import settings
from exhibit.models import Item, Fund, Exhibit
from payment.forms import BuyNowForm, BuyShippingForm, BuyWithBidsReturnForm
from payment.models import Transaction
from django.db.models import Count
from django.contrib import messages
import paypalrestsdk
from settings import PAYPAL_MODE, PAYPAL_SECRET, PAYPAL_CLIENT_ID, PAYPAL_BUY_NOW_RETURN_URL, \
    PAYPAL_BUY_NOW_CANCEL_URL, PAYPAL_BUY_BIDS_RETURN_URL, PAYPAL_BUY_BIDS_CANCEL_URL, \
    PAYPAL_BUY_SHIPPING_RETURN_URL, PAYPAL_BUY_SHIPPING_CANCEL_URL, REWARD_FOR_BUY, \
    PAYPAL_BUY_AND_RETURN_BIDS_RETURN_URL, PAYPAL_BUY_AND_RETURN_BIDS_CANCEL_URL
from websocket.views import websocket_api
from utils.facebook_posts import facebook_public_post


@csrf_exempt
def append_buy_now_form(request):
    if request.user.is_authenticated():
        item = get_object_or_404(Item, pk=request.GET.get('item_pk'))
        transaction = Transaction()
        transaction.item = item
        transaction.user = request.user
        form = BuyNowForm(instance=transaction)

        return render(request, 'payment/modal_buy_now.html', {'item': item, 'form': form})
    else:
        return HttpResponse('')


@login_required
@csrf_exempt
def append_buy_shipping_form(request):
    exhibit = get_object_or_404(Exhibit, pk=request.GET.get('exhibit_id'), last_bidder_member=request.user)
    transaction = Transaction()
    transaction.exhibit = exhibit
    transaction.user = request.user
    form = BuyShippingForm(instance=transaction)

    return render(request, 'payment/modal_buy_shipping.html', {'exhibit': exhibit, 'form': form})


@login_required
@csrf_exempt
def append_bids_return_form(request):

    try:
        exhibit = Exhibit.objects.ended()\
            .exclude(last_bidder_member=request.user) \
            .exclude(id__in=[payment.exhibit_id for payment in request.user.payments.processing_item_transaction().all() if payment.exhibit_id]) \
            .extra(select={'refund_time_left': 'FLOOR({}-(UNIX_TIMESTAMP()-ended_unixtime))'.format(settings.BID_REFUND_TIME)}) \
            .extra(where=['UNIX_TIMESTAMP() - ended_unixtime < {}'.format(settings.BID_REFUND_TIME)]) \
            .annotate(bid_refund=Count('id')) \
            .select_related('item') \
            .get(bids__user=request.user, id=request.GET.get('exhibit_id'))
    except Exhibit.DoesNotExist:
        raise Http404

    transaction = Transaction()
    transaction.exhibit = exhibit
    transaction.user = request.user
    form = BuyWithBidsReturnForm(instance=transaction)

    return render(request, 'payment/modal_buy_and_return_bids.html', {'exhibit': exhibit, 'form': form})


@login_required
@require_POST
def buy_now(request):
    transaction = Transaction(user=request.user, ip=request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR'))
    form = BuyNowForm(request.POST, instance=transaction)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.type = 'buy_item'
        transaction.amount = transaction.item.price

        if transaction.shipping_method == 'standard':
            transaction.amount += transaction.item.standard_shipping_price
        else:
            transaction.amount += transaction.item.priority_shipping_price

        transaction.save()

        if transaction.payment_method == 'paypal':

            paypalrestsdk.configure({
                'mode': PAYPAL_MODE,
                'client_id': PAYPAL_CLIENT_ID,
                'client_secret': PAYPAL_SECRET
            })

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "redirect_urls": {
                    "return_url": PAYPAL_BUY_NOW_RETURN_URL,
                    "cancel_url": PAYPAL_BUY_NOW_CANCEL_URL
                },

                "payer": {
                    "payment_method": "paypal",
                },
                "transactions": [{
                    "item_list":
                    {
                        "items":
                        [
                            {
                                "name": transaction.item.name,
                                "sku": transaction.item.code,
                                "price": str(transaction.item.price),
                                "currency": "USD",
                                "quantity": 1
                            },
                            {
                                "name": "Shipping",
                                "sku": transaction.shipping_method,
                                "price": str(transaction.amount - transaction.item.price),
                                "currency": "USD",
                                "quantity": 1
                            },
                        ]
                    },
                    "amount":
                    {
                        "total": str(transaction.amount),
                        "currency": "USD"
                    },
                    "description": "This is the payment transaction description."
                    }
                ]})

            if payment.create():
                print("Payment %s created successfully" % payment.id)
                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = link.href
                        print("Redirect for approval: %s" % redirect_url)
                        request.user.last_payment_id = payment.id
                        request.user.last_transaction_id = transaction.id
                        request.user.save()
                        # can't make here direct redirect or redirect via js 'next' due to facebook
                        callback_js = "$('#buy-now-form').attr('action', '%s'); " \
                                      "$('#buy-now').removeClass('ajax-submit');" \
                                      "$('#buy-now').text('redirecting...');" \
                                      "$('#buy-now').attr('type', 'submit');" \
                                      "$('#buy-now').click();" % redirect_url

                        return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))
            else:
                print(payment.error)
            # return HttpResponse(json.dumps({'result': 'success', 'next': '/checkout/review/{}/'.format(order.id)}))
        else:
            pass
    else:
        print form._errors
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]
        print response
        return HttpResponse(json.dumps({'response': response, 'result': 'error'}))


@login_required
@require_POST
def buy_and_return_bids(request):
    transaction = Transaction(user=request.user, ip=request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR'))
    form = BuyWithBidsReturnForm(request.POST, instance=transaction)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.type = 'buy_item_return_bids'
        transaction.amount = transaction.exhibit.item.price

        if transaction.shipping_method == 'standard':
            transaction.amount += transaction.exhibit.item.standard_shipping_price
        else:
            transaction.amount += transaction.exhibit.item.priority_shipping_price

        transaction.save()

        if transaction.payment_method == 'paypal':

            paypalrestsdk.configure({
                'mode': PAYPAL_MODE,
                'client_id': PAYPAL_CLIENT_ID,
                'client_secret': PAYPAL_SECRET
            })

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "redirect_urls": {
                    "return_url": PAYPAL_BUY_AND_RETURN_BIDS_RETURN_URL,
                    "cancel_url": PAYPAL_BUY_AND_RETURN_BIDS_CANCEL_URL,
                },

                "payer": {
                    "payment_method": "paypal",
                },
                "transactions": [{
                    "item_list":
                    {
                        "items":
                        [
                            {
                                "name": 'Returned bids',
                                "sku": 'bonus bids',
                                "price": 0,
                                "currency": "USD",
                                "quantity": transaction.exhibit.bids.filter(user=request.user).count(),
                            },
                            {
                                "name": transaction.exhibit.item.name,
                                "sku": transaction.exhibit.item.code,
                                "price": str(transaction.exhibit.item.price),
                                "currency": "USD",
                                "quantity": 1
                            },
                            {
                                "name": "Shipping",
                                "sku": transaction.shipping_method,
                                "price": str(transaction.amount - transaction.exhibit.item.price),
                                "currency": "USD",
                                "quantity": 1
                            },
                        ]
                    },
                    "amount":
                    {
                        "total": str(transaction.amount),
                        "currency": "USD"
                    },
                    "description": "This is the payment transaction description."
                    }
                ]})

            if payment.create():
                print("Payment %s created successfully" % payment.id)
                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = link.href
                        print("Redirect for approval: %s" % redirect_url)
                        request.user.last_payment_id = payment.id
                        request.user.last_transaction_id = transaction.id
                        request.user.save()
                        # can't make here direct redirect or redirect via js 'next' due to facebook
                        callback_js = "$('#buy-and-return-bids-form').attr('action', '%s'); " \
                                      "$('#buy-and-return-bids').removeClass('ajax-submit');" \
                                      "$('#buy-and-return-bids').text('redirecting...');" \
                                      "$('#buy-and-return-bids').attr('type', 'submit');" \
                                      "$('#buy-and-return-bids').click();" % redirect_url
                        return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))
            else:
                print(payment.error)
        else:
            pass
    else:
        print form._errors
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]
        print response
        return HttpResponse(json.dumps({'response': response, 'result': 'error'}))


@login_required
def buy_now_paypal(request):

    cancel = request.GET.get('cancel', False)

    if cancel:
        Transaction.objects.filter(pk=request.user.last_transaction_id).update(status='fail')
        messages.add_message(request, messages.ERROR, 'Payment was canceled')
        return HttpResponseRedirect('/')

    transaction = get_object_or_404(Transaction, pk=request.user.last_transaction_id)
    payment_id = request.user.last_payment_id

    success = request.GET.get('success', False)

    if success:
        payer_id = request.GET.get('PayerID', False)
        paypalrestsdk.configure({
            'mode': PAYPAL_MODE,
            'client_id': PAYPAL_CLIENT_ID,
            'client_secret': PAYPAL_SECRET
        })

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            transaction.status = 'paid'
            transaction.payment_id = payment.id
            transaction.payment_payer_id = payer_id
            transaction.payment_token = request.GET.get('token', False)

            shipping_address, created = Address.objects.get_or_create(
                user=request.user,
                type='shipping',
                first_name=payment.payer.payer_info.first_name,
                last_name=payment.payer.payer_info.last_name,
                address=payment.payer.payer_info.shipping_address.line1 + str(payment.payer.payer_info.shipping_address.line2),
                state=payment.payer.payer_info.shipping_address.state,
                city=payment.payer.payer_info.shipping_address.city,
                postal_code=payment.payer.payer_info.shipping_address.postal_code,
                country=payment.payer.payer_info.shipping_address.country_code,
            )
            transaction.shipping_address = shipping_address

            transaction.save()
            print("Payment[%s] execute successfully" % payment.id)

            # TODO item buy msg
            if request.user.is_facebook_verified():
                item_url = 'http://%s/exhibit/%s/%s/%s/' % (settings.SITE, transaction.item.categories.all()[0].slug,
                                                            transaction.item.brand.slug, transaction.item.slug)
                facebook_public_post(request.user, 'buy', item_url)

            messages.add_message(request, messages.SUCCESS, 'Payment was successfully created')
            request.user.points += REWARD_FOR_BUY
            funding_credits = transaction.item.funding_credits
            if funding_credits:
                request.user.funding_credits += funding_credits

            # clear payment and transaction fields
            request.user.last_transaction_id = request.user.last_payment_id = None

            request.user.save()
            return redirect('orders_list')
        else:
            print(payment.error)
            messages.add_message(request, messages.ERROR, 'Payment was not created')
            return HttpResponseRedirect('/')
    else:
        return HttpResponse('/')


@login_required
def buy_and_return_bids_paypal(request):

    cancel = request.GET.get('cancel', False)

    if cancel:
        Transaction.objects.filter(pk=request.user.last_transaction_id).update(status='fail')
        messages.add_message(request, messages.ERROR, 'Payment was canceled')
        return HttpResponseRedirect('/')

    transaction = get_object_or_404(Transaction, pk=request.user.last_transaction_id)
    payment_id = request.user.get.last_payment_id

    success = request.GET.get('success', False)

    if success:
        payer_id = request.GET.get('PayerID', False)
        paypalrestsdk.configure({
            'mode': PAYPAL_MODE,
            'client_id': PAYPAL_CLIENT_ID,
            'client_secret': PAYPAL_SECRET
        })

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            transaction.status = 'paid'
            transaction.payment_id = payment.id
            transaction.payment_payer_id = payer_id
            transaction.payment_token = request.GET.get('token', False)

            shipping_address, created = Address.objects.get_or_create(
                user=request.user,
                type='shipping',
                first_name=payment.payer.payer_info.first_name,
                last_name=payment.payer.payer_info.last_name,
                address=payment.payer.payer_info.shipping_address.line1 + str(payment.payer.payer_info.shipping_address.line2),
                state=payment.payer.payer_info.shipping_address.state,
                city=payment.payer.payer_info.shipping_address.city,
                postal_code=payment.payer.payer_info.shipping_address.postal_code,
                country=payment.payer.payer_info.shipping_address.country_code,
            )
            transaction.shipping_address = shipping_address

            transaction.save()
            print("Payment[%s] execute successfully" % payment.id)
            messages.add_message(request, messages.SUCCESS, 'Payment was successfully created')
            request.user.points += REWARD_FOR_BUY
            request.user.bonus_bids += transaction.exhibit.bids.filter(user=request.user).count()
            funding_credits = transaction.exhibit.item.funding_credits
            if funding_credits:
                request.user.funding_credits += funding_credits

            # clear payment and transaction fields
            request.user.last_transaction_id = request.user.last_payment_id = None

            request.user.save()
            return redirect('orders_list')
        else:
            print(payment.error)
            messages.add_message(request, messages.ERROR, 'Payment was not created')
            return HttpResponseRedirect('/')
    else:
        return HttpResponse('/')


@login_required
def buy_shipping_paypal(request):
    try:
        cancel = request.GET.get('cancel', False)

        if cancel:
            Transaction.objects.filter(pk=request.user.last_transaction_id).update(status='fail')
            messages.add_message(request, messages.ERROR, 'Payment was canceled')
            return HttpResponseRedirect('/')

        transaction = get_object_or_404(Transaction, pk=request.user.last_transaction_id)
        payment_id = request.user.last_payment_id

        success = request.GET.get('success', False)

        if success:
            payer_id = request.GET.get('PayerID', False)
            paypalrestsdk.configure({
                'mode': PAYPAL_MODE,
                'client_id': PAYPAL_CLIENT_ID,
                'client_secret': PAYPAL_SECRET
            })

            payment = paypalrestsdk.Payment.find(payment_id)

            if payment.execute({"payer_id": payer_id}):
                transaction.status = 'paid'
                transaction.payment_id = payment.id
                transaction.payment_payer_id = payer_id
                transaction.payment_token = request.GET.get('token', False)

                shipping_address, created = Address.objects.get_or_create(
                    user=request.user,
                    type='shipping',
                    first_name=payment.payer.payer_info.first_name,
                    last_name=payment.payer.payer_info.last_name,
                    address=payment.payer.payer_info.shipping_address.line1 + str(payment.payer.payer_info.shipping_address.line2),
                    state=payment.payer.payer_info.shipping_address.state,
                    city=payment.payer.payer_info.shipping_address.city,
                    postal_code=payment.payer.payer_info.shipping_address.postal_code,
                    country=payment.payer.payer_info.shipping_address.country_code,
                )

                transaction.shipping_address = shipping_address

                transaction.save()
                print("Payment[%s] execute successfully" % payment.id)
                messages.add_message(request, messages.SUCCESS, 'Payment was successfully created')
                request.user.points += REWARD_FOR_BUY
                funding_credits = transaction.exhibit.item.funding_credits
                if funding_credits:
                    request.user.funding_credits += funding_credits

                # clear payment and transaction fields
                request.user.last_transaction_id = request.user.last_payment_id = None

                request.user.save()
                return redirect('orders_list')
            else:
                print(payment.error)
                messages.add_message(request, messages.ERROR, 'Payment was not created')
                return HttpResponse('/')
        else:
            return HttpResponse('/')
    except Exception as e:
        with open("/var/www/exhibia/payment_log.txt", 'wb+') as f:
            f.write(e)
        messages.add_message(request, messages.ERROR, 'Payment was not created')
        return HttpResponse('/')


@login_required
@require_POST
def buy_bids(request):

    bids_cost = int(request.POST.get('bids_cost', 0))
    exhibit_pk = int(request.POST.get('exhibit_id', 0))
    coupon_code = int(request.POST.get('coupon_code_hidden', 0) or 0)
    coupon = None
    amount_for_fund = bids_cost
    use_funding_credits = request.POST.get('use_funding_credits')

    # if was used funding credits snd all ok with don't redirect to paypal
    if use_funding_credits:
        try:
            funding_credits = int(request.POST.get('funding_credits', 0))
        except ValueError:
            return HttpResponse(json.dumps(dict(result='error',
                                                response={'funding_credits': 'funding amount is not valid'})))

        if funding_credits > request.user.funding_credits:
            return HttpResponse(json.dumps(dict(result='error', response={'funding_credits': 'not enough funding credits'})))

        exhibit = Exhibit.objects.get(pk=exhibit_pk)
        exhibit.bonus_fund(request.user, funding_credits)
        request.user.save()
        websocket_api(action='FUND_ITEM', params=exhibit_pk, request=request)
        return HttpResponse(json.dumps({'result': 'success'}))

    if coupon_code:
        try:
            coupon = Coupon.objects.get(pk=coupon_code)
        except (Coupon.DoesNotExist, ValueError):
            return HttpResponse(json.dumps(dict(result='error',
                                                response={'coupon_code_hidden': 'wrong code'})))

        if coupon.is_expired():
            return HttpResponse(json.dumps(dict(result='error',
                                                response={'coupon_code_hidden': 'coupon is expired'})))

        if coupon.is_already_used_by(request.user):
            return HttpResponse(json.dumps(dict(result='error',
                                                response={'coupon_code_hidden': 'coupon code can be used only once'})))

        if coupon.min_package_amount and coupon.min_package_amount > bids_cost:
            return HttpResponse(json.dumps(dict(
                result='error',
                response={'coupon_code_hidden': 'coupon can be used only for $%s and more packages' % coupon.min_package_amount}
            )))

        amount_for_fund = bids_cost * coupon.funding_percent / 100

    if not bids_cost or not exhibit_pk:
        return HttpResponse(json.dumps({'result': 'error'}))

    bids_number = Fund.get_bids_count_by_cost(bids_cost, coupon)

    transaction = Transaction(user=request.user,
                              amount=bids_cost,
                              type='buy_bids',
                              coupon=coupon,
                              amount_for_fund=amount_for_fund,
                              ip=request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR'),
                              exhibit_id=exhibit_pk)

    transaction.save()

    if transaction.payment_method == 'paypal':

        paypalrestsdk.configure({
            'mode': PAYPAL_MODE,
            'client_id': PAYPAL_CLIENT_ID,
            'client_secret': PAYPAL_SECRET
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "redirect_urls": {
                "return_url": PAYPAL_BUY_BIDS_RETURN_URL,
                "cancel_url": PAYPAL_BUY_BIDS_CANCEL_URL
            },

            "payer": {
                "payment_method": "paypal",
            },
            "transactions": [{
                "item_list":
                {
                    "items":
                    [
                        {
                            "name": '%s bids' % bids_number,
                            "sku": '%s bids' % bids_number,
                            "price": str(bids_cost),
                            "currency": "USD",
                            "quantity": 1
                        },
                    ]
                },
                "amount":
                {
                    "total": str(bids_cost),
                    "currency": "USD"
                },
                "description": "This is the payment transaction description."
                }
            ]})

        if payment.create():
            print("Payment %s created successfully" % payment.id)
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = link.href
                    print("Redirect for approval: %s" % redirect_url)
                    request.user.last_payment_id = payment.id
                    request.user.last_transaction_id = transaction.id
                    request.user.save()
                    # can't make here direct redirect or redirect via js 'next' due to facebook
                    callback_js = "$('#fund-exhibit-form').attr('action', '%s'); " \
                                  "$('#fund-exhibit').removeClass('ajax-submit');" \
                                  "$('#fund-exhibit').text('redirecting...');" \
                                  "$('#fund-exhibit').attr('type', 'submit');" \
                                  "$('#fund-exhibit').click();" % redirect_url
                    return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))
        else:
            print(payment.error)
            return HttpResponseRedirect('/')

        # return HttpResponse(json.dumps({'result': 'success', 'next': '/checkout/review/{}/'.format(order.id)}))
    else:
        pass


@login_required
def buy_bids_paypal(request):

    cancel = request.GET.get('cancel', False)

    if cancel:
        Transaction.objects.filter(pk=request.user.last_transaction_id).update(status='fail')
        messages.add_message(request, messages.ERROR, 'Payment was canceled')
        return HttpResponseRedirect('/')

    success = request.GET.get('success', False)

    if success:
        payer_id = request.GET.get('PayerID', False)
        paypalrestsdk.configure({
            'mode': PAYPAL_MODE,
            'client_id': PAYPAL_CLIENT_ID,
            'client_secret': PAYPAL_SECRET
        })

        payment_id = request.user.last_payment_id
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):

            transaction = get_object_or_404(Transaction, pk=request.user.last_transaction_id)
            transaction.status = 'paid'
            transaction.payment_id = payment.id
            transaction.payment_payer_id = payer_id
            transaction.payment_token = request.GET.get('token', False)

            shipping_address, created = Address.objects.get_or_create(
                user=request.user,
                type='shipping',
                first_name=payment.payer.payer_info.first_name,
                last_name=payment.payer.payer_info.last_name,
                address=payment.payer.payer_info.shipping_address.line1 + str(payment.payer.payer_info.shipping_address.line2),
                state=payment.payer.payer_info.shipping_address.state,
                city=payment.payer.payer_info.shipping_address.city,
                postal_code=payment.payer.payer_info.shipping_address.postal_code,
                country=payment.payer.payer_info.shipping_address.country_code,
            )

            transaction.shipping_address = shipping_address
            transaction.save()
            transaction.exhibit.fund(transaction.user, transaction.amount_for_fund)
            transaction.user.points += REWARD_FOR_BUY

            # clear payment and transaction fields
            transaction.user.last_transaction_id = transaction.user.last_payment_id = None
            transaction.user.save()
            websocket_api(action='FUND_ITEM', params=transaction.exhibit_id, request=request)
            print("Payment[%s] execute successfully" % payment.id)

            # TODO fund massage
            if request.user.is_facebook_verified():
                # TODO reverse to item_page
                item_url = 'http://%s/exhibit/%s/%s/%s/' % (settings.SITE, transaction.get_item().categories.all()[0].slug,
                                                            transaction.get_item().brand.slug, transaction.get_item().slug)
                facebook_public_post(request.user, 'fund', item_url)

            messages.add_message(request, messages.SUCCESS, 'Payment was successfully created')
            

            return HttpResponseRedirect('/')

        else:
            print(payment.error)
            messages.add_message(request, messages.ERROR, 'Payment was not created')
            return HttpResponse('/')
    else:
        return HttpResponse('/')


@login_required
@require_POST
def buy_shipping(request):

    transaction = Transaction(user=request.user, ip=request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR'))
    form = BuyShippingForm(request.POST, instance=transaction)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.type = 'buy_shipping'

        if transaction.shipping_method == 'standard':
            transaction.amount = transaction.exhibit.item.standard_shipping_price
        else:
            transaction.amount = transaction.exhibit.item.priority_shipping_price

        transaction.save()

        if transaction.payment_method == 'paypal':

            paypalrestsdk.configure({
                'mode': PAYPAL_MODE,
                'client_id': PAYPAL_CLIENT_ID,
                'client_secret': PAYPAL_SECRET
            })

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "redirect_urls": {
                    "return_url": PAYPAL_BUY_SHIPPING_RETURN_URL,
                    "cancel_url": PAYPAL_BUY_SHIPPING_CANCEL_URL,
                },

                "payer": {
                    "payment_method": "paypal",
                },
                "transactions": [{
                    "item_list":
                    {
                        "items":
                        [
                            {
                                "name": transaction.exhibit.item.name,
                                "sku": transaction.exhibit.item.code,
                                "price": 0,
                                "currency": "USD",
                                "quantity": 1
                            },
                            {
                                "name": "Shipping",
                                "sku": transaction.shipping_method,
                                "price": str(transaction.amount),
                                "currency": "USD",
                                "quantity": 1
                            },
                        ]
                    },
                    "amount":
                    {
                        "total": str(transaction.amount),
                        "currency": "USD"
                    },
                    "description": "This is the payment transaction description."
                    }
                ]})

            if payment.create():
                print("Payment %s created successfully" % payment.id)
                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = link.href
                        print("Redirect for approval: %s" % redirect_url)
                        request.user.last_payment_id = payment.id
                        request.user.last_transaction_id = transaction.id
                        request.user.save()
                        # can't make here direct redirect or redirect via js 'next' due to facebook
                        callback_js = "$('#buy-shipping-form').attr('action', '%s'); " \
                                      "$('#buy-shipping').removeClass('ajax-submit');" \
                                      "$('#buy-shipping').text('redirecting...');" \
                                      "$('#buy-shipping').attr('type', 'submit');" \
                                      "$('#buy-shipping').click();" % redirect_url
                        return HttpResponse(json.dumps({'result': 'success', 'callback_js': callback_js}))
            else:
                print(payment.error)
                # transaction
            # return HttpResponse(json.dumps({'result': 'success', 'next': '/checkout/review/{}/'.format(order.id)}))
        else:
            pass
    else:
        print form._errors
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]
        print response
        return HttpResponse(json.dumps({'response': response, 'result': 'error'}))


@login_required
@require_POST
@csrf_exempt
def cancel_order(request):
    try:
        print request.POST.get('transaction_id')
        Transaction.objects\
            .deletable()\
            .get(user=request.user, pk=request.POST.get('transaction_id'))\
            .delete()
    except Transaction.DoesNotExist:
        return HttpResponse(json.dumps({'result': 'error'}))

    return HttpResponse(json.dumps({'result': 'success', 'next': reverse('orders_list')}))
