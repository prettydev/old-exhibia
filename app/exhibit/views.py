from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from exhibit.models import Exhibit, ItemCategory, Item
from django.db.models import Count
import pymongo
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from websocket.views import websocket_api
from time import time
from django.core.cache import cache
import json
import settings


@xframe_options_exempt
def facebook_app_page(request):
    ids = request.GET.get('request_ids')
    print ids
    if ids:
        pass
    return index(request)


@xframe_options_exempt
@csrf_exempt
def index(request):

    funding_exhibits = Exhibit.objects.funding() | Exhibit.objects.full_fund_pause()

    try:
        funding_exhibits = funding_exhibits.select_related('item')\
            .filter(item__categories=ItemCategory.objects.order_by('sort')[0])\
            .order_by('-amount_funded')
    except IndexError:
        funding_exhibits = None

    bidding_exhibits = Exhibit.objects.bidding() \
                    | Exhibit.objects.after_win_pause() \
                    | Exhibit.objects.paused() \
                    | Exhibit.objects.auto_paused_last() \
                    | Exhibit.objects.relisted()

    bidding_exhibits = bidding_exhibits.exclude(in_queue=True)\
        .select_related('item')\
        .select_related('last_bidder_member')

    # we need to display giveaways at 4 and 5 bidding positions
    bidding_exhibits_giveaways = list(bidding_exhibits.filter(item__giveaway=True))
    bidding_exhibits_non_giveaways = list(bidding_exhibits.exclude(item__giveaway=True))

    if len(bidding_exhibits_non_giveaways) > 3:
        bidding_exhibits =  bidding_exhibits_non_giveaways[:3] \
            + bidding_exhibits_giveaways \
            + bidding_exhibits_non_giveaways[3:]
    else:
        bidding_exhibits = bidding_exhibits_non_giveaways + bidding_exhibits_giveaways

    win_limit_time_left = (
        request.user.win_limit_time_left
    ) if request.user.is_authenticated() and request.user.is_on_win_limit() else None

    categories = ItemCategory.objects.order_by('sort')

    # get last 15 chat messages from MongoDB
    connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
    db = getattr(connection, settings.MONGODB['NAME'])
    chat_messages = list(db.chat.find().sort("date", pymongo.DESCENDING).limit(15))
    chat_messages.reverse()

    # chat state from mongo dynamic settings
    guest_chat_state = db.settings.find_one({'name': 'GUEST_CHAT_STATE'})
    guest_chat_state = guest_chat_state.get('status', 1) if guest_chat_state else 1
    
    # temporary disable small bidding templates
    # if bidding_exhibits.count() > settings.MAX_AUCTIONS_BIG_TEMPLATES_COUNT or request.mobile:
    #     bidding_exhibits_template = 'exhibit/bidding_box_small.html'
    # 	  bidding_exhibits_refund_template = 'exhibit/bidding_refund_box_small.html'
    #     mobile_version = 1
    # else:
    #     bidding_exhibits_template = 'exhibit/bidding_box.html'
    #     bidding_exhibits_refund_template = 'exhibit/bidding_refund_box.html'
    #     mobile_version = 0
    mobile_version = 0
    bidding_exhibits_template = 'exhibit/bidding_box.html'

    return render(request, 'exhibit/index.html', {'funding_exhibits': funding_exhibits,
                                                  'bidding_exhibits': bidding_exhibits,
                                                  'categories': categories,
                                                  'chat_messages': chat_messages,
                                                  'win_limit_time_left': win_limit_time_left,
                                                  'bidding_exhibits_template': bidding_exhibits_template,
                                                  # 'bidding_exhibits_refund_template': bidding_exhibits_refund_template,
                                                  'mobile_version': mobile_version,
                                                  'guest_chat_state': guest_chat_state,
                                                  })


def append_funding_carousel(request):
    category_id = request.GET.get('category_id')
    funding_exhibits = Exhibit.objects.funding() | Exhibit.objects.full_fund_pause()
    funding_exhibits = funding_exhibits.filter(item__categories=category_id).order_by('-amount_funded')

    if not funding_exhibits:
        return HttpResponse('')

    return render(request, 'exhibit/funding_carousel.html', {'funding_exhibits': funding_exhibits,
                                                             'category_id': category_id
                                                             })


def append_item_page(request):

    item = get_object_or_404(Item, pk=request.GET.get('item_pk'))
    return render(request, 'exhibit/modal_item_page.html', {'item': item})


def item_page(request, category_slug, brand_slug, item_slug):
    """
    Returns bidding page, funding page ot won item page for item
    """
    try:
        item = Item.objects.get(slug=item_slug)
    except Item.DoesNotExist:
        raise Http404

    # templates:
        # bidding template: chat, modal battle
        # funding template: chat, progress bar
        # won page: chat? modal battle for won

    return render(request, 'exhibit/item_page.html', {'item': item, 'app_id': settings.api.SOCIAL_AUTH_FACEBOOK_KEY,
                                                      'url': request.get_full_path(), 'site': settings.app.SITE})


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def admin_timer_drop_tool(request):

    exhibit_id = request.POST.get('exhibit_id')
    new_time = int(request.POST.get('new_time'))
    exhibit = get_object_or_404(Exhibit, pk=exhibit_id)

    if exhibit.is_ended():
        return HttpResponse('')

    # pause exhibit
    exhibit.status = 'paused'
    exhibit.paused_unixtime = time()
    exhibit.new_bidding_time = new_time
    exhibit.save()

    # set to new_time variable view text from amount of seconds
    for k, v in exhibit.NEW_BIDDING_TIME_CHOICES:
        if k == new_time:
            new_time = v
            break

    # display message to users that timer was dropped by admin
    websocket_api(action='EXHIBIT_TIMER_DROPPED', params=dict(item_name=exhibit.item.name,
                                                              exhibit_id=exhibit.id,
                                                              new_time=new_time),
                  request=request),

    return HttpResponse('ok')


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def pause_all_exhibits(request):
    # get MongoDD settings collections and update PAUSE_ALL_EXHIBITS status
    connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
    db = getattr(connection, settings.MONGODB['NAME'])
    db.settings.update({"name": "PAUSE_ALL_EXHIBITS"}, {"$set": {"status": True}}, True)

    return HttpResponse(json.dumps(dict(result='success')))


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def unpause_all_exhibits(request):
    for exhibit in Exhibit.objects.bidding().exclude(ended_unixtime__isnull=True):
        exhibit.ended_unixtime = time() + exhibit.bidding_time
        exhibit.save()

    # get MongoDD settings collections and update PAUSE_ALL_EXHIBITS status
    connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
    db = getattr(connection, settings.MONGODB['NAME'])
    db.settings.update({"name": "PAUSE_ALL_EXHIBITS"}, {"$set": {"status": False}}, True)

    return HttpResponse(json.dumps(dict(result='success')))


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def toogle_guest_chat(request):
    # get MongoDD settings collections and update GUEST_CHAT_BLOCKED status
    status = int(request.POST.get('status', 1))
    connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
    db = getattr(connection, settings.MONGODB['NAME'])
    db.settings.update({"name": "GUEST_CHAT_STATE"}, {"$set": {"status": 1 - status}}, True)

    return HttpResponse(json.dumps(dict(result='success')))


# Dummy page for tracking new users
def tracking_code(request):

    service_provider_to_template = {
        'facebook': 'tracking_code_fb.html',
    }

    service_provider = request.GET.get('service_provider')

    if not service_provider:
        raise Http404

    template = 'exhibit/%s' % service_provider_to_template[service_provider]

    return render(request, template)

