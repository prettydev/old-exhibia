#!/usr/bin/env python
import os
import sys
import json
import datetime
import tornado.web
import tornado.ioloop
import tornado.websocket
import pymongo
from time import time

# get project root and add it to python path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(1, PROJECT_ROOT + '/app')

# setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.conf import settings
from django.utils.importlib import import_module
from account.models import Profile
from exhibit.models import Exhibit
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count
from django.db.models import F

from utils.facebook_posts import facebook_public_post

# import Django session
session_engine = import_module(settings.SESSION_ENGINE)

# interval in ms for running notifications for clients
UPDATE_ACTIVE_USERS_COUNTER_INTERVAL = 5 * 1000
UPDATE_BIDDING_EXHIBITS_INTERVAL = 1 * 1000
MONITOR_PAUSED_EXHIBITS_INTERVAL = 3 * 1000
MONITOR_MIN_MAX_ACTIVE_EXHIBITS_INTERVAL = 3 * 1000
START_ADMIN_PAUSED_EXHIBITS_INTERVAL = 1 * 1000
DECLARE_WINNER_OR_RELIST_INTERVAL = 7 * 1000


class Guest():
    """
    Dummy class, contains default parameters for anonymous users, so we don't need to check if user exists
    every time when user post message
    """
    id = ''
    username = 'guest'
    avatar = Profile.defaul_avatar()
    # TODO enable banning by IP for anonymous users
    is_banned = False
    is_superuser = False


