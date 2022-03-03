import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def global_owner():
	return auth_register_v2_request('u4@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def ch_owner(global_owner):
	return auth_register_v2_request('u@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def user(global_owner):
	return auth_register_v2_request('u2@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def ch_pub(ch_owner):
	return channels_create_v2_request(ch_owner, "public", True).json()['channel_id']

@pytest.fixture
def msg(ch_pub, ch_owner):
	return message_send_v1_request(ch_owner, ch_pub, "message").json()['message_id']

### Tests ###

def test_status_code(ch_owner, msg):
	assert message_remove_v1_request(ch_owner, msg).status_code == 200

def test_return_type(ch_owner, msg):
	assert message_remove_v1_request(ch_owner, msg).json() == {}

def test_invalid_token(ch_owner, msg):
	# Not a token
	assert message_remove_v1_request(ch_owner, msg).status_code == 200
	assert message_remove_v1_request("QWERTY", msg).status_code == 403

	# Tampered token
	assert message_remove_v1_request(ch_owner[:-1] + '~', msg).status_code == 403
	
def test_session_ended(ch_owner, msg):
	auth_logout_v1_request(ch_owner)
	assert message_remove_v1_request(ch_owner, msg).status_code == 403

def test_invalid_msg_id(ch_owner):
	assert message_remove_v1_request(ch_owner, 12346578).status_code == 400

def test_msg_in_different_channel(user, msg):
	# User attempts to remove a valid message, but in a channel they're not a member of
	assert message_remove_v1_request(user, msg).status_code == 400

def test_global_owner_remove(global_owner, ch_pub, msg):
	channel_join_v2_request(global_owner, ch_pub)
	assert message_remove_v1_request(global_owner, msg).status_code == 200

def test_ch_owner_remove(ch_owner, user, ch_pub):
	channel_join_v2_request(user, ch_pub)
	m_id = message_send_v1_request(user, ch_pub, "message").json()['message_id']
	assert message_remove_v1_request(ch_owner, m_id).status_code == 200

def test_not_sender_remove(user, ch_pub, msg):
	channel_join_v2_request(user, ch_pub)
	assert message_remove_v1_request(user, msg).status_code == 403

def test_message_gone(ch_owner, msg, ch_pub):
	assert channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'][0]['message'] == 'message'
	message_remove_v1_request(ch_owner, msg)
	assert channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'] == []

def test_message_gone_global_owner(global_owner, msg, ch_pub):
	channel_join_v2_request(global_owner, ch_pub)
	assert channel_messages_v2_request(global_owner, ch_pub, 0).json()['messages'][0]['message'] == 'message'
	message_remove_v1_request(global_owner, msg)
	assert channel_messages_v2_request(global_owner, ch_pub, 0).json()['messages'] == []

def test_remove_twice(ch_owner, msg):
	assert message_remove_v1_request(ch_owner, msg).status_code == 200
	assert message_remove_v1_request(ch_owner, msg).status_code == 400

def test_dm():
	dm_owner = auth_register_v2_request("e@mail.com", "psword", "first", "last").json()['token']
	dm = dm_create_v1_request(dm_owner, []).json()['dm_id']
	msg = message_senddm_v1_request(dm_owner, dm, "hello").json()['message_id']
	assert dm_messages_v1_request(dm_owner, dm, 0).json()['messages'][0]['message'] == "hello"
	message_remove_v1_request(dm_owner, msg)
	assert dm_messages_v1_request(dm_owner, dm, 0).json()['messages'] == []