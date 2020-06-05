from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import settings
from django.http import HttpResponse

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'exhibit.views.index', name='home'),
    url(r'^facebook-app-page/$', 'exhibit.views.facebook_app_page', name='facebook-app-page'),
    url(r'^payment/', include('payment.urls')),
    url(r'^exhibit/', include('exhibit.urls')),
    url(r'^profile/', include('account.urls')),
    url(r"^admin/chat/$", "websocket.views.admin_chat", name='admin_chat'),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('^accounts/', include('django.contrib.auth.urls')),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nAllow: /", mimetype="text/plain")),
    url(r'^ckeditor/upload/', 'ckeditor.views.upload', name='ckeditor_upload'),
    url(r'^ckeditor/browse/', 'ckeditor.views.browse', name='ckeditor_browse'),
)

# only for debug mode
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

