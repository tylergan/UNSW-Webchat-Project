import pytest

from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def owner_tkn():
	return auth_register_v2_request("owneremail@gmail.com", "pass123", "trish", "vman").json()['token']

@pytest.fixture
def c_id(owner_tkn):
	c_id = channels_create_v2_request(owner_tkn, "channelname", True).json()['channel_id']
	return c_id

@pytest.fixture
def user_tkn():
    auth_register_v2_request("user2email@gmail.com", "pass111", "first", "user")
    return auth_register_v2_request("useremail@gmail.com", "pass111", "first", "user").json()['token']

@pytest.fixture
def user_id(user_tkn, c_id):
    channel_join_v2_request(user_tkn, c_id).json()
    return auth_login_v2_request('useremail@gmail.com', 'pass111').json()['auth_user_id']

@pytest.fixture
def user_id2(c_id):
    user_tkn2 = auth_register_v2_request('user2@gmail.com', 'pass444', 'second', 'user').json()['token']
    channel_join_v2_request(user_tkn2, c_id).json()
    return auth_login_v2_request('user2@gmail.com', 'pass444').json()['auth_user_id']

@pytest.fixture
def user_not_in_channel():
    auth_register_v2_request('user3@gmail.com', 'pass333', 'third', 'user')
    return auth_login_v2_request('user3@gmail.com', 'pass333').json()['auth_user_id']

def check_user_added_as_owner(owner_tkn, c_id, user_id):
    owners = channel_details_v2_request(owner_tkn, c_id).json()['owner_members']
    assert any(user['u_id'] == user_id for user in owners)

# Tests

def test_invalid_channel_id(owner_tkn, user_id):
    assert channel_addowner_v1_request(owner_tkn, 67873, user_id).status_code == 400
    assert channel_addowner_v1_request(owner_tkn, -2736, user_id).status_code == 400

def test_invalid_uid(owner_tkn, c_id):
	assert channel_addowner_v1_request(owner_tkn, c_id, 2763872).status_code == 400

def test_invalid_auth_id(c_id, user_id):
    assert channel_addowner_v1_request(123678, c_id, user_id).status_code == 403

def test_user_not_in_channel(owner_tkn, c_id, user_not_in_channel):
    assert channel_addowner_v1_request(owner_tkn, c_id, user_not_in_channel).status_code == 400

def test_already_owner(owner_tkn, c_id, user_id):
    assert channel_addowner_v1_request(owner_tkn, c_id, user_id).status_code == 200
    assert channel_addowner_v1_request(owner_tkn, c_id, user_id).status_code == 400

def test_no_owner_permissions(user_tkn, c_id, user_id, user_id2):
    assert channel_addowner_v1_request(user_tkn, c_id, user_id).status_code == 403
    assert channel_addowner_v1_request(user_tkn, c_id, user_id2).status_code == 403

def test_not_a_member(c_id, user_id):
    user = auth_register_v2_request("e@mail.com", "psword", "first", "last").json()['token']
    assert channel_addowner_v1_request(user, c_id, user_id).status_code == 403


def test_add_multiple_owners(owner_tkn, c_id, user_id, user_id2):
    assert channel_addowner_v1_request(owner_tkn, c_id, user_id).status_code == 200
    assert channel_addowner_v1_request(owner_tkn, c_id, user_id2).status_code == 200
    check_user_added_as_owner(owner_tkn, c_id, user_id)
    check_user_added_as_owner(owner_tkn, c_id, user_id2)








