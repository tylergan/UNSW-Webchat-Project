import pytest
from src.make_request_test import *

# Reset application data before each test is run
@pytest.fixture(autouse=True)
def clear_data():
	clear_v1_request()

@pytest.fixture
def owner():
	return auth_register_v2_request("name1@email.com", "password", "firstname", "lastname").json()

@pytest.fixture
def member1():
	# Ensure user isn't global owner
	auth_register_v2_request("name2@email.com", "password", "firstname", "lastname")

	return auth_register_v2_request("name3@email.com", "password", "1firstname", "1lastname").json()

@pytest.fixture
def member2():
	# Ensure user isn't global owner
	auth_register_v2_request("name4@email.com", "password", "firstname", "lastname")

	return auth_register_v2_request("name5@email.com", "password", "2firstname", "2lastname").json()

@pytest.fixture
def channel():
	member1 = auth_register_v2_request("namech@email.com", "password", "firstname", "lastname").json()['token']
	return channels_create_v2_request(member1, "channel", True).json()['channel_id']

def test_invalid_token(owner, member1):
	assert admin_user_remove_v1_request('goodeveningmgentlemen', member1['auth_user_id']).status_code == 403

def test_invalid_u_id(owner):
	assert admin_user_remove_v1_request(owner['token'], 1).status_code == 400

def test_non_owner_useage(owner, member1):
	assert admin_user_remove_v1_request(member1['token'], owner['auth_user_id']).status_code == 403
	assert admin_user_remove_v1_request(member1['token'], member1['auth_user_id']).status_code == 403

def test_solo_owner_removal(owner):
	assert admin_user_remove_v1_request(owner['token'], owner['auth_user_id']).status_code == 400

def test_successful_owner_removes_member1(owner, member1, member2, channel):
	# Add member1 to a channel and have them send a message
	channel_join_v2_request(member1['token'], channel)
	channel_join_v2_request(owner['token'], channel)
	message_send_v1_request(member1['token'], channel, 'It is time...')
	message_send_v1_request(member1['token'], channel, 'Goodbye, cruel world')
	message_send_v1_request(member2['token'], channel, 'lmfao')

	# Have member1 and owner create a channel each
	channels_create_v2_request(member1['token'], 'achannel', True)
	channels_create_v2_request(owner['token'], 'anotherchannel', False)

	# have member1 make a dm with member2 and have them send a message
	dm_id = dm_create_v1_request(member1['token'], [owner['auth_user_id'], member2['auth_user_id']]).json()['dm_id']
	message_senddm_v1_request(member1['token'], dm_id, 'Change da worl')
	message_senddm_v1_request(member1['token'], dm_id, 'My final message...')
	message_senddm_v1_request(member1['token'], dm_id, 'Goodbye')
	message_senddm_v1_request(member2['token'], dm_id, 'lmfao delete this cringel0rd')
	message_senddm_v1_request(owner['token'], dm_id, 'way ahead of you')

	# Have member2 make a dm with member1, and another with owner
	dm_create_v1_request(member2['token'], [member1['auth_user_id']])
	dm_create_v1_request(owner['token'], [member2['auth_user_id']])

	# set a handle
	user_profile_sethandle_v1_request(member1['token'], 'l8rallig8r')

	assert admin_user_remove_v1_request(owner['token'], member1['auth_user_id']).status_code == 200

	# check member is no longer in channel
	assert message_send_v1_request(member1['token'], channel, 'I am kill').status_code == 403

	# check member is no longer in dm
	assert dm_leave_v1_request(member1['token'], dm_id).status_code == 403

	# check user profile is still retrieveable
	assert user_profile_v1_request(owner['token'], member1['auth_user_id']).status_code == 200

	# check email and handle reusable
	assert user_profile_setemail_v1_request(member2['token'], 'name3@email.com').status_code == 200
	assert user_profile_sethandle_v1_request(member2['token'], 'l8rallig8r').status_code == 200

	# check that profile of removed user has been updated
	profile = user_profile_v1_request(owner['token'], member1['auth_user_id']).json()['user']
	assert profile['name_first'] == 'Removed'
	assert profile['name_last'] == 'user'

