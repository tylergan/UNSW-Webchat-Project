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
def dm(user):
	dm_id = dm_create_v1_request(user, []).json()['dm_id']
	return dm_id

# Get the messages of a channel as a list of strings
def message_strings(token, dm, start):
	messages = dm_messages_v1_request(token, dm, start).json()['messages']
	return [m['message'] for m in messages]

def test_invalid_dm_id(user, dm):
	assert dm_messages_v1_request(user, -1, 0).status_code == 400
	assert dm_messages_v1_request(user, 5, 0).status_code == 400

def test_valid_no_messages(user, dm):
	assert dm_messages_v1_request(user, dm, 0).json() == {'messages': [], 'start':0, 'end':-1}

def test_messages_list_len(user, dm):
	assert 0 <= len(dm_messages_v1_request(user, dm, 0).json()['messages']) <= 50

def test_invalid_user(dm):
	assert dm_messages_v1_request(12365478, dm, 0).status_code == 403

def test_invalid_start(user, dm):
	assert dm_messages_v1_request(user, dm, 5).status_code == 400
	assert dm_messages_v1_request(user, dm, -5).status_code == 400

def test_not_member(dm):
	user_unauthorised = auth_register_v2_request("user2@mail.com", "password", "first", "last").json()['token']
	assert dm_messages_v1_request(user_unauthorised, dm, 0).status_code == 403


def test_single_message(user, dm):
	assert message_strings(user, dm, 0) == []
	message_senddm_v1_request(user, dm, "hello")
	assert message_strings(user, dm, 0) == ["hello"]

def test_10_messages(user, dm):
	msgs_10 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

	assert message_strings(user, dm, 0) == []
	
	for msg in msgs_10:
		message_senddm_v1_request(user, dm, msg)
	
	# All messages should be returned in reversed order
	assert dm_messages_v1_request(user, dm, 0).json()['start'] == 0
	assert dm_messages_v1_request(user, dm, 0).json()['end'] == -1
	assert message_strings(user, dm, 0) == ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0']

def test_50_messages(user, dm):
	# ['0', '1', ... , '49']
	msgs_50 = [f'{n}' for n in range(0,50)]

	assert message_strings(user, dm, 0) == []
	
	for msg in msgs_50:
		message_senddm_v1_request(user, dm, msg)
	
	# All messages should be returned in reversed order
	assert dm_messages_v1_request(user, dm, 0).json()['start'] == 0
	assert dm_messages_v1_request(user, dm, 0).json()['end'] == -1
	assert message_strings(user, dm, 0) == list(reversed(msgs_50))

def test_pagination_100(user, dm):
	# ['0', '1', ... , '99']
	msgs_100 = [f'{n}' for n in range(0,100)]

	assert message_strings(user, dm, 0) == []
	
	for msg in msgs_100:
		message_senddm_v1_request(user, dm, msg)
	
	# First page returns 0-49, second returns 50-99
	assert dm_messages_v1_request(user, dm, 0).json()['start'] == 0
	assert dm_messages_v1_request(user, dm, 0).json()['end'] == 50
	assert message_strings(user, dm, 0) == msgs_100[99:49:-1]

	assert dm_messages_v1_request(user, dm, 50).json()['start'] == 50
	assert dm_messages_v1_request(user, dm, 50).json()['end'] == -1
	assert message_strings(user, dm, 50) == msgs_100[49::-1]

def test_pagination_111(user, dm):
	# ['0', '1', ... , '110']
	msgs_111 = [f'{n}' for n in range(0,111)]

	assert message_strings(user, dm, 0) == []
	
	for msg in msgs_111:
		message_senddm_v1_request(user, dm, msg)
	
	assert dm_messages_v1_request(user, dm, 0).json()['start'] == 0
	assert dm_messages_v1_request(user, dm, 0).json()['end'] == 50
	assert message_strings(user, dm, 0) == msgs_111[110:60:-1]
	
	assert dm_messages_v1_request(user, dm, 50).json()['start'] == 50
	assert dm_messages_v1_request(user, dm, 50).json()['end'] == 100
	assert message_strings(user, dm, 50) == msgs_111[60:10:-1]
	
	assert dm_messages_v1_request(user, dm, 100).json()['start'] == 100
	assert dm_messages_v1_request(user, dm, 100).json()['end'] == -1
	assert message_strings(user, dm, 100) == msgs_111[10::-1]

def test_edited(user, dm):
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	m_id = message_senddm_v1_request(user, dm, 'hello world!').json()['message_id']
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	message_senddm_v1_request(user, dm, 'ASDFGHJ')

	assert message_strings(user, dm, 0) == ['ASDFGHJ', 'ASDFGHJ', 'hello world!', 'ASDFGHJ', 'ASDFGHJ']

	message_edit_v1_request(user, m_id, 'goodbye world!')

	assert message_strings(user, dm, 0) == ['ASDFGHJ', 'ASDFGHJ', 'goodbye world!', 'ASDFGHJ', 'ASDFGHJ']

def test_removed(user, dm):
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	m_id = message_senddm_v1_request(user, dm, 'hello world!').json()['message_id']
	message_senddm_v1_request(user, dm, 'ASDFGHJ')
	message_senddm_v1_request(user, dm, 'ASDFGHJ')

	assert message_strings(user, dm, 0) == ['ASDFGHJ', 'ASDFGHJ', 'hello world!', 'ASDFGHJ', 'ASDFGHJ']

	message_remove_v1_request(user, m_id)

	assert message_strings(user, dm, 0) == ['ASDFGHJ', 'ASDFGHJ', 'ASDFGHJ', 'ASDFGHJ']