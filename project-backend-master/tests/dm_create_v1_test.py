import pytest
from src.make_request_test import *
from src import config

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def owner():
	return auth_register_v2_request("u@mail.com", "password", "blake", "morris").json()['token']

@pytest.fixture
def user1():
	return auth_register_v2_request("u2@mail.com", "password", "redmond", "mobbs").json()['auth_user_id']

@pytest.fixture
def user2():
	return auth_register_v2_request("u3@mail.com", "password", "tyler", "gan").json()['auth_user_id']
	

def test_status(owner, user1):
	assert dm_create_v1_request(owner, [user1]).status_code == 200

def test_return(owner, user1):
	resp = dm_create_v1_request(owner, [user1]).json()
	assert set(resp.keys()) == {'dm_id'}
	assert isinstance(resp['dm_id'], int)

def test_invalid_token(owner, user1):
	# Not a token
	assert dm_create_v1_request(owner, [user1]).status_code == 200
	assert dm_create_v1_request('abc', [user1]).status_code == 403

	# Tampered token
	assert dm_create_v1_request('~' + owner[1:], [user1]).status_code == 403
	
	# Session ended
	assert dm_create_v1_request(owner, [user1]).status_code == 200
	auth_logout_v1_request(owner)
	assert dm_create_v1_request(owner, [user1]).status_code == 403

def test_one_invalid_u_id(owner):
	assert dm_create_v1_request(owner, [99999]).status_code == 400

def test_all_invalid_u_id(owner):
	assert dm_create_v1_request(owner, [99999, 99998, 99997]).status_code == 400

def test_any_invalid_u_id(owner, user1, user2):
	assert dm_create_v1_request(owner, [user1, user2, 99999]).status_code == 400

def test_create_no_u_ids(owner):
	u_id = auth_login_v2_request('u@mail.com', 'password').json()['auth_user_id']
	dm = dm_create_v1_request(owner, []).json()['dm_id']
	assert dm_details_v1_request(owner, dm).json() == {
		'name': 'blakemorris',
		'members': [
			{
				'u_id': u_id,
				'email': 'u@mail.com',
				'name_first': 'blake',
				'name_last': 'morris',
				'handle_str': 'blakemorris',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			}
		]
	}

def test_create_one_u_id(owner, user1):
	u_id = auth_login_v2_request('u@mail.com', 'password').json()['auth_user_id']
	dm = dm_create_v1_request(owner, [user1]).json()['dm_id']
	assert dm_details_v1_request(owner, dm).json() == {
		'name': 'blakemorris, redmondmobbs',
		'members': [
			{
				'u_id': u_id,
				'email': 'u@mail.com',
				'name_first': 'blake',
				'name_last': 'morris',
				'handle_str': 'blakemorris',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
			{
				'u_id': user1,
				'email': 'u2@mail.com',
				'name_first': 'redmond',
				'name_last': 'mobbs',
				'handle_str': 'redmondmobbs',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
		]
	}

def test_create_multiple_u_ids(owner, user1, user2):
	u_id = auth_login_v2_request('u@mail.com', 'password').json()['auth_user_id']
	dm = dm_create_v1_request(owner, [user1, user2]).json()['dm_id']
	assert dm_details_v1_request(owner, dm).json() == {
		'name': 'blakemorris, redmondmobbs, tylergan',
		'members': [
			{
				'u_id': u_id,
				'email': 'u@mail.com',
				'name_first': 'blake',
				'name_last': 'morris',
				'handle_str': 'blakemorris',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
			{
				'u_id': user1,
				'email': 'u2@mail.com',
				'name_first': 'redmond',
				'name_last': 'mobbs',
				'handle_str': 'redmondmobbs',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
			{
				'u_id': user2,
				'email': 'u3@mail.com',
				'name_first': 'tyler',
				'name_last': 'gan',
				'handle_str': 'tylergan',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
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