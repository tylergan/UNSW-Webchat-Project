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
	member = auth_register_v2_request("namech@email.com", "password", "firstname", "lastname").json()['token']
	return channels_create_v2_request(member, "channel", True).json()['channel_id']

def test_invalid_token(owner, channel):
	assert channel_leave_v1_request('goodeveninggentlemen', channel).status_code == 403

def test_invalid_channel_id(owner, channel):
	assert channel_leave_v1_request(owner['token'], 68).status_code == 400
	channel_join_v2_request(owner['token'], channel)
	assert channel_leave_v1_request(owner['token'], 69).status_code == 400

def test_all_invalid_inputs(owner, channel):
	assert channel_leave_v1_request('whatsfunnierthan24', 420).status_code == 403

def test_not_channel_member(member1, channel):
	assert channel_leave_v1_request(member1['token'], channel).status_code == 403

def test_successful_member_leave(owner, member1, channel):
	channel_join_v2_request(member1['token'], channel)
	channel_join_v2_request(owner['token'], channel)
	message_send_v1_request(owner['token'], channel, 'skibiddy bop')
	message_send_v1_request(member1['token'], channel, 'mmm dada')

	assert channel_leave_v1_request(member1['token'], channel).status_code == 200
	assert channel_leave_v1_request(member1['token'], channel).status_code == 403

	assert channel_messages_v2_request(owner['token'], channel, 2).status_code == 200
	assert channel_messages_v2_request(owner['token'], channel, 3).status_code == 400

def test_successful_channel_abandon(owner, member1, member2):
	channel = channels_create_v2_request(member1['token'], 'chanel no5', True).json()['channel_id']
	channel_join_v2_request(owner['token'], channel)
	channel_join_v2_request(member2['token'], channel)
	message_send_v1_request(owner['token'], channel, 'skibiddy bop')
	message_send_v1_request(member1['token'], channel, 'mmm dada')

	assert channel_leave_v1_request(owner['token'], channel).status_code == 200
	assert channel_leave_v1_request(member1['token'], channel).status_code == 200
	assert channel_leave_v1_request(member1['token'], channel).status_code == 403

	assert channel_messages_v2_request(member2['token'], channel, 2).status_code == 200
	assert channel_messages_v2_request(member2['token'], channel, 3).status_code == 400
