import pytest
from src import config
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def owner():
	return auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']

@pytest.fixture
def user1():
	return auth_register_v2_request("testemail2@gmail.com", "password", "david", "smith").json()['token']


def test_invalid_dm_id(owner):
    assert dm_details_v1_request(owner, -1).status_code == 400
    assert dm_details_v1_request(owner, 9999).status_code == 400

def test_invalid_token(owner):
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    assert dm_details_v1_request('aaaaa', dm).status_code == 403 

def test_not_member(owner, user1):
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    assert dm_details_v1_request(user1, dm).status_code == 403 

def test_owner(owner):
    u_id = auth_login_v2_request('testemail@gmail.com', 'password').json()['auth_user_id']
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    assert dm_details_v1_request(owner, dm).json() == {
		'name': 'vuluu',
		'members': [
			{
				'u_id': u_id,
				'email': 'testemail@gmail.com',
				'name_first': 'vu',
				'name_last': 'luu',
				'handle_str': 'vuluu',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			}
		]
	}

def test_multiple_members(owner, user1):
    owner_id = auth_login_v2_request('testemail@gmail.com', 'password').json()['auth_user_id']
    user1_id = auth_login_v2_request('testemail2@gmail.com', 'password').json()['auth_user_id']
    dm = dm_create_v1_request(owner, [user1_id]).json()['dm_id']
    assert dm_details_v1_request(owner, dm).json() == {
		'name': 'davidsmith, vuluu',
		'members': [
			{
				'u_id': owner_id,
				'email': 'testemail@gmail.com',
				'name_first': 'vu',
				'name_last': 'luu',
				'handle_str': 'vuluu',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
            {
				'u_id': user1_id,
				'email': 'testemail2@gmail.com',
				'name_first': 'david',
				'name_last': 'smith',
				'handle_str': 'davidsmith',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			}
		]
	}

def test_name_sort():																	 # Handle:
	owner = auth_register_v2_request('u@m.com', 'psword', 'zzz', 'zzz').json()['token']		 # zzzzzz (6th)
	u1 = auth_register_v2_request('u1@m.com', 'psword', 'xxx', 'xxx').json()['auth_user_id'] # xxxxxx (5th)
	u2 = auth_register_v2_request('u2@m.com', 'psword', 'xxx', 'aaa').json()['auth_user_id'] # xxxaaa (3rd)
	u3 = auth_register_v2_request('u3@m.com', 'psword', 'xxx', 'aaa').json()['auth_user_id'] # xxxaaa0 (4th)
	u4 = auth_register_v2_request('u4@m.com', 'psword', 'MMM', 'MMM').json()['auth_user_id'] # mmmmmm (2nd)
	u5 = auth_register_v2_request('u5@m.com', 'psword', 'aaa', 'aaa').json()['auth_user_id'] # aaaaaa (1st)

	dm = dm_create_v1_request(owner, [u1, u2, u3, u4, u5]).json()['dm_id']

	assert dm_details_v1_request(owner, dm).json()['name'] == 'aaaaaa, mmmmmm, xxxaaa, xxxaaa0, xxxxxx, zzzzzz'