def test_successful_owner_removes_owner(owner, member1, member2, channel):
	# Make member1 an owner
	admin_userpermission_change_v1_request(owner['token'], member1['auth_user_id'], 1)

	# Add member1 to a channel and have them send a message
	channel_join_v2_request(member1['token'], channel)
	channel_join_v2_request(owner['token'], channel)
	message_send_v1_request(member1['token'], channel, 'It is time...')
	message_send_v1_request(member1['token'], channel, 'Goodbye, cruel world')
	message_send_v1_request(member2['token'], channel, 'lmfao')

	# Have member1 and owner create a channel each
	channels_create_v2_request(member1['token'], 'achannel', True)
	channels_create_v2_request(owner['token'], 'anotherchannel', False)

	# Have member1 make a dm with member2 and have them send a message
	dm_id = dm_create_v1_request(member1['token'], [owner['auth_user_id'], member2['auth_user_id']]).json()['dm_id']
	message_senddm_v1_request(member1['token'], dm_id, 'Change da worl')
	message_senddm_v1_request(member1['token'], dm_id, 'My final message...')
	message_senddm_v1_request(member1['token'], dm_id, 'Goodbye')
	message_senddm_v1_request(member2['token'], dm_id, 'lmfao delete this cringel0rd')
	message_senddm_v1_request(owner['token'], dm_id, 'way ahead of you')

	# Have member2 make a dm with member1, and another with owner
	dm_create_v1_request(member2['token'], [member1['auth_user_id']])
	dm_create_v1_request(owner['token'], [member2['auth_user_id']])

	# set a handle
	user_profile_sethandle_v1_request(member1['token'], 'l8rallig8r')

	assert admin_user_remove_v1_request(owner['token'], member1['auth_user_id']).status_code == 200

	# check member is no longer in channel
	assert message_send_v1_request(member1['token'], channel, 'I am kill').status_code == 403

	# check member is no longer in dm
	assert dm_leave_v1_request(member1['token'], dm_id).status_code == 403

	# check user profile is still retrieveable
	assert user_profile_v1_request(owner['token'], member1['auth_user_id']).status_code == 200

	# check email and handle reusable
	assert user_profile_setemail_v1_request(member2['token'], 'name3@email.com').status_code == 200
	assert user_profile_sethandle_v1_request(member2['token'], 'l8rallig8r').status_code == 200

def test_messages_updated(owner, member1, channel):
	channel_join_v2_request(owner['token'], channel)
	channel_join_v2_request(member1['token'], channel)

	message_send_v1_request(member1['token'], channel, "hello world")
	message_send_v1_request(member1['token'], channel, "hello again")

	assert channel_messages_v2_request(owner['token'], channel, 0).json()['messages'][1]['message'] == "hello world"
	assert channel_messages_v2_request(owner['token'], channel, 0).json()['messages'][0]['message'] == "hello again"

	admin_user_remove_v1_request(owner['token'], member1['auth_user_id'])
	
	assert channel_messages_v2_request(owner['token'], channel, 0).json()['messages'][1]['message'] == "Removed user"
	assert channel_messages_v2_request(owner['token'], channel, 0).json()['messages'][0]['message'] == "Removed user"

def test_removed_session(owner, member1):
	assert channels_listall_v2_request(member1['token']).status_code == 200
	admin_user_remove_v1_request(owner['token'], member1['auth_user_id'])
	assert channels_listall_v2_request(member1['token']).status_code == 403

def test_removed_login(owner, member1):
	assert auth_login_v2_request("name3@email.com", "password").status_code == 200
	admin_user_remove_v1_request(owner['token'], member1['auth_user_id'])
	assert auth_login_v2_request("name3@email.com", "password").status_code == 400