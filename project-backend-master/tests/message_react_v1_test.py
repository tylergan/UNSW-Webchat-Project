import re
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
	return message_send_v1_request(user, channel, "Hello world").json()['message_id']

#=== Tests ===

def test_status(user, message):
	assert message_react_v1_request(user, message, 1).status_code == 200

def test_return(user, message):
	assert message_react_v1_request(user, message, 1).json() == {}

def test_invalid_message(user):
	assert message_react_v1_request(user, -999, 1).status_code == 400

def test_user_not_in_channel(user, user2):
	channel2 = channels_create_v2_request(user2, "channel2", True).json()['channel_id']
	message2 = message_send_v1_request(user2, channel2, "Goodbye world").json()['message_id']

	assert message_react_v1_request(user, message2, 1).status_code == 400

def test_user_not_in_dm(user, user2):
	dm = dm_create_v1_request(user2, []).json()['dm_id']
	message2 = message_senddm_v1_request(user2, dm, "Goodbye world").json()['message_id']

	assert message_react_v1_request(user, message2, 1).status_code == 400

def test_invalid_react_id(user, message):
	assert message_react_v1_request(user, message, -999).status_code == 400

def test_already_reacted(user, message):
	assert message_react_v1_request(user, message, 1).status_code == 200
	assert message_react_v1_request(user, message, 1).status_code == 400

def test_already_reacted_other_user(user, channel, message):
	user2 = auth_register_v2_request("u2@mail.com", "psword", "first", "last").json()['token']
	channel_join_v2_request(user2, channel)

	assert message_react_v1_request(user2, message, 1).status_code == 200
	assert message_react_v1_request(user2, message, 1).status_code == 400
	assert message_react_v1_request(user, message, 1).status_code == 200
	assert message_react_v1_request(user, message, 1).status_code == 400

def test_invalid_token(user, message):
	assert message_react_v1_request("qwerty", message, 1).status_code == 403

	assert message_react_v1_request("~" + user[1:], message, 1).status_code == 403

	auth_logout_v1_request(user)
	assert message_react_v1_request(user, message, 1).status_code == 403

def test_reaction_shows_in_channel_messages(user, channel, message, user2):
	u1id = auth_login_v2_request("e@mail.com", "psword").json()['auth_user_id']
	u2id = auth_login_v2_request("u2@mail.com", "psword").json()['auth_user_id']
	assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [],
		'is_this_user_reacted': False
	}]
	message_react_v1_request(user, message, 1)

	# Ensure that the correct react list is shown for user
	assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id],
		'is_this_user_reacted': True
	}]

	# user2 should see the same except for is_this_user_reacted
	channel_join_v2_request(user2, channel)
	assert channel_messages_v2_request(user2, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id],
		'is_this_user_reacted': False
	}]

	message_react_v1_request(user2, message, 1)
	
	assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id, u2id],
		'is_this_user_reacted': True
	}]

def test_reaction_shows_in_dm_messages(user, user2):
	u1id = auth_login_v2_request("e@mail.com", "psword").json()['auth_user_id']
	u2id = auth_login_v2_request("u2@mail.com", "psword").json()['auth_user_id']

	dm = dm_create_v1_request(user, [u2id]).json()['dm_id']
	
	message = message_senddm_v1_request(user, dm, "Hi").json()['message_id']

	assert dm_messages_v1_request(user, dm, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [],
		'is_this_user_reacted': False
	}]
	
	message_react_v1_request(user, message, 1)

	# Ensure that the correct react list is shown for user
	assert dm_messages_v1_request(user, dm, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id],
		'is_this_user_reacted': True
	}]

	# user2 should see the same except for is_this_user_reacted
	assert dm_messages_v1_request(user2, dm, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id],
		'is_this_user_reacted': False
	}]

	message_react_v1_request(user2, message, 1)
	
	assert dm_messages_v1_request(user, dm, 0).json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id, u2id],
		'is_this_user_reacted': True
	}]

def test_reaction_shows_in_search(user, message):
	u1id = auth_login_v2_request("e@mail.com", "psword").json()['auth_user_id']
	assert search_v1_request(user, "ello").json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [],
		'is_this_user_reacted': False	
	}]
	message_react_v1_request(user, message, 1)
	assert search_v1_request(user, "ello").json()['messages'][0]['reacts'] == [{
		'react_id': 1,
		'u_ids': [u1id],
		'is_this_user_reacted': True	
	}]