import json
from flask.globals import request
import requests
from src import config

# Make request


def auth_register_v2_request(email, password, name_first, name_last):
    return requests.post(config.url + 'auth/register/v2', json={
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    })


def auth_login_v2_request(email, password):
    return requests.post(config.url + 'auth/login/v2', json={
        'email': email,
        'password': password,
    })

def auth_passwordreset_v1_request(email):
    return requests.post(config.url + 'auth/passwordreset/request/v1', json={
        'email': email
    })
    
def auth_passwordreset_reset_v1_request(reset_code, new_password):
    return requests.post(config.url + 'auth/passwordreset/reset/v1', json={
        'reset_code': reset_code,
        'new_password': new_password
    })

def clear_v1_request():
    return requests.delete(config.url + 'clear/v1', params={})


def channels_create_v2_request(token, name, is_public):
    return requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': name,
        'is_public': is_public
    })


def channel_join_v2_request(token, channel_id):
    return requests.post(config.url + 'channel/join/v2', json={
        'token': token,
        'channel_id': channel_id,
    })


def channel_details_v2_request(token, channel_id):
    return requests.get(config.url + 'channel/details/v2', params={
        'token': token,
        'channel_id': channel_id,
    })


def channel_invite_v2_request(token, channel_id, u_id):
    return requests.post(config.url + 'channel/invite/v2', json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })


def channel_addowner_v1_request(token, channel_id, u_id):
    return requests.post(config.url + 'channel/addowner/v1', json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })


def channel_removeowner_v1_request(token, channel_id, u_id):
    return requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })


def channels_listall_v2_request(token):
    return requests.get(config.url + 'channels/listall/v2', params={
        'token': token
    })


def channels_list_v2_request(token):
    return requests.get(config.url + 'channels/list/v2', params={
        'token': token
    })


def channel_messages_v2_request(token, channel_id, start):
    return requests.get(config.url + 'channel/messages/v2', params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    })


def channel_leave_v1_request(token, channel_id):
    return requests.post(config.url + 'channel/leave/v1', json={
        'token': token,
        'channel_id': channel_id
    })


def auth_logout_v1_request(token):
    return requests.post(config.url + 'auth/logout/v1', json={
        'token': token
    })


def message_send_v1_request(token, channel_id, message):
    return requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })


def message_senddm_v1_request(token, dm_id, message):
    return requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': message
    })


def admin_userpermission_change_v1_request(token, u_id, permission_id):
    return requests.post(config.url + 'admin/userpermission/change/v1', json={
        'token': token,
        'u_id': u_id,
        'permission_id': permission_id
    })


def admin_user_remove_v1_request(token, u_id):
    return requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': token,
        'u_id': u_id
    })


def dm_create_v1_request(token, u_ids):
    return requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids': u_ids
    })


def dm_details_v1_request(token, dm_id):
    return requests.get(config.url + 'dm/details/v1', params={
        'token': token,
        'dm_id': dm_id
    })


def user_profile_v1_request(token, u_id):
    return requests.get(config.url + 'user/profile/v1', params={
        'token': token,
        'u_id': u_id
    })


def message_edit_v1_request(token, message_id, message):
    return requests.put(config.url + 'message/edit/v1', json={
        'token': token,
        'message_id': message_id,
        'message': message
    })


def user_profile_sethandle_v1_request(token, handle_str):
    return requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': token,
        'handle_str': handle_str
    })


def user_profile_setemail_v1_request(token, email):
    return requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': token,
        'email': email
    })


def user_profile_setname_v1_request(token, name_first, name_last):
    return requests.put(config.url + 'user/profile/setname/v1', json={
        'token': token,
        'name_first': name_first,
        'name_last': name_last
    })


def user_stats_v1_request(token):
	return requests.get(config.url + 'user/stats/v1', params={
		'token': token
	})

def message_remove_v1_request(token, message_id):
    return requests.delete(config.url + 'message/remove/v1', json={
        'token': token,
        'message_id': message_id
    })


def users_all_v1_request(token):
    return requests.get(config.url + 'users/all/v1', params={
        'token': token
    })

def users_stats_v1_request(token):
	return requests.get(config.url + 'users/stats/v1', params={
		'token': token
	})

def dm_messages_v1_request(token, dm_id, start):
    return requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id,
        'start': start
    })


def dm_list_v1_request(token):
    return requests.get(config.url + 'dm/list/v1', params={
        'token': token
    })


def dm_leave_v1_request(token, dm_id):
    return requests.post(config.url + 'dm/leave/v1', json={
        'token': token,
        'dm_id': dm_id
    })


def dm_remove_v1_request(token, dm_id):
    return requests.delete(config.url + 'dm/remove/v1', json={
        'token': token,
        'dm_id': dm_id
    })


def search_v1_request(token, query_str):
    return requests.get(config.url + 'search/v1', params={
        'token': token,
        'query_str': query_str
    })


def message_react_v1_request(token, message_id, react_id):
	return requests.post(config.url + 'message/react/v1', json={
		'token': token,
		'message_id': message_id,
		'react_id': react_id
	})

def message_unreact_v1_request(token, message_id, react_id):
	return requests.post(config.url + 'message/unreact/v1', json={
		'token': token,
		'message_id': message_id,
		'react_id': react_id
	})

def standup_start_v1_request(token, channel_id, length):
    return requests.post(config.url + 'standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })

def user_profile_uploadphoto_v1_request(token, img_url, x_start, y_start, x_end, y_end):
    return requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': token,
        'img_url': img_url,
        'x_start': x_start,
        'y_start': y_start,
        'x_end': x_end,
        'y_end': y_end
    })

def standup_active_v1_request(token, channel_id):
    return requests.get(config.url + 'standup/active/v1', params={
        'token': token,
        'channel_id': channel_id
    })

def message_pin_v1_request(token, message_id):
    return requests.post(config.url + 'message/pin/v1', json={
        'token': token,
        'message_id': message_id
    })

def message_unpin_v1_request(token, message_id):
    return requests.post(config.url + 'message/unpin/v1', json={
        'token': token,
        'message_id': message_id
    })
    
def standup_send_v1_request(token, channel_id, message):
    return requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

def notifications_get_v1_request(token):
    return requests.get(config.url + 'notifications/get/v1', params={
        'token': token
    })

def message_share_v1_request(token, og_message_id, message, channel_id, dm_id):
    return requests.post(config.url + 'message/share/v1', json={
        'token': token,
        'og_message_id': og_message_id,
        'message': message,
        'channel_id': channel_id,
        'dm_id': dm_id
    })

def message_sendlater_v1_request(token, channel_id, message, time_sent):
    return requests.post(config.url + 'message/sendlater/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent
    })

def message_sendlaterdm_v1_request(token, dm_id, message, time_sent):
    return requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent
    })
