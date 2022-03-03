import jwt
import src.auth
from src.data_store import data_store
from src.error import AccessError, InputError
import re

# Returns true if channel_id refers to a valid channel, else false
def valid_channel_id(channel_id):
    store = data_store.get()
    return any(ch['channel_id'] == channel_id for ch in store['channels'])

def valid_dm_id(dm_id):
    store = data_store.get()
    return any(dm['dm_id'] == dm_id for dm in store['dms'])

# Returns true if u_id refers to a valid user, else false
def valid_user_id(u_id, include_removed=False):
    store = data_store.get()
    return any(u['u_id'] == u_id for u in store['users'] if u['global_permissions'] != 3 or include_removed)


# Returns the user id of the user associated with the token
# Assumes the token is valid
def token_user(token):
    return jwt.decode(token, src.auth.SECRET, algorithms=['HS256'])['u_id']

# Returns true if token refers to a valid user token
def valid_token(token):
    store = data_store.get()
    sessions = store['sessions']

    try:
        decoded_jwt = jwt.decode(token, src.auth.SECRET, algorithms=['HS256']) 
    except Exception:
        print("Could not decode token")
        return False

    u_id = decoded_jwt['u_id']
    s_id = decoded_jwt['s_id']
    

    # Is the user valid?
    if not valid_user_id(u_id):
        print(f"Invalid UID {u_id}")
        return False
    
    # Is the session valid?
    return any(s == s_id for s in sessions)
  


# Returns true if user u_id is a member of channel c_id, else false
# if optional third arg is 'dms', checks dms instead of channels
def user_is_member(u_id, c_id, chat_type='channels'):
    store = data_store.get()
    users = store[chat_type][c_id]['all_members']
    return u_id in users

# Returns true if user u_id is a global owner and a member of the channel,
# or is an owner of the channel
# if optional third arg is 'dms', checks dms instead of channels
def user_has_owner_perms(u_id, c_id, chat_type='channels'):
    store = data_store.get()

    if store['users'][u_id]['global_permissions'] == 1 and user_is_member(u_id, c_id):
        return True

    if any(u == u_id for u in store[chat_type][c_id]['owner_members']):
        return True
    
    return False


# Return user's details as a dict given u_id
def get_user_details(u_id):
    store = data_store.get()
    users = store['users']
    user_details = {}
    for user in users:
        if user['u_id'] == u_id:
            user_details = {
                'u_id': user['u_id'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'email': user['email'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url']
            }
    return user_details

# Returns true if email address matches the format for a valid email address
def email_is_valid(email):
	pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
	return True if re.fullmatch(pattern, email) else False

def user_has_reacted(u_id, message_id, react_id):
    store = data_store.get()
    # determine what channel the message is in
    chat_type = store['message_info'][message_id]['type']
    chat_id = store['message_info'][message_id]['to']
    chat = store[chat_type][chat_id]

    for msg in chat['messages']:
        if msg['message_id'] == message_id:
            return u_id in msg['reacts'][react_id - 1]['u_ids']

def message_with_user_react(message, u_id):
    for i, react in enumerate(message['reacts']):
        message['reacts'][i]['is_this_user_reacted'] = u_id in react['u_ids']
    return message
    
def pin_message(u_id, m_id, pin_mode=True):
    store = data_store.get()
    try:
        msg_info = store['message_info'][m_id]
    except Exception as e:
        raise InputError(description='Message ID does not exist.') from e

    channel = None
    if msg_info['type'] == 'channels':
        c_id = msg_info['to']
        channel = store['channels'][c_id]
    else:
        dm_id = msg_info['to']
        channel = store['dms'][dm_id]

    if u_id not in channel['all_members']:
        raise InputError(description='message_id is not a valid message within a channel or DM that the authorised user has joined')
    if u_id not in channel['owner_members']:
        raise AccessError(description='message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM')

    msg = list(filter(lambda m: m_id == m['message_id'], channel['messages']))[0]

    if pin_mode:
        if msg['is_pinned']:
            raise InputError(description='Message is already pinned.')
        msg['is_pinned'] = True
    else:
        if not msg['is_pinned']:
            raise InputError(description='Message is already not pinned.')
        msg['is_pinned'] = False

    return msg['is_pinned']

def reset_code_is_valid(reset_code):
    store = data_store.get()
    return any(user['reset_code'] == reset_code for user in store['users'])


   