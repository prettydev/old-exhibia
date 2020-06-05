# -*- coding: utf-8 -*-
STANDARD_SHIPPING_PRICE = 7
PRIORITY_SHIPPING_PRICE = 15

# delay before displaying for bidding (after exhibit was fully funded)
# WHENEVER you change this value, be sure that task
# fully_fund_notifier and cron for this task has time less than this one in two times
FULL_FUND_PAUSE_TIME = 10 * 60

# exhibit will stay there for X mins more displaying the winner until disappears from bidding and appears to funding
AFTER_WIN_PAUSE_TIME = 10 * 60

FACEBOOK_ADMIN_USER_ID = 22

# displaying items on main page
MIN_DISPLAY_AUCTIONS = 5
MAX_DISPLAY_AUCTIONS = 15

NEWBIE_GIVEAWAY_DISPLAY_AUCTIONS = 1
GIVEAWAY_DISPLAY_AUCTIONS = 1

# minimum amount of bids before we can declare the winner/either relist exhibit
DEFAULT_MIN_BIDS_AMOUNT = 20

# count of extending timer dropping (Going, Going, Gone)
TIMER_EXTENDING_COUNT = 2

# pause after admin drop timer for exhibit
DROP_TIMER_PAUSE_TIME = 5

# if exhibits count > this value items will be displayed in small size
MAX_AUCTIONS_BIG_TEMPLATES_COUNT = 15

WIN_LIMIT_TIME = 24 * 60 * 60

# for X time user can get his bids back if he buy item at full price
BID_REFUND_TIME = 6 * 60 * 60

# needed for displaying in emails/mobile messages
SITE = 'www.exhibia.com'

# reward points for some actions
REWARD_FOR_FUND = 3
REWARD_FOR_BID = 1
REWARD_FOR_WON = 2
REWARD_FOR_BUY = 2
REWARD_FOR_FULL_SOCIAL_ASSOCIATE = 4000
# end rewards

# TINYMCE_DEFAULT_CONFIG = {
#     'plugins': "table,spellchecker,paste,searchreplace",
#     'theme': "advanced",
#     'cleanup_on_startup': True,
#     'custom_undo_redo_levels': 10,
#     'width' : '768',
#     'height':'512',
#     }
#
# ### rackspace cloud files settings
# CLOUDFILES_USERNAME = 'artem.davidov'
# CLOUDFILES_API_KEY = '2f7bfec9dc1b45e09bbccfb318dfd4b8'
# CLOUDFILES_CONTAINER = 'static'
# DEFAULT_FILE_STORAGE = 'storages.backends.mosso.CloudFilesStorage'
# # Optional - use SSL
# #CLOUDFILES_SSL = True

# django-compressor
# COMPRESS = False
# COMPRESS_ENABLED = False
# COMPRESS = True
# COMPRESS_ENABLED = True
# COMPRESS_OFFLINE = True
# COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# COMPRESS_STORAGE = 'storages.backends.mosso.CloudFilesStorage'
