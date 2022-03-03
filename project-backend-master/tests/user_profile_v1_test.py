import pytest
from src.make_request_test import *
from src import config

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("u@mail.com", "password", "first", "last").json()

def test_status_code(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).status_code == 200

def test_profile_self(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user'] == {
		'u_id': user['auth_user_id'],
		'email': 'u@mail.com',
		'name_first': 'first',
		'name_last': 'last',
		'handle_str': 'firstlast',
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
	}

def test_profile_other_user(user):
	user2 = auth_register_v2_request("u2@mail.com", "qwerty", "blake", "morris").json()

	assert user_profile_v1_request(user['token'], user2['auth_user_id']).json()['user'] == {
		'u_id': user2['auth_user_id'],
		'email': 'u2@mail.com',
		'name_first': 'blake',
		'name_last': 'morris',
		'handle_str': 'blakemorris',
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
	}

def test_profile_bad_token(user):
	# Not a token
	assert user_profile_v1_request(user['token'], user['auth_user_id']).status_code == 200
	assert user_profile_v1_request('!@#$%^&', user['auth_user_id']).status_code == 403

	# Tampered token
	assert user_profile_v1_request(user['token'][:-1] + '~', user['auth_user_id']).status_code == 403
	
	# Session ended
	assert user_profile_v1_request(user['token'], user['auth_user_id']).status_code == 200
	auth_logout_v1_request(user['token'])
	assert user_profile_v1_request(user['token'], user['auth_user_id']).status_code == 403

def test_profile_bad_u_id(user):
	assert user_profile_v1_request(user['token'], 999999).status_code == 400

def test_profile_changed(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user'] == {
		'u_id': user['auth_user_id'],
		'email': 'u@mail.com',
		'name_first': 'first',
		'name_last': 'last',
		'handle_str': 'firstlast',
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
	}

	user_profile_setname_v1_request(user['token'], "jake", "borris")
	user_profile_setemail_v1_request(user['token'], "z5555555@unsw.edu.au")
	user_profile_sethandle_v1_request(user['token'], "xxviuserxx")

	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user'] == {
		'u_id': user['auth_user_id'],
		'email': 'z5555555@unsw.edu.au',
		'name_first': 'jake',
		'name_last': 'borris',
		'handle_str': 'xxviuserxx',
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
	}

def test_profile_removed(user):
	# User is global owner
	user2 = auth_register_v2_request("hello@mail.com", "pssword", "first", "last").json()
	assert admin_user_remove_v1_request(user['token'], user2['auth_user_id']).status_code == 200
	assert user_profile_v1_request(user['token'], user2['auth_user_id']).status_code == 200