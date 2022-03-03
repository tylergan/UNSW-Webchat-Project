import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("u@m.com", "psword", "first", "last").json()

def test_status(user):
	assert user_profile_sethandle_v1_request(user['token'], "newhandle").status_code == 200

def test_return(user):
	assert user_profile_sethandle_v1_request(user['token'], "newhandle").json() == {}

def test_handle_changed(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['handle_str'] == "firstlast"
	user_profile_sethandle_v1_request(user['token'], "newhandle").json()
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['handle_str'] == "newhandle"

def test_invalid_length(user):
	assert user_profile_sethandle_v1_request(user['token'], "").status_code == 400
	assert user_profile_sethandle_v1_request(user['token'], "a").status_code == 400
	assert user_profile_sethandle_v1_request(user['token'], "ab").status_code == 400
	assert user_profile_sethandle_v1_request(user['token'], "abc").status_code == 200
	assert user_profile_sethandle_v1_request(user['token'], "abcdefghijklmnopqrst").status_code == 200
	assert user_profile_sethandle_v1_request(user['token'], "abcdefghijklmnopqrstu").status_code == 400

def test_not_alnum(user):
	assert user_profile_sethandle_v1_request(user['token'], "abcde").status_code == 200
	assert user_profile_sethandle_v1_request(user['token'], "12345").status_code == 200
	assert user_profile_sethandle_v1_request(user['token'], "1bc123").status_code == 200
	assert user_profile_sethandle_v1_request(user['token'], "ab de").status_code == 400
	assert user_profile_sethandle_v1_request(user['token'], "ab_de").status_code == 400
	assert user_profile_sethandle_v1_request(user['token'], "abc%^&*").status_code == 400

def test_handle_in_use(user):
	u2 = auth_register_v2_request("u2@m.com", "psword", "blake", "morris").json()['token']
	assert user_profile_sethandle_v1_request(user['token'], "blakemorris").status_code == 400
	user_profile_sethandle_v1_request(u2, "notblakemorris")
	assert user_profile_sethandle_v1_request(user['token'], "blakemorris").status_code == 200
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['handle_str'] == "blakemorris"

def test_invalid_token(user):
	assert user_profile_sethandle_v1_request('sdfjgkl', 'newhandle').status_code == 403

	assert user_profile_sethandle_v1_request(user['token'][:-1] + '~', 'newhandle').status_code == 403

	auth_logout_v1_request(user['token'])
	assert user_profile_sethandle_v1_request(user['token'], 'newhandle').status_code == 403
