import pytest

from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def owner_tkn():
	return auth_register_v2_request("owneremail@gmail.com", "pass123", "trish", "vman").json()['token']

@pytest.fixture
def owner_id():
    return auth_login_v2_request('owneremail@gmail.com', 'pass123').json()['auth_user_id']

@pytest.fixture
def c_id(owner_tkn):
	c_id = channels_create_v2_request(owner_tkn, "channelname", True).json()['channel_id']
	return c_id

@pytest.fixture
def user_owner_id(c_id, owner_tkn):
    user_owner_tkn = auth_register_v2_request("useremail@gmail.com", "pass111", "first", "user").json()['token']
    channel_join_v2_request(user_owner_tkn, c_id).json()
    user_owner_id = auth_login_v2_request('useremail@gmail.com', 'pass111').json()['auth_user_id']
    channel_addowner_v1_request(owner_tkn, c_id, user_owner_id).json()
    return user_owner_id

@pytest.fixture
def user_not_owner_tkn():
    return auth_register_v2_request("user2email@gmail.com", "pass444", "second", "user").json()['token']

@pytest.fixture
def user_not_owner_id(c_id, user_not_owner_tkn):
    channel_join_v2_request(user_not_owner_tkn, c_id).json()
    return auth_login_v2_request('user2email@gmail.com', 'pass444').json()['auth_user_id']

@pytest.fixture
def user_not_in_channel():
    auth_register_v2_request('user3email@gmail.com', 'pass333', 'third', 'user')
    return auth_login_v2_request('user3email@gmail.com', 'pass333').json()['auth_user_id']

def check_user_removed_as_owner(owner_tkn, c_id, user_id):
    owners = channel_details_v2_request(owner_tkn, c_id).json()['owner_members']
    assert user_id not in owners

# Tests

# Checks for invalid channel_id
def test_invalid_channel_id(owner_tkn, user_owner_id):
    assert channel_removeowner_v1_request(owner_tkn, 34234, user_owner_id).status_code == 400
    assert channel_removeowner_v1_request(owner_tkn, -244, user_owner_id).status_code == 400

# Check for invalid user id
def test_invalid_uid(owner_tkn, c_id):
	assert channel_removeowner_v1_request(owner_tkn, c_id, 34234).status_code == 400

# Checks for invalid token
def test_invalid_auth_id(c_id, user_owner_id):
    assert channel_removeowner_v1_request(83748, c_id, user_owner_id).status_code == 403

# If user is not a member of the channel, return an error
def test_user_not_in_channel(owner_tkn, c_id, user_not_in_channel):
    assert channel_removeowner_v1_request(owner_tkn, c_id, user_not_in_channel).status_code == 400

# User is not an owner to be removed
def test_not_existing_owner(owner_tkn, c_id, user_not_owner_id):
    assert channel_removeowner_v1_request(owner_tkn, c_id, user_not_owner_id).status_code == 400

# Authorised user does not have owner permissions
def test_no_owner_permissions(user_not_owner_tkn, c_id, user_owner_id):
    assert channel_removeowner_v1_request(user_not_owner_tkn, c_id, user_owner_id).status_code == 403

# Test remove owner
def test_remove_multiple_owners(owner_tkn, c_id, user_owner_id, user_not_owner_id):
    assert channel_removeowner_v1_request(owner_tkn, c_id, user_owner_id).status_code == 200
    channel_addowner_v1_request(owner_tkn, c_id, user_not_owner_id).json()
    assert channel_removeowner_v1_request(owner_tkn, c_id, user_not_owner_id).status_code == 200
    check_user_removed_as_owner(owner_tkn, c_id, user_owner_id)
    check_user_removed_as_owner(owner_tkn, c_id, user_not_owner_id)

# Test user removed is the only owner
def test_one_owner(owner_tkn, owner_id, c_id):
    assert channel_removeowner_v1_request(owner_tkn, c_id, owner_id).status_code == 400








