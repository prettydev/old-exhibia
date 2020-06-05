
"""
Django settings for exhibia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*nujamw2^-6=6x!o7q7$@@k&fg53p9ejgo)6*$3qrkj&drck&v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SERVER_EMAIL = 'info@exhibia.com'

ADMINS = (
    ('Anthony', 'anthony.poddubny@gmail.com'),
)

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'account.Profile'
# Application definition

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    # 3rd party apps
    'pipeline',
    'social.apps.django_app.default',
    'gunicorn',
    'south',
    'widget_tweaks',
    'mailqueue',
    #'sslserver',
    'ckeditor',


    'app.account',
    'app.exhibit',
    'app.payment',
    'app.websocket',
    'app.screen_capture',

    # for development
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # ubnable for running this application from facebook app (using canvas)
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mobi.middleware.MobileDetectionMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'urls'

SITE_ID = 1

WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'app.websocket.context_processors.websocket_address',
)

LOGGING = {
   'version': 1,
   'disable_existing_loggers': False,
   'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] -- %(message)s'
        },
        'adwanced': {
            'format': '[%(levelname)s] -- %(message)s -- %(module)s'
            ' %(process)d %(thread)d'
        },
    },
   'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
   },
   'loggers': {
       'exhibia': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'exHI165lau954abc',
        'NAME': 'exhibia'
    }
}

# mongodb is using to store chat messages
MONGODB = {
    'HOST': 'localhost',
    'PORT': 27017,
    'NAME': 'exhibia',
}


TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, "templates"),

]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Basic',
        'toolbar_Basic': [
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            ['Source', '-', 'Bold', 'Italic', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',]
        ],
    },
}

# Start Pipeline configuration
#STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
# End Pipeline configuration

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'project_static'),
)


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TEMP_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'temp')

CKEDITOR_UPLOAD_PATH = BASE_DIR + '/media/uploads'

SESSION_ENGINE = 'redis_sessions.session'

ACCOUNT_VERIFICATION_DAYS = 2

# port used to run tornado web-server
TORNADO_PORT = '8001'

# proxy header X_Forwarded_Proto with value $https will be ('on' or '')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'on')


# Nginx will proxy all requests with /websocket/ to tornado web server. See exhibia_nginx.conf.
def get_websocket_address(request):

    if request.is_secure():
        return 'wss://www.exhibia.com/websocket/'

    return 'ws://www.exhibia.com/websocket/'


# url for tornado handler, using as API
def get_tornado_api_address(request):
    return 'http://www.exhibia.com/websocket/api/'
    # if request.META.get('HTTP_X_FORWARDED_PROTOCOL', '') == 'https':
    #     'https://www.exhibia.com/websocket/api/'
    #     # TORNADO_API_ADDRESS
    # return 'http://www.exhibia.com/websocket/api/'