@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data
    """
    transaction.commit()

def debugger(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print '>>>>>>>> error occur'
            print e
            print 'error occur <<<<<<<<'
    return wrapper

class WebSocket(tornado.websocket.WebSocketHandler):
    """
    Class that handles all main real-time logic. MESSAGE_CALLBACKS associates
    action type sent from client with executed function
    """
    def open(self):
        self.application.active_users_counter += 1
        self.application.websockets_pool.append(self)
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)

        try:
            user_id = session.get("_auth_user_id")
            if not user_id:
                raise Profile.DoesNotExist
            self.user = Profile.objects.get(pk=user_id)
            # add link user => connections
            self.application.user_websockets.setdefault(self.user.id, []).append(self)
            # if admin add to admins pool
            if self.user.is_superuser:
                self.application.websockets_admins_pool.append(self)

        except (KeyError, Profile.DoesNotExist):
            self.user = Guest

    def on_message(self, message):
        message = json.loads(message)
        callback = self.MESSAGE_CALLBACKS.get(message.get('type', 'ERROR'))
        callback(self, message)

    def on_close(self, message=None):
        self.application.active_users_counter -= 1
        # remove from WebSockets pool
        for key, value in enumerate(self.application.websockets_pool):
            if value == self:
                del self.application.websockets_pool[key]
        # remove from user link
        if self.user is not Guest:
            try:
                self.application.user_websockets[self.user.id].remove(self)
            except (KeyError, ValueError):
                pass
        # remove from admin pool
        if self.user.is_superuser:
            for key, value in enumerate(self.application.websockets_admins_pool):
                if value == self:
                        del self.application.websockets_admins_pool[key]

    def on_init(self, message):
        # temporary disable small bidding templates
        # self.mobile_version = message.get('mobile_version', False)
        self.mobile_version = False

    def on_chat_message(self, message):
        """
        Callback function when some client send message
        """
        guest_chat_state = application.db.settings.find_one({'name': 'GUEST_CHAT_STATE'})
        guest_chat_state = guest_chat_state.get('status', 1) if guest_chat_state else 1
        
        if not guest_chat_state and self.user is Guest:
            message = dict(type='CHAT_BANNED')
            message['message'] = 'Chat is available only for  authorized users'
            self.ws_connection.write_message(json.dumps(message))
            return

        if self.user.is_banned:
            message = dict(type='CHAT_BANNED')
            message['message'] = 'You have been banned from chat'
            self.ws_connection.write_message(json.dumps(message))
            return

        # TODO render template, same for new messages and messages from database
        message['username'] = self.user.username
        message['user_id'] = self.user.id
        message['avatar'] = settings.MEDIA_URL + self.user.avatar

        # notify all connected clients
        for client in application.websockets_pool:
            client.ws_connection.write_message(json.dumps(message))

        # save message in MongoDB
        message.pop('type')
        message['date'] = datetime.datetime.utcnow(),
        self.application.db.chat.insert(message)

    def on_bid(self, message):
        """
        Callback function when some client makes a bid
        """
        if self.user is Guest:
            message = dict(type='CANNOT_BID')
            message['message'] = 'Please login to make a bid!'
            message['nonauthorized'] = True
            self.ws_connection.write_message(json.dumps(message))
            return

        try:
            flush_transaction()
            exhibit = Exhibit.objects.bidding().get(pk=message.get('exhibit_id'))
        except Exhibit.DoesNotExist:
            message['message'] = "Exhibit has already been ended"
            self.ws_connection.write_message(json.dumps(message))
            return

        try:
            exhibit.bid_by(self.user)

            # update profile panel and update bidder name & photo only for bidder
            message = {'type': 'SUCCESS_BID',
                       'id': exhibit.id,
                       'bidder_name': self.user.username,
                       'bidder_img': settings.MEDIA_URL + self.user.avatar,
                       'bidder_id': self.user.id,
                       'bids': self.user.bids,
                       'bonus_bids': self.user.bonus_bids,
                       'points': self.user.points,
                       'wins': self.user.wins_number}

            print 'USER %s BID EXHIBIT %s' % (self.user.id, exhibit.id)

            self.ws_connection.write_message(json.dumps(message))

            #TODO bid maked msg
            if self.user.is_facebook_verified():
                item_url = 'http://%s/exhibit/%s/%s/%s/' % (settings.SITE, exhibit.item.categories.all()[0].slug,
                                                            exhibit.item.brand.slug, exhibit.item.slug)
                facebook_public_post(self.user, 'bid', item_url)

        except Exhibit.CannotBidException as e:
            message = {'type': 'CANNOT_BID', 'message': str(e)}
            self.ws_connection.write_message(json.dumps(message))


    def on_error(self, message):
        """
        Callback function for all non-correct actions
        """
        print 'error connection: message %s' % message

    # messages from client
    MESSAGE_CALLBACKS = {
        'INIT': on_init,
        'CHAT_MESSAGE': on_chat_message,
        'BID': on_bid,
        'ERROR': on_error,
    }


class Api(tornado.web.RequestHandler):
    """
    API Class. Can communicate with all connected clients. Uses Django SECRET_KEY as security key.
    POST parameters
    :parameter secret_key
    :parameter action
    :parameter data - needed data for concrete function, can be string, json, whatever
    """
    def fund_item(self, exhibit_id):
        """
        Notificate all connected users that some exhibit was funded
        """
        exhibit = get_object_or_404(Exhibit, pk=exhibit_id)
        message = dict(type='UPDATE_FUNDING_EXHIBIT',
                       backers=exhibit.backers_count,
                       percent_funded=exhibit.percent_funded,
                       id=exhibit_id)

        # notify all connected clients
        for client in application.websockets_pool:
            client.ws_connection.write_message(json.dumps(message))

        # if item was fully funded update users which have this item in wish list
        # if exhibit.amount_funded >= exhibit.item.price:
        #     users = Profile.objects\
        #                    .filter(wishlist__item=exhibit.item)\
        #                    .distinct()
        #     for user in users:
        #         user.social_notify(exhibit)

    def update_user_status(self, data):
        """
        Update user status: banned/unbanned (for case when user objects will be keeping directly in memory)
        """
        for client in application.user_websockets.get(int(data['user_id']), []):
            client.user.is_banned = data['status']

    def exhibit_timer_dropped(self, data):
        """
        Display message that exhibit timer was dropped by admin
        """
        exhibit_id = data['exhibit_id']
        item_name = data['item_name']
        new_time = data['new_time']

        print 'ADMIN CHANGE TIMER FOR EXHIBIT %s TO %s' % (exhibit_id, new_time)

        message = dict(type='EXHIBIT_TIMER_DROPPED',
                       exhibit_id=exhibit_id,
                       new_time=new_time)

        sys_message = '"%s" timer set to %s' % (item_name, new_time)
        message.setdefault('sys_notifications', []).append(sys_message)
        # add it to mongoDB
        insert_system_notification_in_db(sys_message)

        # notify all connected clients
        for client in application.websockets_pool:
            client.ws_connection.write_message(json.dumps(message))

    def error(self, data):
        print 'api error: data %s' % data

    API_ACTIONS = {'FUND_ITEM': fund_item,
                   'UPDATE_USER_STATUS': update_user_status,
                   'EXHIBIT_TIMER_DROPPED': exhibit_timer_dropped,
                   'ERROR': error,
                   }

    def post(self, *args, **kwargs):
        """
        Handles POST requests to API
        """
        # check if received secret key is correct
        if self.get_argument('secret_key') == settings.SECRET_KEY:
            action = self.get_argument('action', default='ERROR')
            callback = self.API_ACTIONS.get(action)
            callback(self, json.loads(self.get_argument('data', default=False)))


class Application(tornado.web.Application):
    def __init__(self):
        # list of all connected clients(WebSockets)
        self.websockets_pool = list()
        self.active_users_counter = 0
        # relation between the user and his connections (it may be several tabs/connection for specific user)
        self.user_websockets = dict()
        # admin users pool (for displaying active users count)
        self.websockets_admins_pool = list()

        connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
        self.db = getattr(connection, settings.MONGODB['NAME'])

        handlers = (
            (r'/', WebSocket),
            (r'/api/', Api),
        )

        tornado.web.Application.__init__(self, handlers,  debug=settings.DEBUG)

application = Application()


def update_active_users_counter():
    """
    Update online users counter for chat (only for admin users)
    """
    message = {'type': 'UPDATE_USER_COUNTER', 'count': application.active_users_counter}

    # notify all connected clients
    for client in application.websockets_admins_pool:
       	client.ws_connection.write_message(json.dumps(message))

def update_bidding_exhibits():
    """
    Get all exhibits in status "bidding" and "paused". Changes exhibits status to "after_win_pause" if exhibit ends.
    Send exhibits information to all clients
    """
    flush_transaction()
    data = []
    # make dict object user, so we can dynamically change id for each user for all messages
    user = {'id': ''}
    message = {'type': 'UPDATE_ACTIVE_EXHIBITS', 'data': data}
    now_time = time()
    exhibits = Exhibit.objects.bidding().exclude(ended_unixtime__isnull=True)
    pause_all = application.db.settings.find_one({'name': 'PAUSE_ALL_EXHIBITS'})
    if pause_all:
        pause_all = pause_all['status']

    for exhibit in exhibits:
        info = {'id': exhibit.id}
        # check if exhibit.bidding time ends
        if exhibit.ended_unixtime <= now_time and not exhibit.is_paused() and not exhibit.is_auto_paused() and not pause_all:
            # check if we can end exhibit or need to drop timer
            # can_be_ended = exhibit.can_be_ended()
            can_extend_timer = exhibit.can_extend_timer()

            if exhibit.previous_status == 'auto_paused_last':
                exhibit.end()

                info['end'] = True
                # update winner profile panel
                winner = exhibit.last_bidder_member
                print '>' *10
                print 'USER %s WON EXHIBIT %s. (exhibit ended from status "auto_paused_last")' % (winner.id, exhibit.id)
                print 'total exhibit bidding time: %s' % (exhibit.ended_unixtime - exhibit.started_unixtime)
                print '<' *10

                user_connections = application.user_websockets.get(winner.id, list())
                winner_message = {'type': 'WON_EXHIBIT',
                                  'wins_number': winner.wins_number,
                                  'is_on_win_limit': winner.is_on_win_limit(),
                                  'win_limit_time_left': winner.win_limit_time_left}

                for connection in user_connections:
                    # update user object for WebSocket clients
                    connection.user.wins_number = winner.wins_number
                    connection.user.last_win_unixtime = winner.last_win_unixtime
                    # send message to winner
                    connection.write_message(json.dumps(winner_message))

                # add system notification to main message
                sys_message = '%s won "%s"' % (winner.username, exhibit.item.name)
                message.setdefault('sys_notifications', []).append(sys_message)
                # add it to mongoDB
                insert_system_notification_in_db(sys_message)
                data.append(info)
                # TODO winner msg
                if winner.is_facebook_verified():
                    # publish custom story
                    item_url = 'http://%s/exhibit/%s/%s/%s/' % (settings.SITE, exhibit.item.categories.all()[0].slug,
                                                                exhibit.item.brand.slug, exhibit.item.slug)
                    facebook_public_post(winner, 'win', item_url)
                continue
            elif can_extend_timer: # reset timer
                print 'EXTENDING TIMER FOW EXHIBIT %s (set status to "auto_paused")' % exhibit.id
                exhibit.status = 'auto_paused'
                exhibit.last_bidder_before_reset = exhibit.last_bidder_member
                exhibit.paused_unixtime = time()
                exhibit.auto_paused_amount +=1
                exhibit.save()
            else:  
                print 'EXTENDING TIMER FOW EXHIBIT %s LAST TIME (set status to "auto_paused_last")' % exhibit.id
                exhibit.status = 'auto_paused_last'
                exhibit.last_bidder_before_reset = exhibit.last_bidder_member
                exhibit.paused_unixtime = time()
                exhibit.save() 

        info['bidder_name'] = exhibit.last_bidder_name
        info['bidder_img'] = settings.MEDIA_URL + exhibit.last_bidder_member.avatar
        info['bidder_id'] = exhibit.last_bidder_member.id

        if pause_all:
            info['pause_all'] = True
        elif exhibit.is_paused():
            info['paused'] = True
        elif exhibit.is_auto_paused():
            info['auto_paused'] = True
        elif exhibit.is_auto_paused_last():
            info['auto_paused_last'] = True
        else:
            if exhibit.item.giveaway:
                info['time_left'] = view_time_left_giveaway(exhibit.ended_unixtime - now_time)
            else:
                info['time_left'] = view_time_left(exhibit.ended_unixtime - now_time)

            if exhibit.locked:
                info['locked_by'] = [bid[0] for bid in exhibit.bids.values_list('user').distinct()]
                # for guest users
                info['locked_by'].append('')
                info['user'] = user
        data.append(info)

    # notify all connected clients
    for client in application.websockets_pool:
        user['id'] = client.user.id
        client.ws_connection.write_message(json.dumps(message))


def view_time_left(time_left):
    """
    change seconds number to format "mm:ss"
    """
    minutes = str(int(time_left / 60))

    seconds = str(int(time_left % 60))

    if len(minutes) == 1:
        minutes = ''.join(['0', minutes])

    if len(seconds) == 1:
        seconds = ''.join(['0', seconds])

    return ':'.join([minutes, seconds])

def view_time_left_giveaway(time_left):
    """
    change seconds number to format "HH:mm:ss"
    """
    hours = int(time_left / 3600)
    time_left -= hours * 3600

    minutes = int(time_left  / 60)
    seconds = int(time_left  % 60)

    hours = str(hours)
    minutes = str(minutes)
    seconds = str(seconds)

    if len(hours) == 1:
        hours = ''.join(['0', hours])

    if len(minutes) == 1:
        minutes = ''.join(['0', minutes])

    if len(seconds) == 1:
        seconds = ''.join(['0', seconds])

    return ':'.join([hours, minutes, seconds])

def monitor_paused_exhibits():
    """
    Check if exhibits with statuses ["full_fund_pause", "after_win_pause", "relisted"] have passed their waiting phase if they did,
    move them to new statuses. If old status is "after_win_pause" - notify clients to remove this item. Create another
    exhibit from this item if there is amount
    """
    flush_transaction()
    removed = []
    created = []
    message = {'type': 'UPDATE_PAUSED_EXHIBITS', 'removed': removed, 'created': created}

    after_funding_exhibits = Exhibit.objects.full_fund_pause()\
        .filter(funded_unixtime__lt=time() - settings.FULL_FUND_PAUSE_TIME)

    for exhibit in after_funding_exhibits:
        print 'MOVE FUNDING EXHIBIT %s TO BIDDING STATUS (IN QUEUE)' % exhibit.id
        msg = {'id': exhibit.id, 'from_status': 'funding'}

        exhibit.status = 'bidding'
        exhibit.in_queue = True
        exhibit.save()
        removed.append(msg)

    after_bidding_exhibits = Exhibit.objects.after_win_pause() \
        .filter(ended_unixtime__lt=time() - settings.AFTER_WIN_PAUSE_TIME)

    for exhibit in after_bidding_exhibits:
        print 'MOVE BIDDING EXHIBIT %s TO BIDDING STATUS (IN QUEUE)' % exhibit.id
        msg = {'id': exhibit.id, 'from_status': 'bidding'}

        exhibit.status = 'waiting_payment'
        exhibit.save()
        removed.append(msg)

        new_exhibit = Exhibit.objects.create_from_item(exhibit.item)

        if new_exhibit:
            print 'CREATING NEW BIDDING EXHIBIT %s FROM FUNDED EXHIBIT %s' % (new_exhibit.id, exhibit.id)

            msg = dict(id=new_exhibit.id)
            msg['funding_box_prototype'] = render_to_string('exhibit/funding_box_prototype.html', {'exhibit': new_exhibit})
            msg['categories'] = [category.id for category in new_exhibit.item.categories.all()]
            created.append(msg)

    after_relisted_exhibits = Exhibit.objects.relisted() \
        .filter(ended_unixtime__lt=time() - settings.AFTER_WIN_PAUSE_TIME)

    for exhibit in after_relisted_exhibits:
        print 'MOVE RELISTED EXHIBIT %s BACK TO FUNDING STATE' % exhibit.id
        msg = {'id': exhibit.id, 'from_status': 'bidding'}
        # TODO clarify what it needed to be remove when item goes back to funding phase
        exhibit.cleanup_relisted_exhibit()
        exhibit.save()
        removed.append(msg)

        msg = dict(id=exhibit.id)
        created.append(msg)
        msg['categories'] = [category.id for category in exhibit.item.categories.all()]
        msg['funding_box_prototype'] = render_to_string('exhibit/funding_box_prototype.html', {'exhibit': exhibit})


    if removed:
        # notify all connected clients
        for client in application.websockets_pool:
            for msg in created:
                # change fund buttons for concrete user
                fund_button = render_to_string('exhibit/fund_button_prototype.html', {
                    'is_authenticated': not (client.user is Guest),
                    'exhibit_id': msg['id']})

                # generate template for it
                msg['funding_box'] = msg['funding_box_prototype'].replace('__FUND_BUTTON__', fund_button)
            client.ws_connection.write_message(json.dumps(message))


def insert_system_notification_in_db(text):
    """
    create record in MongoDB chat collection for system notification
    """
    msg = dict(message=text,
               date=datetime.datetime.utcnow(),
               system=True,
               )

    application.db.chat.insert(msg)


def monitor_min_max_active_exhibits():

    data = []
    message = {'type': 'ADD_NEW_BIDDINGS', 'data': data}

    # all exhibits which displaying in main menu
    exhibits = Exhibit.objects.bidding() \
            | Exhibit.objects.after_win_pause() \
            | Exhibit.objects.paused() \
            | Exhibit.objects.auto_paused_last() \
            | Exhibit.objects.relisted()

    active_count = exhibits.exclude(in_queue=True).count()

    # if there are free slots for biddings, display them
    available_slots = settings.MAX_DISPLAY_AUCTIONS - active_count

    # open one newbie giveaway and one giveaway for all users
    active_giveaways = exhibits.filter(item__giveaway=True).exclude(item__newbie=True)
    active_newbie_giveaways = exhibits.filter(item__giveaway=True, item__newbie=True)
    created_giveaways = []

    if len(active_giveaways) < settings.GIVEAWAY_DISPLAY_AUCTIONS:
        exhibit = Exhibit.objects.create_giveaway(newbie=False)
        if exhibit:
            created_giveaways.append(exhibit)
            print 'CREATING NEW GIVEAWAY EXHIBIT %s' % exhibit.id

    if len(active_newbie_giveaways) < settings.NEWBIE_GIVEAWAY_DISPLAY_AUCTIONS:
        exhibit = Exhibit.objects.create_giveaway(newbie=True)
        if exhibit:
            print 'CREATING NEW NEWBIE GIVEAWAY EXHIBIT %s' % exhibit.id
            created_giveaways.append(exhibit)

    for exhibit in created_giveaways:
        msg = dict(id=exhibit.id)
        msg['bidding_box_prototype'] = render_to_string('exhibit/bidding_box_prototype.html', {'exhibit': exhibit})
        msg['bidding_box_small_prototype'] = render_to_string('exhibit/bidding_box_small_prototype.html', {'exhibit': exhibit})
        msg['timer_drop_tool'] = render_to_string('exhibit/timer_drop_tool.html', {'exhibit': exhibit})
        msg['is_newbie'] = exhibit.item.newbie
        msg['giveaway'] = exhibit.item.giveaway
        data.append(msg)

        # add system notification to main message
        sys_message = '"%s" has been opened for bidding' % exhibit.item.name
        message.setdefault('sys_notifications', []).append(sys_message)
        # write it to MongoDB
        insert_system_notification_in_db(sys_message) 
        
    if available_slots > 0:
        # active_count += exhibits.filter(pk__in=exhibits.filter(in_queue=True)[:available_slots]).update(in_queue=False)
        queued_exhibits = exhibits.filter(in_queue=True)[:available_slots]

        for exhibit in queued_exhibits:
            print 'MOVE EXHIBIT %s FROM QUEUE TO BIDDING' % exhibit.id
            exhibit.in_queue = False
            exhibit.save()
            active_count += 1

            msg = dict(id=exhibit.id)
            msg['bidding_box_prototype'] = render_to_string('exhibit/bidding_box_prototype.html', {'exhibit': exhibit})
            msg['bidding_box_small_prototype'] = render_to_string('exhibit/bidding_box_small_prototype.html', {'exhibit': exhibit})
            msg['timer_drop_tool'] = render_to_string('exhibit/timer_drop_tool.html', {'exhibit': exhibit})
            msg['is_newbie'] = exhibit.item.newbie
            msg['giveaway'] = exhibit.item.giveaway
            data.append(msg)

            # add system notification to main message
            sys_message = '"%s" has been opened for bidding' % exhibit.item.name
            message.setdefault('sys_notifications', []).append(sys_message)
            # write it to MongoDB
            insert_system_notification_in_db(sys_message)
    else:
        return   

    if data:
        # notify all connected clients
        for client in application.websockets_pool:
            for msg in message['data']:
                # draw bid button for concrete user
                params = {'bid_allowed': False}
                if client.user is not Guest:
                    if not client.user.is_on_win_limit(msg['giveaway']):
                        if msg['is_newbie']:
                            if client.user.is_newbie:
                                params['bid_allowed'] = True
                            else:
                                params['newbie'] = True
                        else:
                            params['bid_allowed'] = True
                else:
                    params['not_logged'] = True

                if client.mobile_version:
                    # replace bidding template to small
                    prototype = msg['bidding_box_small_prototype']
                else:
                    prototype = msg['bidding_box_prototype']

                bid_button = render_to_string('exhibit/bid_button_prototype.html', {'params': params, 'exhibit_id': msg['id']})
                #replace it in bidding box
                msg['bidding_box'] = prototype.replace('__BID_BUTTON__', bid_button)
                if client.user.is_superuser:
                    msg['bidding_box'] = msg['bidding_box'].replace('__TIMER_DROP_TOOL__', msg['timer_drop_tool'])
                else:
                    msg['bidding_box'] = msg['bidding_box'].replace('__TIMER_DROP_TOOL__', '')

            client.ws_connection.write_message(json.dumps(message))


def start_admin_paused_exhibits():
    """
    unpause exhibits which timer has being dropped by admin
    """
    exhibits = Exhibit.objects.paused().filter(paused_unixtime__lt=time() - settings.DROP_TIMER_PAUSE_TIME)
    for exhibit in exhibits:
        print 'MOVE EXHIBIT %s FROM PAUSE TO BIDDING' % exhibit.id
        exhibit.status = 'bidding'
        # if exhibits has being already started change it's end time
        if exhibit.ended_unixtime:
            print 'UPDATE EXHIBIT %s BIDDING TIME (AFTER PAUSE)' % exhibit.id
            exhibit.ended_unixtime = time() + exhibit.bidding_time

        exhibit.save()


def declare_winner_or_relist():
    """
    Search for ended extended exhibits and declare winner or relist it 
    """
    flush_transaction()
    exhibits = Exhibit.objects.auto_paused_last()
    data = []
    message = {'type': 'RELIST_EXHIBITS', 'data': data}

    for exhibit in exhibits:
        if not exhibit.item.giveaway and exhibit.bids_amount < exhibit.min_bids_amount: # relist exhibit
            print 'RELIST EXHIBIT %s' % exhibit.id
            info = {'id': exhibit.id}
            # TODO don't relist giveaway items!
            exhibit.set_status('relisted')
            exhibit.ended_unixtime = time() - 1
            # return bids to users
            bids = exhibit.bids.all().values('user', 'type').annotate(count=Count('id'))
            for bid in bids: 
                bids_type = 'bonus_bids' if bid['type'] == 'bonus' else 'bids'
                update_date = {bids_type: F(bids_type) + bid.get('count', 0)}
                Profile.objects.filter(id=bid['user']).update(**update_date)

            # remove all old bids
            exhibit.bids.all().delete()
            exhibit.save() 
            data.append(info)

            # add system notification to main message
            sys_message = '"%s" has been relisted' % (exhibit.item.name)
            message.setdefault('sys_notifications', []).append(sys_message)
            # add it to mongoDB
            insert_system_notification_in_db(sys_message)

        else: # declare winner
            print 'GIVEAWAY ITEM, DECLARE winner for EXHIBIT %s' % exhibit.id
            exhibit.set_status('bidding')
            exhibit.ended_unixtime = time() - 1
            exhibit.save() 

    # notify all connected clients
    for client in application.websockets_pool:
        client.ws_connection.write_message(json.dumps(message))

if __name__ == '__main__':
    application.listen(settings.TORNADO_PORT)

    main_loop = tornado.ioloop.IOLoop.instance()

    active_users_ct = tornado.ioloop.\
        PeriodicCallback(update_active_users_counter,
                         UPDATE_ACTIVE_USERS_COUNTER_INTERVAL,
                         io_loop=main_loop)

    pause_exhibits = tornado.ioloop.\
        PeriodicCallback(monitor_paused_exhibits,
                         MONITOR_PAUSED_EXHIBITS_INTERVAL,
                         io_loop=main_loop)

    admin_paused_exhibits = tornado.ioloop.\
        PeriodicCallback(start_admin_paused_exhibits,
                         START_ADMIN_PAUSED_EXHIBITS_INTERVAL,
                         io_loop=main_loop)

    biddings_update = tornado.ioloop.\
        PeriodicCallback(update_bidding_exhibits,
                         UPDATE_BIDDING_EXHIBITS_INTERVAL,
                         io_loop=main_loop)

    min_max_active = tornado.ioloop.\
        PeriodicCallback(monitor_min_max_active_exhibits,
                         MONITOR_MIN_MAX_ACTIVE_EXHIBITS_INTERVAL,
                         io_loop=main_loop)

    declare_winner_or_relist = tornado.ioloop.\
        PeriodicCallback(declare_winner_or_relist,
                         DECLARE_WINNER_OR_RELIST_INTERVAL,
                         io_loop=main_loop)

    active_users_ct.start()
    pause_exhibits.start()
    biddings_update.start()
    min_max_active.start()
    admin_paused_exhibits.start()
    declare_winner_or_relist.start()

    main_loop.start()
