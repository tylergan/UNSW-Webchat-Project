import pytest # slight change
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

def test_invalid_token():
    assert dm_remove_v1_request("qwerty", 1234).status_code == 403

def test_invalid_dm_id(owner):
    assert dm_remove_v1_request(owner, -1).status_code == 400
    assert dm_remove_v1_request(owner, 9999).status_code == 400


def test_not_member(owner, user1):
    user1_token = auth_login_v2_request(
        'testemail2@gmail.com', 'password').json()['token']
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    assert dm_remove_v1_request(user1_token, dm).status_code == 403


def test_not_authorised(owner, user1):
    user1_token = auth_login_v2_request(
        'testemail2@gmail.com', 'password').json()['token']
    dm = dm_create_v1_request(owner, [user1]).json()['dm_id']
    assert dm_remove_v1_request(user1_token, dm).status_code == 403


def test_1_dm(owner):
    dm = dm_create_v1_request(owner, []).json()['dm_id']
    dm_remove_v1_request(owner, dm)
    assert dm_list_v1_request(owner).json() == {'dms': []}


def test_many_dm(owner, user1, user2):
    user1_token = auth_login_v2_request(
        'testemail2@gmail.com', 'password').json()['token']
    dm = dm_create_v1_request(owner, [user1]).json()['dm_id']
    dm_2 = dm_create_v1_request(owner, [user1, user2]).json()['dm_id']
    dm_3 = dm_create_v1_request(owner, [user2]).json()['dm_id']

    dm_remove_v1_request(owner, dm)
    assert dm_list_v1_request(owner).json() == {'dms': [
        {
            'dm_id': dm_2,
            'name': 'davidsmith, samnguyen, vuluu'
        },
        {
            'dm_id': dm_3,
            'name': 'samnguyen, vuluu'
        }]
    }

    assert dm_list_v1_request(user1_token).json() == {'dms': [
        {
            'dm_id': dm_2,
            'name': 'davidsmith, samnguyen, vuluu'
        }]
    }
