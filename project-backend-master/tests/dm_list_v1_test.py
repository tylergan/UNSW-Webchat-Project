import pytest
from src.make_request_test import *
from tests.dm_messages_v1_test import dm

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

def test_invalid_token():
    assert dm_list_v1_request("qwerty").status_code == 403

def test_dm_list_empty(owner):
    assert dm_list_v1_request(owner).json() == {'dms': []}

def test_one_dm_list(owner):
    dm = dm_create_v1_request(owner, []).json()['dm_id']

    assert dm_list_v1_request(owner).json() == {'dms':[
        {
        'dm_id': dm,
        'name': 'vuluu'
        }]
    }

def test_all_dm_list(owner, user1, user2):
    dm_1 = dm_create_v1_request(owner, [user1]).json()['dm_id']
    dm_2 = dm_create_v1_request(owner, [user1, user2]).json()['dm_id']

    assert dm_list_v1_request(owner).json() == {'dms': [
        {
        'dm_id': dm_1,
        'name': 'davidsmith, vuluu'
        },
        {
        'dm_id': dm_2,
        'name': 'davidsmith, samnguyen, vuluu'
        }]
    }

def test_some_dm_list(owner, user1, user2):
    # owner is in dm_1 and dm_2
    # user 1 is in dm_2 and dm_3 but not in dm_1
    # user 2 is in all dms
    user1_token = auth_login_v2_request('testemail2@gmail.com', 'password').json()['token']
    user2_token = auth_login_v2_request('testemail3@gmail.com', 'password').json()['token']
    dm_1 = dm_create_v1_request(owner, [user2]).json()['dm_id']
    dm_2 = dm_create_v1_request(owner, [user1, user2]).json()['dm_id']
    dm_3 = dm_create_v1_request(user1_token, [user2]).json()['dm_id']

    assert dm_list_v1_request(user1_token).json() == {'dms': [
        {
        'dm_id': dm_2,
        'name': 'davidsmith, samnguyen, vuluu'
        },
        {
        'dm_id': dm_3,
        'name': 'davidsmith, samnguyen'
        }]
    }

    assert dm_list_v1_request(owner).json() == {'dms': [
        {
        'dm_id': dm_1,
        'name': 'samnguyen, vuluu'
        },
        {
        'dm_id': dm_2,
        'name': 'davidsmith, samnguyen, vuluu'
        }]
    }

    assert dm_list_v1_request(user2_token).json() == {'dms': [
        {
        'dm_id': dm_1,
        'name': 'samnguyen, vuluu'
        },
        {
        'dm_id': dm_2,
        'name': 'davidsmith, samnguyen, vuluu'
        },
        {
        'dm_id': dm_3,
        'name': 'davidsmith, samnguyen'
        }]
    }


