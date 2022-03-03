import pytest
from src.other import clear_v1

from src.make_request_test import *

# Reset application data before each test is run
@pytest.fixture(autouse=True)
def clear_data():
    clear_v1_request()

@pytest.fixture
def owner():
    return auth_register_v2_request("name1@email.com", "password", "firstname", "lastname").json()

@pytest.fixture
def member():
    # Ensure user isn't global owner
    auth_register_v2_request("name2@email.com", "password", "firstname", "lastname")

    return auth_register_v2_request("name3@email.com", "password", "firstname", "lastname").json()

@pytest.fixture
def channel():
    member = auth_register_v2_request("namech@email.com", "password", "firstname", "lastname").json()['token']
    return channels_create_v2_request(member, "channel", False).json()['channel_id']

def test_invalid_token(owner):
    assert admin_userpermission_change_v1_request('goodeveningmgentlemen', owner['auth_user_id'], 1).status_code == 403

def test_invalid_u_id(owner):
    assert admin_userpermission_change_v1_request(owner['token'], 1, 1).status_code == 400
    assert admin_userpermission_change_v1_request(owner['token'], 1, 2).status_code == 400

def test_invalid_permission_id(owner, member):
    assert admin_userpermission_change_v1_request(owner['token'], member['auth_user_id'], 0).status_code == 400
    assert admin_userpermission_change_v1_request(owner['token'], member['auth_user_id'], 3).status_code == 400

def test_solo_owner_demotion(owner, member):
    assert admin_userpermission_change_v1_request(owner['token'], owner['auth_user_id'], 2).status_code == 400

def test_non_owner_useage(owner, member):
    assert admin_userpermission_change_v1_request(member['token'], owner['auth_user_id'], 2).status_code == 403
    assert admin_userpermission_change_v1_request(member['token'], owner['auth_user_id'], 1).status_code == 403
    assert admin_userpermission_change_v1_request(member['token'], member['auth_user_id'], 2).status_code == 403
    assert admin_userpermission_change_v1_request(member['token'], member['auth_user_id'], 2).status_code == 403

def test_successful_solo_owner_to_owner(owner, member):
    assert admin_userpermission_change_v1_request(owner['token'], owner['auth_user_id'], 1).status_code == 200

def test_successful_member_to_member(owner, member, channel):
    assert admin_userpermission_change_v1_request(owner['token'], member['auth_user_id'], 2).status_code == 200

    # Ensure user is still a member by making them try join a private channel
    assert channel_join_v2_request(member['token'], channel).status_code == 403

def test_successful_member_to_owner(owner, member, channel):
    assert admin_userpermission_change_v1_request(owner['token'], member['auth_user_id'], 1).status_code == 200

    # Ensure user is now an owner by making them try join a private channel
    assert channel_join_v2_request(member['token'], channel).status_code == 200

def test_successful_ownership_swap(owner, member, channel):
    assert admin_userpermission_change_v1_request(owner['token'], member['auth_user_id'], 1).status_code == 200
    assert admin_userpermission_change_v1_request(member['token'], owner['auth_user_id'], 2).status_code == 200

    # Ensure old owner is now a member by making them try join a private channel
    assert channel_join_v2_request(owner['token'], channel).status_code == 403