# -*- coding: utf-8 -*-

# Start python-social-auth configuration
SOCIAL_AUTH_LOGIN_ERROR_URL = '/'
SOCIAL_AUTH_USER_MODEL = 'account.Profile'
SOCIAL_AUTH_FACEBOOK_KEY = '129299757101755'
SOCIAL_AUTH_FACEBOOK_SECRET = '6b2f92a905b24bbc762c20c37c7cd7df'
FACEBOOK_APP_TOKEN = '129299757101755|91iGBPML5yv1RGK37IUtvXMHSgU'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_friends', 'publish_actions'] # 'user_location', 'user_birthday'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '313089854027-tfljmmcdf9bt0b07bqo23dj9o7q231d2.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'esTgrmFueFCC3HzF9KnMdRQK'
SOCIAL_AUTH_UUID_LENGTH = 4
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['_username', '_email', '_first_name']

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'app.account.pipeline.save_profile_picture',
    'app.account.pipeline.process_verification_bonuses',
)
# End python-social-auth configuration

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'info@exhibia.com'
EMAIL_HOST_PASSWORD = 'bitches000'
DEFAULT_FROM_EMAIL = 'info@exhibia.com'

# Twilio settings
ACCOUNT_SID = 'AC05e81cddbe87e108bfa59b01cc2a44c9'
AUTH_TOKEN = '290f55d984c517149a37610625d3827b'
# Test settings
# ACCOUNT_SID = 'AC05e81cddbe87e108bfa59b01cc2a44c9'
# AUTH_TOKEN = '290f55d984c517149a37610625d3827b'
# END Test settings
FROM_NUMBER = '+13234309333'  # valid test number
# END Twilio settings


LOGIN_REDIRECT_URL = 'https://www.exhibia.com/'

PAYPAL_TEST_ACCOUNT = 'info@exhibia.com'
PAYPAL_END_POINT = 'api.paypal.com'
PAYPAL_MODE = 'live'
PAYPAL_CLIENT_ID = 'AW6-DhBSYK9RkjwdURNuXlFt4diVACeh4hRu7H_7WGS4gh9LuFjRGkfWDvPo'
PAYPAL_SECRET = 'EAHMihDOo47g1H_KWXxlG-qTInNn-RihVFvr_yOz3dGZ360FDTB07RHXp3BK'
PAYPAL_BUY_NOW_RETURN_URL = "https://www.exhibia.com/payment/buy-now/paypal?success=true"
PAYPAL_BUY_NOW_CANCEL_URL = "https://www.exhibia.com/payment/buy-now/paypal?cancel=true"
PAYPAL_BUY_BIDS_RETURN_URL = "https://www.exhibia.com/payment/buy-bids/paypal?success=true"
PAYPAL_BUY_BIDS_CANCEL_URL = "https://www.exhibia.com/payment/buy-bids/paypal?cancel=true"
PAYPAL_BUY_SHIPPING_RETURN_URL = "https://www.exhibia.com/payment/buy-shipping/paypal?success=true"
PAYPAL_BUY_SHIPPING_CANCEL_URL = "https://www.exhibia.com/payment/buy-shipping/paypal?cancel=true"
PAYPAL_BUY_AND_RETURN_BIDS_RETURN_URL = "https://www.exhibia.com/payment/buy-and-return-bids/paypal?success=true"
PAYPAL_BUY_AND_RETURN_BIDS_CANCEL_URL = "https://www.exhibia.com/payment/buy-and-return-bids/paypal?cancel=true"


# TWITTER_CONSUMER_KEY = 'y2vUwX1Bsamx9X8wYmM9g'
# TWITTER_CONSUMER_SECRET = 'LvavS6nKMrzG8wMm6feah84lnMxOXb6e9mKVrf09Pg'
# TWITTER_ACCESS_TOKEN = ''
# TWITTER_TOKEN_SECRET = ''
# TWITTER_HASH_TAGS = ['exhibia']


#video-manager
# VIDEO_MANAGER_CONFIG = {
#     'DEVELOPER_KEY': 'AI39si4mlBv42cQbZOPyMaFtMBu-X2M1Uikq_pyoST-Wf1L32jll00nkVq9hXWhZIJNt6ZqoZlBfEBUnwU_Z7RUTkki-3RSH2g',
#     'CLIENT_ID': 'Bidstick',
#     'SOURCE': 'django_video_rec',
#     'VIDEO_PATH': 'videos',
#     'VIDEO_SAVE_FN': 'testimonials.views.video_save_fn',
#     'VIDEO_SNAPSHOT_FN': 'testimonials.views.video_snapshot_fn',
#     'VIDEO_ID_FN': 'testimonials.views.video_id_fn',
#     'RTMP_SERVER': 'rtmp://test.app.com/hdfvr/_definst_'
# }
# #from django.core.files.storage import default_storage
# #default_storage.path('fichero.flv')

# SOCIAL_ACCOUNTS = {
#     'youtube': {
#         'DEVELOPER_KEY': 'AI39si4mlBv42cQbZOPyMaFtMBu-X2M1Uikq_pyoST-Wf1L32jll00nkVq9hXWhZIJNt6ZqoZlBfEBUnwU_Z7RUTkki-3RSH2g',
#         'CLIENT_ID': 'Bidstick',
#         'SOURCE': 'django_video_rec',
#         'USERNAME': 'xtealc@gmail.com',
#         'PASSWORD': ''
#     },
#     'facebook': {
#         'API_ID': '129299757101755',
#         'API_SECRET': '6b2f92a905b24bbc762c20c37c7cd7df',
#         'ACCESS_TOKEN': 'AAABphjOSYt8BAPE8uSe7WiwZC6616gJwGqwoLdKi8QFRZANft2i8vqfzN1UZBoS4x7zNbNNfQWlqmZAU40Ktdzd1YYZCE1TEZD',
#         'APP_TOCKEN': '129299757101755|91iGBPML5yv1RGK37IUtvXMHSgU',
#         'PAGE_ID': '107701282676058',
#         'PAGE_ACCESS_TOKEN': 'AAABphjOSYt8BAKCkjVrybJQXqV6hJIPZBPdqoZB1jksCoYLFZAlJ9CXP5NADQphbePwW1CP9ZCoHuTbQYI5MGZAgqMeCo0nchlSPxLGWE7AZDZD'
#     }
# }
#
# RED5_STREAM_PATH = '/Users/vh5/Downloads/hd/red8/webapps/hdfvr/streams/_definst_/'
#
# # Social
#
# GOOGLEPLUS_ITEM_LIMIT_DAILY = 2
# GOOGLEPLUS_ITEM_FREEBIDS = 1
# FACEBOOK_LIKES_ITEM_LIMIT_DAILY = 2
# FACEBOOK_LIKE_ITEM_FREEBIDS = 1
#
# # endSocial
