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
	return auth_register_v2_request("testemail2@gmail.com", "password", "david", "smith").json()['auth_user_id']

@pytest.fixture
def user2():
	return auth_register_v2_request("testemail3@gmail.com", "password", "sam", "nguyen").json()['auth_user_id']

def test_invalid_token(owner, user1):
    dm = dm_create_v1_request(owner, [user1]).json()['dm_id']
    assert dm_leave_v1_request("qwerty", dm).status_code == 403

def test_invalid_dm_id(owner):
    assert dm_details_v1_request(owner, -1).status_code == 400
    assert dm_details_v1_request(owner, 9999).status_code == 400

def test_not_member(owner, user1):
    user1_token = auth_login_v2_request('testemail2@gmail.com', 'password').json()['token']
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    assert dm_leave_v1_request(user1_token, dm).status_code == 403

def test_valid(owner, user1):
    dm = dm_create_v1_request(owner, [user1]).json()['dm_id']
    user1_token = auth_login_v2_request('testemail2@gmail.com', 'password').json()['token']
    dm_leave_v1_request(user1_token, dm)
    dm_details_v1_request(owner, dm) 
    assert dm_list_v1_request(user1_token).json() == {'dms': []}


def test_owner_leave_dm_empty(owner):
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    dm_leave_v1_request(owner, dm)
    assert dm_list_v1_request(owner).json() == {'dms': []}
    

def test_owner_leave_dm_with_users(owner, user1, user2):
    user1_token = auth_login_v2_request('testemail2@gmail.com', 'password').json()['token']
    dm = dm_create_v1_request(owner, [user1, user2]).json()['dm_id']
    dm_leave_v1_request(owner, dm)
    assert dm_details_v1_request(user1_token, dm).json() == {
		'name': 'davidsmith, samnguyen, vuluu',
		'members': [
			{
				'u_id': user1,
				'email': 'testemail2@gmail.com',
				'name_first': 'david',
				'name_last': 'smith',
				'handle_str': 'davidsmith',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			},
            {
				'u_id': user2,
				'email': 'testemail3@gmail.com',
				'name_first': 'sam',
				'name_last': 'nguyen',
				'handle_str': 'samnguyen',
				'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
			}
		]
	}


def test_multiple_dm(owner, user1, user2):
    user1_token = auth_login_v2_request('testemail2@gmail.com', 'password').json()['token']
    dm_1 = dm_create_v1_request(owner, [user1]).json()['dm_id']
    dm_2 = dm_create_v1_request(owner, [user1]).json()['dm_id']
    dm_3 = dm_create_v1_request(user1_token, [user2]).json()['dm_id']

    dm_leave_v1_request(user1_token, dm_1)
    assert dm_list_v1_request(user1_token).json() == {'dms': [
        {
        'dm_id': dm_2,
        'name': 'davidsmith, vuluu'
        },
        {
        'dm_id': dm_3,
        'name': 'davidsmith, samnguyen'
        }
        ]   
    }