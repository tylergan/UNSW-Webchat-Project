import pytest
from src.make_request_test import *
import time
from src.data_store import data_store

def now():
    return int(time.time())

def time_eq(a, b):
    return abs(a - b) <= 1

@pytest.fixture(autouse=True)
def clear():
    clear_v1_request()


@pytest.fixture
def user():
    return auth_register_v2_request("u@mail.com", "psword", "first", "last").json()['token']


@pytest.fixture
def user2():
    return auth_register_v2_request("u2@mail.com", "psword", "first", "last").json()['token']


@pytest.fixture
def channel(user):
    return channels_create_v2_request(user, "channel", True).json()['channel_id']

def test_status(user, channel):
	standup_start_v1_request(user, channel, 0)
	assert standup_active_v1_request(user, channel).status_code == 200

def test_no_standup(user, channel):
	assert standup_active_v1_request(user, channel).json() == {'is_active': False, 'time_finish': None}

def test_active_standup(user, channel):
	assert standup_active_v1_request(user, channel).json() == {'is_active': False, 'time_finish': None}
	standup_start_v1_request(user, channel, 1)
	print(data_store.get())
	standup_info = standup_active_v1_request(user, channel).json()
	assert standup_info['is_active'] == True
	assert time_eq(standup_info['time_finish'], now() + 1)
	time.sleep(1.1)

def test_standup_ended(user, channel):
	assert standup_active_v1_request(user, channel).json() == {'is_active': False, 'time_finish': None}
	standup_start_v1_request(user, channel, 1)
	assert standup_active_v1_request(user, channel).json()['is_active'] == True
	time.sleep(0.5)
	assert standup_active_v1_request(user, channel).json()['is_active'] == True
	time.sleep(0.6)
	assert standup_active_v1_request(user, channel).json()['is_active'] == False

def test_invalid_token(user, channel):
	assert standup_active_v1_request("qwerty", channel).status_code == 403
	assert standup_active_v1_request("~" + user[1:], channel).status_code == 403
	auth_logout_v1_request(user)
	assert standup_active_v1_request(user, channel).status_code == 403

def test_invalid_channel(user):
	assert standup_active_v1_request(user, -999).status_code == 400

def test_not_member(user2, channel):
	assert standup_active_v1_request(user2, channel).status_code == 403

def test_concurrent(user, channel):
	channel2 = channels_create_v2_request(user, "channel2", True).json()['channel_id']

	standup_start_v1_request(user, channel, 1)
	standup_start_v1_request(user, channel2, 2)

	assert standup_active_v1_request(user, channel).json()['is_active'] == True
	assert standup_active_v1_request(user, channel2).json()['is_active'] == True

	time.sleep(0.5)

	assert standup_active_v1_request(user, channel).json()['is_active'] == True
	assert standup_active_v1_request(user, channel2).json()['is_active'] == True

	time.sleep(0.75)

	assert standup_active_v1_request(user, channel).json()['is_active'] == False
	assert standup_active_v1_request(user, channel2).json()['is_active'] == True

	time.sleep(1)

	assert standup_active_v1_request(user, channel).json()['is_active'] == False
	assert standup_active_v1_request(user, channel2).json()['is_active'] == False