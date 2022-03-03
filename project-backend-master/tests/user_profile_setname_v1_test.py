import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("u@m.com", "psword", "first", "last").json()

def test_status(user):
	assert user_profile_setname_v1_request(user['token'], "blake", "morris").status_code == 200

def test_return(user):
	assert user_profile_setname_v1_request(user['token'], "blake", "morris").json() == {}

def test_name_changed(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_first'] == "first"
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_last'] == "last"

	user_profile_setname_v1_request(user['token'], "blake", "last")

	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_first'] == "blake"
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_last'] == "last"

	user_profile_setname_v1_request(user['token'], "blake", "morris")

	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_first'] == "blake"
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['name_last'] == "morris"

def test_invalid_length_first(user):
	assert user_profile_setname_v1_request(user['token'], "", "last").status_code == 400
	assert user_profile_setname_v1_request(user['token'], "a", "last").status_code == 200
	assert user_profile_setname_v1_request(user['token'], "a" * 50, "last").status_code == 200
	assert user_profile_setname_v1_request(user['token'], "a" * 51, "last").status_code == 400

def test_invalid_length_last(user):
	assert user_profile_setname_v1_request(user['token'], "first", "").status_code == 400
	assert user_profile_setname_v1_request(user['token'], "first", "a").status_code == 200
	assert user_profile_setname_v1_request(user['token'], "first", "a" * 50).status_code == 200
	assert user_profile_setname_v1_request(user['token'], "first", "a" * 51).status_code == 400

def test_invalid_token(user):
	assert user_profile_setname_v1_request('sdfjgkl', "blake", "morris").status_code == 403

	assert user_profile_setname_v1_request(user['token'][:-1] + '~', "blake", "morris").status_code == 403

	auth_logout_v1_request(user['token'])
	assert user_profile_setname_v1_request(user['token'], "blake", "morris").status_code == 403
