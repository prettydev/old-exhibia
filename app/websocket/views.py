import json
from django.http import HttpResponse
import requests
from account.models import Profile
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from bson.objectid import ObjectId
import pymongo
import settings


@staff_member_required
def admin_chat(request):

    connection = pymongo.Connection(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
    db = getattr(connection, settings.MONGODB['NAME'])

    if request.method == 'POST':
        if request.POST.get('action') == 'delete_selected':
            ids = request.POST.getlist('_selected_action')
            if ids:
                response = db.chat.remove({"_id": {"$in": [ObjectId(id) for id in ids]}})
                messages.add_message(request, messages.INFO, 'Successfully delete messages.')
                return redirect('admin_chat')
            else:
                messages.add_message(request, messages.INFO, 'Items must be selected in order to perform actions on them. No items have been changed.')
        elif not request.POST.get('action'):
            messages.add_message(request, messages.INFO, 'No action selected.')

    cursor = db.chat.find().limit(50).sort("date", pymongo.DESCENDING)

    chat_messages = []
    users = dict()

    for message in cursor:
        if not message.get('user_id'):
            message['user'] = None
        else:
            message['user'] = users.get(message['user_id'], Profile.objects.get(pk=message['user_id']))
        chat_messages.append(message)

    return render(request, 'websocket/chat_admin.html', {'chat_messages': chat_messages})


def websocket_api(action, params, request):
    data = dict(secret_key=settings.SECRET_KEY, action=action, data=json.dumps(params))
    result = requests.post(settings.get_tornado_api_address(request), data=data)
    print '>>> post result %s' % result
    return result
