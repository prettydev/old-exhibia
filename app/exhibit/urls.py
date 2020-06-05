# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('exhibit.views',
    url(r'^append-funding-carousel/$', 'append_funding_carousel', name='append_funding_carousel'),
    url(r'^append_item_page/$', 'append_item_page', name='append_item_page'),
    url(r'^admin-timer-drop-tool/$', 'admin_timer_drop_tool', name='admin_timer_drop_tool'),
    url(r'^admin-pause-all/$', 'pause_all_exhibits', name='pause_all_exhibits'),
    url(r'^admin-unpause-all/$', 'unpause_all_exhibits', name='unpause_all_exhibits'),
    url(r'^tracking-code/$', 'tracking_code', name='tracking_code'),
    url(r'^(?P<category_slug>[-\w]+)/(?P<brand_slug>[-\w]+)/(?P<item_slug>[-\w]+)/$', 'item_page', name='item_page'),
    url(r'^toogle-guest-chat/$', 'toogle_guest_chat', name='toogle-guest-chat'),
)
