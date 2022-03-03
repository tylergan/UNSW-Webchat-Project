import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user1():
	return auth_register_v2_request("u1@mail.com", "password", "first", "last").json()['token']

@pytest.fixture
def user2():
	return auth_register_v2_request("u2@mail.com", "password", "first", "last").json()['token']

@pytest.fixture
def channel1(user1):
	ch = channels_create_v2_request(user1, "channel1", True).json()['channel_id']
	message_send_v1_request(user1, ch, "hello world")
	message_send_v1_request(user1, ch, "abcdefg")
	message_send_v1_request(user1, ch, "defghij")
	return ch

@pytest.fixture
def channel2(user2):
	ch = channels_create_v2_request(user2, "channel1", True).json()['channel_id']
	message_send_v1_request(user2, ch, "goodbye world")
	message_send_v1_request(user2, ch, "abcdefg")
	message_send_v1_request(user2, ch, "defghij")
	return ch

@pytest.fixture
def dm(user1, user2):
	u2id = auth_login_v2_request("u2@mail.com", "password").json()['auth_user_id']
	dm = dm_create_v1_request(user1, [u2id]).json()['dm_id']
	message_senddm_v1_request(user1, dm, "the world is flat")
	message_senddm_v1_request(user2, dm, "you're an idiot")




def test_status(user1, channel1):
	assert search_v1_request(user1, "hello").status_code == 200

def test_one_result(user1, channel1):
	messages = search_v1_request(user1, "hello").json()['messages']
	assert {m['message'] for m in messages} == {"hello world"}

def test_multiple_results(user1, channel1):
	messages = search_v1_request(user1, "defg").json()['messages']
	assert {m['message'] for m in messages} == {"abcdefg", "defghij"}

def test_other_channels(user1, channel1, channel2):
	messages = search_v1_request(user1, "world").json()['messages']
	assert {m['message'] for m in messages} == {"hello world"}

def test_dm(user1, dm):
	messages = search_v1_request(user1, "world").json()['messages']
	assert {m['message'] for m in messages} == {"the world is flat"}

def test_dm_and_channel(user1, dm, channel1):
	messages = search_v1_request(user1, "world").json()['messages']
	assert {m['message'] for m in messages} == {"the world is flat", "hello world"}

def test_empty_search(user1):
	assert search_v1_request(user1, "").status_code == 400
	assert search_v1_request(user1, "a").status_code == 200

def test_long_search(user1):
	assert search_v1_request(user1, "a" * 1000).status_code == 200
	assert search_v1_request(user1, "a" * 1001).status_code == 400

def test_invalid_token():
	assert search_v1_request("asdgfhjk", "hello").status_code == 403