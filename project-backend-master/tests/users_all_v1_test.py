from enum import auto
import pytest
from src import config
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("e@mail.com", "psword", "first", "last").json()['token']

@pytest.fixture
def users():
	auth_register_v2_request("u1@mail.com", "psword", "vu", "luu")
	auth_register_v2_request("u2@mail.com", "psword", "redmond", "mobbs")
	auth_register_v2_request("u3@mail.com", "psword", "trissha", "varman")
	auth_register_v2_request("u4@mail.com", "psword", "blake", "morris")
	auth_register_v2_request("u5@mail.com", "psword", "tyler", "gan")

def test_return(user):
	assert users_all_v1_request(user).status_code == 200

def test_one_user(user):
	u_id = auth_login_v2_request('e@mail.com', 'psword').json()['auth_user_id']
	assert users_all_v1_request(user).json()['users'][0] == {
		'u_id': u_id,
		'email': 'e@mail.com',
		'name_first': 'first',
		'name_last': 'last',
		'handle_str': 'firstlast',
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
	}

def test_multiple_users(user, users):
	resp = users_all_v1_request(user).json()
	assert len(resp['users']) == 6

def test_invalid_token(user):
	assert users_all_v1_request('asdgfhjk').status_code == 403
	assert users_all_v1_request('~' + user[1:]).status_code == 403