from src.error import AccessError, InputError
from src.validation import email_is_valid, valid_token, token_user, valid_user_id, get_user_details
from src.data_store import data_store
from datetime import datetime, timezone
import requests
from PIL import Image
from io import BytesIO
from src import config

def user_profile_v1(token, u_id):
    '''
    Returns information about a user.

    Arguments:
        token (string)		- authorisation token of the user (session) requesting a profile
        u_id (int)			- u_id of the user to return the profile of

    Exceptions:
        InputError - Occurs when:
            > u_id does not refer to a valid user
        
        AccessError - Occers when:
            > token is invalid

    Return Value:
        Returns a user dictionary containing 'u_id', 'email', 'name_first', 'name_last', 'handle_str', 'profile_img_url'
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    if not valid_user_id(u_id, include_removed=True):
        raise InputError(description="Invalid u_id")

    return {'user': get_user_details(u_id)}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Replaces the user's handle with handle_str.

    Arguments:
        token (string)		- authorisation token of the user (session) requesting a handle change
        handle_str (string) - new handle to use

    Exceptions:
        InputError - Occurs when:
            > handle_str is not between 3 and 20 chars (inc.)
            > handle_str is already in use
            > handle_str is not entirely alphanumeric
        
        AccessError - Occers when:
            > token is invalid

    Return Value:
        Returns an empty dictionary
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    if not 3 <= len(handle_str) <= 20:
        raise InputError(description="Handle must be between 3 and 20 characters")

    if not handle_str.isalnum():
        raise InputError(description="Handle must be alphanumeric")

    store = data_store.get()

    if any(u['handle_str'] == handle_str for u in store['users']):
        raise InputError(description="This handle is already in use")

    store['users'][token_user(token)]['handle_str'] = handle_str

    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    Replaces the user's email with email.

    Arguments:
        token (string)		- authorisation token of the user (session) requesting an email change
        email (string)		- new email to use

    Exceptions:
        InputError - Occurs when:
            > email is not a valid email format
            > email is already in use
        
        AccessError - Occers when:
            > token is invalid

    Return Value:
        Returns an empty dictionary
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    if not email_is_valid(email):
        raise InputError(description="Email does not match a valid format")

    store = data_store.get()

    if any(u['email'] == email for u in store['users']):
        raise InputError(description="This email is already in use")

    store['users'][token_user(token)]['email'] = email

    data_store.set(store)
    return {}

def user_profile_setname_v1(token, name_first, name_last):
    '''
    Replaces the user's first and last names.

    Arguments:
        token (string)		- authorisation token of the user (session) requesting an email change
        name_first (string)	- new first name to use
        name_last (string)	- new last name to use

    Exceptions:
        InputError - Occurs when:
            > either name is not 1..50 characters
        
        AccessError - Occurs when:
            > token is invalid

    Return Value:
        Returns an empty dictionary
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    if not (1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50):
        raise InputError(description="Both names must be between 1 and 50 chars long (inc.)")

    store = data_store.get()

    store['users'][token_user(token)]['name_first'] = name_first
    store['users'][token_user(token)]['name_last'] = name_last

    data_store.set(store)
    return {}

def user_stats_v1(token):
    '''
    Returns analytics about a given user's involvement with UNSW streams

    Arguments: 
        token (string)	- authorisation token of the user requesting the analytics

    Exceptions:
        AccessError - Occurs when:
            > token is invalid

    Return Value:
        Returns a user_stats dictionary containing 'channels_joined', 'dms_joined', 'messages_sent', 'involvement_rate'
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    store = data_store.get()
    users = store['users']
    u_id = token_user(token)

    for user in users:
        if user['u_id'] == u_id:
            stat_block = dict(user['stats'])
            
    numerator = 0
    for key, value in stat_block.items():
        numerator += value[-1]['num_' + key]

    denominator = 0
    for key, value in store['workplace_stats'].items():
        denominator += value[-1]['num_' + key]
    if denominator == 0:
        involvement_rate = 0
    else:
        involvement_rate = numerator/denominator

    stat_block['involvement_rate'] = involvement_rate
    return {
        'user_stats': stat_block
    }

def stat_update(u_id, statistic, diff):
    '''
    Helper function that updates a user's statistics
    '''

    store = data_store.get()
    users = store['users']

    for user in users:
        if user['u_id'] == u_id:
            user['stats'][statistic].append({
                'num_' + statistic: user['stats'][statistic][-1]['num_' + statistic]+diff,
                'time_stamp': int(datetime.now(timezone.utc).timestamp())
            })
            break
    return

def global_stat_update(statistic, diff):
    '''
    Helper function that updates global statistics
    '''

    store = data_store.get()
    store['workplace_stats'][statistic].append({
        'num_' + statistic: store['workplace_stats'][statistic][-1]['num_' + statistic]+diff,
        'time_stamp': int(datetime.now(timezone.utc).timestamp())
    })
    return

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end, host_url):
    '''
    Downloads a JPG image from the internet via a given URL, and crops according to specifications.
    The formatted image becomes the user's profile picture.
    
    Arguments: 
        token (string)	- authorisation token of the user requesting the profile picture change
        img_url (string)  - URL that the desired JPG resides at
        x_start (int) - number of horizontal pixels (starting left) from which to begin image cropping
        y_start (int) - number of vertical pixels (starting top) from which to begin image cropping
        x_end (int) - number of horizontal pixels (starting left) at which to end image cropping
        y_end (int) - number of vertical pixels (starting top) at which to end image cropping

    Exceptions:
        InputError  - Occurs when:
            > img_url returns an HTTP status other than 200
            > any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
            > x_end is less than x_start or y_end is less than y_start
            > image uploaded is not a JPG
        AccessError - Occurs when:
            > token is invalid

    Return Value:
        Returns an empty dictionary
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    try:
        resp = requests.get(img_url, stream=True)
    except Exception as e:
        raise InputError(description="Url did not respond") from e
    if resp.status_code != 200:
        raise InputError(description="Url did not return successfully")

    image = Image.open(BytesIO(resp.content))
    if image.format not in ('JPEG', 'JPG'):
        raise InputError(description="Improper file type")
    if not (0 <= x_start <= x_end <= image.size[0]-1 and 0 <= y_start <= y_end <= image.size[1]-1):
        raise InputError(description="Specified bounds are Invalid")

    u_id = token_user(token)

    image = image.crop((x_start, y_start, x_end, y_end))

    store = data_store.get()
    imageno = store['current_profile_img']
    image.save(f'profile_imgs/{imageno}.jpg')

    store['users'][u_id]['profile_img_url'] = host_url + f'profile_imgs/{imageno}.jpg'

    store['current_profile_img'] += 1

    data_store.set(store)
    return {}