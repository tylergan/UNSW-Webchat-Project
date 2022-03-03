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
	assert message_edit_v1_request(ch_owner, msg, "new_message").status_code == 200

def test_return_type(ch_owner, msg):
	assert message_edit_v1_request(ch_owner, msg, "new_message").json() == {}


def test_invalid_token(ch_owner, msg, ch_pub):
	# Not a token
	assert message_edit_v1_request(ch_owner, msg, "new_message").status_code == 200
	assert message_edit_v1_request("QWERTY", msg, "new_message").status_code == 403

	# Tampered token
	assert message_edit_v1_request(ch_owner[:-1] + '~', msg, "new_message").status_code == 403
	
	# Session ended
	assert message_edit_v1_request(ch_owner, msg, "new_message").status_code == 200
	auth_logout_v1_request(ch_owner)
	assert message_edit_v1_request(ch_owner, msg, "new_message").status_code == 403

def test_too_long(ch_owner, msg):
	assert message_edit_v1_request(ch_owner, msg, "a" * 1000).status_code == 200
	assert message_edit_v1_request(ch_owner, msg, "a" * 1001).status_code == 400

def test_invalid_msg_id(ch_owner):
	assert message_edit_v1_request(ch_owner, 12346578, "new_message").status_code == 400

def test_msg_in_different_channel(user, msg):
	# User attempts to edit a valid message, but in a channel they're not a member of
	assert message_edit_v1_request(user, msg, "new_message").status_code == 400

def test_global_owner_edit(global_owner, ch_pub, msg):
	channel_join_v2_request(global_owner, ch_pub)
	assert message_edit_v1_request(global_owner, msg, "new_message").status_code == 200

def test_ch_owner_edit(ch_owner, user, ch_pub):
	channel_join_v2_request(user, ch_pub)
	m_id = message_send_v1_request(user, ch_pub, "message").json()['message_id']
	assert message_edit_v1_request(ch_owner, m_id, "new_message").status_code == 200

def test_not_sender_edit(user, ch_pub, msg):
	channel_join_v2_request(user, ch_pub)
	assert message_edit_v1_request(user, msg, "new_message").status_code == 403

def test_message_contents(ch_owner, msg, ch_pub):
	assert channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'][0]['message'] == 'message'
	message_edit_v1_request(ch_owner, msg, "new_message")
	assert channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'][0]['message'] == 'new_message'
	message_edit_v1_request(ch_owner, msg, "asdjkhfahsdgkjfhagsdfg")
	assert channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'][0]['message'] == 'asdjkhfahsdgkjfhagsdfg'

def test_message_contents_global_owner(global_owner, msg, ch_pub):
	channel_join_v2_request(global_owner, ch_pub)
	assert channel_messages_v2_request(global_owner, ch_pub, 0).json()['messages'][0]['message'] == 'message'
	message_edit_v1_request(global_owner, msg, "new_message")
	assert channel_messages_v2_request(global_owner, ch_pub, 0).json()['messages'][0]['message'] == 'new_message'
	message_edit_v1_request(global_owner, msg, "lkjhklsfdhglskdfjhg")
	assert channel_messages_v2_request(global_owner, ch_pub, 0).json()['messages'][0]['message'] == 'lkjhklsfdhglskdfjhg'

def test_delete(ch_owner, msg, ch_pub):
	assert message_edit_v1_request(ch_owner, msg, "").status_code == 200
	# Ensure that no message matching the ID exists
	assert not any(m['message_id'] == msg for m in \
		channel_messages_v2_request(ch_owner, ch_pub, 0).json()['messages'])

def test_dm():
	dm_owner = auth_register_v2_request("e@mail.com", "psword", "first", "last").json()['token']
	dm = dm_create_v1_request(dm_owner, []).json()['dm_id']
	msg = message_senddm_v1_request(dm_owner, dm, "hello").json()['message_id']
	assert dm_messages_v1_request(dm_owner, dm, 0).json()['messages'][0]['message'] == "hello"
	message_edit_v1_request(dm_owner, msg, "newmessage")
	assert dm_messages_v1_request(dm_owner, dm, 0).json()['messages'][0]['message'] == "newmessage"