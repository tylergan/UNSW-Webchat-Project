import pytest
from src.make_request_test import *
from datetime import datetime, timezone
from time import sleep

def t_eq(a, b):
	return abs(a - b) <= 1

# Reset application data before each test is run
@pytest.fixture(autouse=True)
def clear_data():
	clear_v1_request()

@pytest.fixture
def owner():
	return auth_register_v2_request("name1@email.com", "password", "firstname", "lastname").json()

@pytest.fixture
def member1(owner):
	return auth_register_v2_request("name2@email.com", "password", "1firstname", "1lastname").json()

@pytest.fixture
def member2(owner):
	return auth_register_v2_request("name3@email.com", "password", "2firstname", "2lastname").json()

@pytest.fixture
def channel1(member1):
	return channels_create_v2_request(member1['token'], "channel1", True).json()['channel_id']

@pytest.fixture
def channel2(member2, member1):
	channel_id = channels_create_v2_request(member2['token'], "channel2", False).json()['channel_id']
	channel_invite_v2_request(member2['token'], channel_id, member1['auth_user_id'])
	return channel_id

@pytest.fixture
def channel3(owner, member1):
	channel_id = channels_create_v2_request(owner['token'], "channel3", True).json()['channel_id']
	channel_join_v2_request(member1['token'], channel_id)
	return channel_id

@pytest.fixture
def dm1(member1, owner):
	return dm_create_v1_request(member1['token'], [owner['auth_user_id']]).json()['dm_id']

@pytest.fixture
def dm2(member1, member2, owner):
	return dm_create_v1_request(member2['token'], [owner['auth_user_id'], member1['auth_user_id']]).json()['dm_id']

def test_invalid_token():
	assert user_stats_v1_request('mentlegen').status_code == 403

def test_return_type_simple(member1):
	resp = user_stats_v1_request(member1['token']).json()
	assert len(resp['user_stats']) == 4

def test_no_involvement(owner):
	token = auth_register_v2_request("name0@email.com", "password", "firstname", "lastname").json()['token']
	assert user_stats_v1_request(token).json()['user_stats']['involvement_rate'] == 0 
	
def test_involvement_rate(owner, member1, member2, channel1, channel2, channel3, dm1, dm2):
	message_send_v1_request(member1['token'], channel1, 'Hello')
	message_send_v1_request(member1['token'], channel1, 'Goodbye')
	message_send_v1_request(member1['token'], channel2, 'Hello')
	message_send_v1_request(member1['token'], channel2, 'Goodbye')
	message_send_v1_request(member1['token'], channel3, 'Hello')
	message_send_v1_request(member1['token'], channel3, 'Goodbye')
	message_send_v1_request(member1['token'], dm1, 'Hello')
	message_send_v1_request(member1['token'], dm1, 'Goodbye')
	message_send_v1_request(member1['token'], dm2, 'Hello')
	message_send_v1_request(member1['token'], dm2, 'Goodbye')
	
	assert user_stats_v1_request(member1['token']).status_code == 200
	assert user_stats_v1_request(member1['token']).json()['user_stats']['involvement_rate'] == 1

	ownerchannel = channels_create_v2_request(owner['token'], 'ownerchannel', False).json()['channel_id']

	message_send_v1_request(member1['token'], channel1, 'Hello')
	message_send_v1_request(member2['token'], channel2, 'Hello')
	message_send_v1_request(owner['token'], channel3, 'Hello')
	message_send_v1_request(owner['token'], ownerchannel, 'This is my sneaky private channel')

	assert user_stats_v1_request(member1['token']).status_code == 200
	assert user_stats_v1_request(member1['token']).json()['user_stats']['involvement_rate'] == (16/20)

	message_send_v1_request(member1['token'], dm1, 'Hello')
	message_send_v1_request(member2['token'], dm2, 'Hello')

	assert user_stats_v1_request(member1['token']).status_code == 200
	assert user_stats_v1_request(member1['token']).json()['user_stats']['involvement_rate'] == (17/22)

def test_time_records(owner, member1):
	time = []
	time.append(int(datetime.now(timezone.utc).timestamp()))

	stats = user_stats_v1_request(member1['token']).json()['user_stats']
	assert t_eq(stats['channels_joined'][0]['time_stamp'], time[0])
	assert t_eq(stats['dms_joined'][0]['time_stamp'], time[0])
	assert t_eq(stats['messages_sent'][0]['time_stamp'], time[0])

	time.append(int(datetime.now(timezone.utc).timestamp()))
	channel_id = channels_create_v2_request(member1['token'], 'channel1', True).json()['channel_id']
	time.append(int(datetime.now(timezone.utc).timestamp()))
	dm_id = dm_create_v1_request(member1['token'], [owner['auth_user_id']]).json()['dm_id']

	stats = user_stats_v1_request(member1['token']).json()['user_stats']
	assert t_eq(stats['channels_joined'][0]['time_stamp'], time[0])
	assert t_eq(stats['channels_joined'][1]['time_stamp'], time[1])
	assert stats['channels_joined'][0]['num_channels_joined'] == 0
	assert stats['channels_joined'][1]['num_channels_joined'] == 1
	assert t_eq(stats['dms_joined'][0]['time_stamp'], time[0])
	assert t_eq(stats['dms_joined'][1]['time_stamp'], time[1])
	assert stats['dms_joined'][0]['num_dms_joined'] == 0
	assert stats['dms_joined'][1]['num_dms_joined'] == 1


	sleep(1)
	time.append(int(datetime.now(timezone.utc).timestamp()))
	message_send_v1_request(member1['token'], channel_id, 'Hello')

	time.append(int(datetime.now(timezone.utc).timestamp()))
	message_send_v1_request(member1['token'], dm_id, 'Hello')

	stats = user_stats_v1_request(member1['token']).json()['user_stats']
	assert t_eq(stats['messages_sent'][0]['time_stamp'], time[0])
	assert t_eq(stats['messages_sent'][1]['time_stamp'], time[3])
	assert t_eq(stats['messages_sent'][2]['time_stamp'], time[4])
	assert stats['messages_sent'][0]['num_messages_sent'] == 0
	assert stats['messages_sent'][1]['num_messages_sent'] == 1
	assert stats['messages_sent'][2]['num_messages_sent'] == 2