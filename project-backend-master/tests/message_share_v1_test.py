import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def sender():
	return auth_register_v2_request("e@mail.com", "psword", "first", "last").json()['token']

@pytest.fixture
def channel1(sender):
	return channels_create_v2_request(sender, "channel1", True).json()['channel_id']

@pytest.fixture
def channel2(sender):
	return channels_create_v2_request(sender, "channel2", True).json()['channel_id']

@pytest.fixture
def user(channel1):
	user = auth_register_v2_request("u@mail.com", "psword", "first", "last").json()['token']
	channel_join_v2_request(user, channel1)
	return user

@pytest.fixture
def dm(sender):
	return dm_create_v1_request(sender, []).json()['dm_id']

@pytest.fixture
def message(sender, channel1):
	return message_send_v1_request(sender, channel1, "The world is flat").json()['message_id']


def test_status(sender, message, channel2):
	assert message_share_v1_request(sender, message, "This guy agrees", channel2, -1).status_code == 200

def test_channel_and_dm_invalid(sender, message):
	assert message_share_v1_request(sender, message, "Hi", 12345, 12345).status_code == 400

def test_channel_and_dm_not_neg1(sender, message, channel2, dm):
	assert message_share_v1_request(sender, message, "Hi", channel2, dm).status_code == 400

def test_channel_invalid(sender, message):
	assert message_share_v1_request(sender, message, "Hi", 12345, -1).status_code == 400

def test_invalid_message(sender, channel1):
	assert message_share_v1_request(sender, 12345, "Hi", channel1, -1).status_code == 400

def test_too_long(sender, channel1, message):
	assert message_share_v1_request(sender, message, "a" * 1000, channel1, -1).status_code == 200
	assert message_share_v1_request(sender, message, "a" * 1001, channel1, -1).status_code == 400

def test_not_member_channel(user, channel2, message):
	assert message_share_v1_request(user, message, "Hi", channel2, -1).status_code == 403

def test_not_member_dm(user, dm, message):
	assert message_share_v1_request(user, message, "Hi", -1, dm).status_code == 403

def test_shared_message_channel(sender, channel2, message):
	assert message_share_v1_request(sender, message, "Look at this idiot", channel2, -1).status_code == 200
	msg = channel_messages_v2_request(sender, channel2, 0).json()['messages'][0]['message']
	assert "Look at this idiot" in msg
	assert "The world is flat" in msg

def test_shared_message_dm(sender, dm, message):
	assert message_share_v1_request(sender, message, "Truer words were never spoken", -1, dm).status_code == 200
	msg = dm_messages_v1_request(sender, dm, 0).json()['messages'][0]['message']
	assert "Truer words were never spoken" in msg
	assert "The world is flat" in msg

def test_deleted_message(sender, channel1, message):
	message_remove_v1_request(sender, message)
	assert message_share_v1_request(sender, message, "Look at this", channel1, -1).status_code == 400

def test_edited_message(sender, channel1, message):
	message_edit_v1_request(sender, message, "uwu")
	message_share_v1_request(sender, message, "Look at this", channel1, -1).status_code == 200
	msg = channel_messages_v2_request(sender, channel1, 0).json()['messages'][0]['message']
	assert "Look at this" in msg
	assert "uwu" in msg

def test_invalid_token(channel1, message):
	assert message_share_v1_request("qwerty", message, "Hi", channel1, -1).status_code == 403