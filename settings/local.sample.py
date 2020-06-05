# sample file to create local settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '',
        'NAME': 'exhibia'
    }
}
TORNADO_PORT = '8001'
WEBSOCKET_ADDRESS = 'ws://127.0.0.1:' + TORNADO_PORT
TORNADO_API_ADDRESS = 'http://127.0.0.1:' + TORNADO_PORT + '/api/'

PAYPAL_TEST_ACCOUNT = 'anthony.poddubny-facilitator@gmail.com'
PAYPAL_END_POINT = 'api.sandbox.paypal.com'
PAYPAL_MODE = 'sandbox'
PAYPAL_CLIENT_ID = 'AWlXPBB2j2lcLmMDnIqncdKC4hbSv0sH_iEgb2pI-M40JgDyWVabYZOUF3tZ'
PAYPAL_SECRET = 'EHzcQhB2rCtQCNUfbwwTJFfjOXHsGz84BBd3t2lwWCW6B2wxTDl8kfwICX_x'

PAYPAL_BUY_NOW_RETURN_URL = "http://127.0.0.1:8000/payment/buy-now/paypal?success=true"
PAYPAL_BUY_NOW_CANCEL_URL = "http://127.0.0.1:8000/payment/buy-now/paypal?cancel=true"
PAYPAL_BUY_BIDS_RETURN_URL = "http://127.0.0.1:8000/payment/buy-bids/paypal?success=true"
PAYPAL_BUY_BIDS_CANCEL_URL = "http://127.0.0.1:8000/payment/buy-bids/paypal?cancel=true"
PAYPAL_BUY_SHIPPING_RETURN_URL = "http://127.0.0.1:8000/payment/buy-shipping/paypal?success=true"
PAYPAL_BUY_SHIPPING_CANCEL_URL = "http://127.0.0.1:8000/payment/buy-shipping/paypal?cancel=true"
PAYPAL_BUY_AND_RETURN_BIDS_RETURN_URL = "http://127.0.0.1:8000/payment/buy-and-return-bids/paypal?success=true"
PAYPAL_BUY_AND_RETURN_BIDS_CANCEL_URL = "http://127.0.0.1:8000/payment/buy-and-return-bids/paypal?cancel=true"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '313089854027-qev02oocrld6hrl61tgtu3dcn3ma5gvf.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'zGG1M8LT3bXbmVtfMIUyTJqJ'

SOCIAL_AUTH_FACEBOOK_KEY = '1531074240440476'
SOCIAL_AUTH_FACEBOOK_SECRET = 'f419d49777c222388c6556ad335e63c8'

SITE = 'localhost:8000'
# SITE = '127.0.0.1:8000'

def get_websocket_address(request):
    return WEBSOCKET_ADDRESS


# url for tornado handler, using as API
def get_tornado_api_address(request):
    return TORNADO_API_ADDRESS
