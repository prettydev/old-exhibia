import requests
from settings import FACEBOOK_ADMIN_USER_ID
from account.models import Profile


def _get_fb_access_token(user):
	return user.social_auth.get(provider='facebook').extra_data.get('access_token')


def facebook_public_post(user, msg_type, item_url):
	access_token = _get_fb_access_token(user)
	requests.get('https://graph.facebook.com/me/exhibia:%s?' % msg_type,
                     params={'access_token': access_token,
                             'method': 'POST',
                             'item': item_url})

def facebook_public_winner_post(user, winner_post_img, item_name):
	access_token = _get_fb_access_token(user)
 	if user.first_name and user.last_name:
 		user_name = '%s %s' % (user.first_name, user.last_name)
	else:
		user_name = user.username
	msg = '%s won %s' % (user_name, item_name)
	fb_uid = user.social_auth.get(provider='facebook').uid
	print requests.get('https://graph.facebook.com/%s/photos' % fb_uid,
                     params={'access_token': access_token,
                             'method': 'POST',
                             'url': winner_post_img,
                             'message': msg
                             })

def facebook_public_winner_post_at_exhibia(user, winner_post_img, item_name):
	admin_user = Profile.objects.get(id=FACEBOOK_ADMIN_USER_ID)
	access_token = _get_fb_access_token(admin_user)

 	if user.first_name and user.last_name:
 		user_name = '%s %s' % (user.first_name, user.last_name)
	else:
		user_name = user.username
	msg = '%s won %s' % (user_name, item_name)
	print requests.get('https://graph.facebook.com/Exhibia/feed',
                 params={'access_token': access_token,
                         'method': 'POST',
                         'link': winner_post_img,
                         'message': msg
                         })


# FB.api(
#     "/Exhibia/feed",
#     "POST",
#     {
#         "link": "https://www.exhibia.com/media/items/Disney_Frozen_Scoop_Carry_All_Tin_Classic_Purse_with_Beaded_Handle_Elsa.jpg", 
#          "message":"message test"
#     },
#     function (response) {
#       console.log(response);
#     })


# ### exhibia group

# FB.api(
#     "/me/permissions",
#     function (response) {
#       if (response && !response.error) {
#         console.log(response);
#       }
#     }
# );