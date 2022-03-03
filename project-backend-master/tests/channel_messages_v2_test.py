import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	u_id = auth_register_v2_request("user@mail.com", "password", "first", "last").json()['token']
	return u_id

@pytest.fixture
def channel(user):
	c_id = channels_create_v2_request(user, "channel", True).json()['channel_id'] # User automatically added to channel
	return c_id

# Get the messages of a channel as a list of strings
def message_strings(token, channel, start):
	messages = channel_messages_v2_request(token, channel, start).json()['messages']
	return [m['message'] for m in messages]

# Tests:

def test_invalid_channel_id(user, channel):
	assert channel_messages_v2_request(user, -1, 0).status_code == 400
	assert channel_messages_v2_request(user, 5, 0).status_code == 400

def test_valid_no_messages(user, channel):
	assert channel_messages_v2_request(user, channel, 0).json() == {'messages': [], 'start':0, 'end':-1}

def test_messages_list_len(user, channel):
	assert 0 <= len(channel_messages_v2_request(user, channel, 0).json()['messages']) <= 50

def test_invalid_user(channel):
	assert channel_messages_v2_request(12365478, channel, 0).status_code == 403

def test_invalid_start(user, channel):
	assert channel_messages_v2_request(user, channel, 5).status_code == 400
	assert channel_messages_v2_request(user, channel, -5).status_code == 400

def test_not_member(channel):
	user_unauthorised = auth_register_v2_request("user2@mail.com", "password", "first", "last").json()['token']
	assert channel_messages_v2_request(user_unauthorised, channel, 0).status_code == 403

def test_single_message(user, channel):
	assert message_strings(user, channel, 0) == []
	message_send_v1_request(user, channel, "hello")
	assert message_strings(user, channel, 0) == ["hello"]

def test_10_messages(user, channel):
	msgs_10 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

	assert message_strings(user, channel, 0) == []
	
	for msg in msgs_10:
		message_send_v1_request(user, channel, msg)
	
	# All messages should be returned in reversed order
	assert channel_messages_v2_request(user, channel, 0).json()['start'] == 0
	assert channel_messages_v2_request(user, channel, 0).json()['end'] == -1
	assert message_strings(user, channel, 0) == ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0']

def test_50_messages(user, channel):
	# ['0', '1', ... , '49']
	msgs_50 = [f'{n}' for n in range(0,50)]

	assert message_strings(user, channel, 0) == []
	
	for msg in msgs_50:
		message_send_v1_request(user, channel, msg)
	
	# All messages should be returned in reversed order
	assert channel_messages_v2_request(user, channel, 0).json()['start'] == 0
	assert channel_messages_v2_request(user, channel, 0).json()['end'] == -1
	assert message_strings(user, channel, 0) == list(reversed(msgs_50))

def test_pagination_100(user, channel):
	# ['0', '1', ... , '99']
	msgs_100 = [f'{n}' for n in range(0,100)]

	assert message_strings(user, channel, 0) == []
	
	for msg in msgs_100:
		message_send_v1_request(user, channel, msg)
	
	# First page returns 0-49, second returns 50-99
	assert channel_messages_v2_request(user, channel, 0).json()['start'] == 0
	assert channel_messages_v2_request(user, channel, 0).json()['end'] == 50
	assert message_strings(user, channel, 0) == msgs_100[99:49:-1]

	assert channel_messages_v2_request(user, channel, 50).json()['start'] == 50
	assert channel_messages_v2_request(user, channel, 50).json()['end'] == -1
	assert message_strings(user, channel, 50) == msgs_100[49::-1]

def test_pagination_111(user, channel):
	# ['0', '1', ... , '110']
	msgs_111 = [f'{n}' for n in range(0,111)]

	assert message_strings(user, channel, 0) == []
	
	for msg in msgs_111:
		message_send_v1_request(user, channel, msg)
	
	assert channel_messages_v2_request(user, channel, 0).json()['start'] == 0
	assert channel_messages_v2_request(user, channel, 0).json()['end'] == 50
	assert message_strings(user, channel, 0) == msgs_111[110:60:-1]
	
	assert channel_messages_v2_request(user, channel, 50).json()['start'] == 50
	assert channel_messages_v2_request(user, channel, 50).json()['end'] == 100
	assert message_strings(user, channel, 50) == msgs_111[60:10:-1]
	
	assert channel_messages_v2_request(user, channel, 100).json()['start'] == 100
	assert channel_messages_v2_request(user, channel, 100).json()['end'] == -1
	assert message_strings(user, channel, 100) == msgs_111[10::-1]

def test_edited(user, channel):
	message_send_v1_request(user, channel, 'ASDFGHJ')
	message_send_v1_request(user, channel, 'ASDFGHJ')
	m_id = message_send_v1_request(user, channel, 'hello world!').json()['message_id']
	message_send_v1_request(user, channel, 'ASDFGHJ')
	message_send_v1_request(user, channel, 'ASDFGHJ')

	assert message_strings(user, channel, 0) == ['ASDFGHJ', 'ASDFGHJ', 'hello world!', 'ASDFGHJ', 'ASDFGHJ']

	message_edit_v1_request(user, m_id, 'goodbye world!')

	assert message_strings(user, channel, 0) == ['ASDFGHJ', 'ASDFGHJ', 'goodbye world!', 'ASDFGHJ', 'ASDFGHJ']

def test_removed(user, channel):
	message_send_v1_request(user, channel, 'ASDFGHJ')
	message_send_v1_request(user, channel, 'ASDFGHJ')
	m_id = message_send_v1_request(user, channel, 'hello world!').json()['message_id']
	message_send_v1_request(user, channel, 'ASDFGHJ')
	message_send_v1_request(user, channel, 'ASDFGHJ')

	assert message_strings(user, channel, 0) == ['ASDFGHJ', 'ASDFGHJ', 'hello world!', 'ASDFGHJ', 'ASDFGHJ']

	message_remove_v1_request(user, m_id)

	assert message_strings(user, channel, 0) == ['ASDFGHJ', 'ASDFGHJ', 'ASDFGHJ', 'ASDFGHJ']