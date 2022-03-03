import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request('e@mail.com', "psword", "first", "last").json()['token']

@pytest.fixture
def user2():
	return auth_register_v2_request('u2@mail.com', "psword", "first", "last").json()['token']

@pytest.fixture
def channel(user):
	return channels_create_v2_request(user, "channel", True).json()['channel_id']

@pytest.fixture
def message(user, channel):
	message = message_send_v1_request(user, channel, "Hello world").json()['message_id']
	assert message_react_v1_request(user, message, 1).status_code == 200
	return message

#=== Tests ===

def test_status(user, message):
	assert message_unreact_v1_request(user, message, 1).status_code == 200

def test_return(user, message):
	assert message_unreact_v1_request(user, message, 1).json() == {}

def test_invalid_react_id(user, message):
	assert message_unreact_v1_request(user, message, -1).status_code == 400

def test_no_reacts(user, channel):
	msg = message_send_v1_request(user, channel, "Hi").json()['message_id']
	assert message_unreact_v1_request(user, msg, 1).status_code == 400

def test_other_user_react(user, user2, channel):
	msg = message_send_v1_request(user, channel, "Hi").json()['message_id']
	channel_join_v2_request(user2, channel)
	message_react_v1_request(user2, msg, 1)
	assert message_unreact_v1_request(user, msg, 1).status_code == 400

def test_invalid_message(user):
	assert message_unreact_v1_request(user, 12345678, 1).status_code == 400

def test_invalid_token(user, message):
	assert message_unreact_v1_request("qwerty", message, 1).status_code == 403
	assert message_unreact_v1_request('~' + user[1:], message, 1).status_code == 403
	auth_logout_v1_request(user)
	assert message_unreact_v1_request(user, message, 1).status_code == 403

def test_react_gone(user, message, channel):
	message_unreact_v1_request(user, message, 1)
	assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [],
		'is_this_user_reacted': False
	}]

def test_react_gone_multiple_users(user, message, user2, channel):
	channel_join_v2_request(user2, channel)
	message_react_v1_request(user2, message, 1)
	message_unreact_v1_request(user, message, 1)
	u2_id = auth_login_v2_request('u2@mail.com', "psword").json()['auth_user_id']
	assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u2_id],
		'is_this_user_reacted': False
	}]

def test_not_member(user2, channel):
	channel_join_v2_request(user2, channel)
	msg = message_send_v1_request(user2, channel, "Hi").json()['message_id']
	message_react_v1_request(user2, msg, 1)
	channel_leave_v1_request(user2, channel)
	assert message_unreact_v1_request(user2, msg, 1).status_code == 400