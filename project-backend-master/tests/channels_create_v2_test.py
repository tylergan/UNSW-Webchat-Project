import pytest
from src.make_request_test import *

# Clears existing data for all tests
@pytest.fixture(autouse=True)
def clear():
      clear_v1_request()

@pytest.fixture
def user():
      resp = auth_register_v2_request("player1@mail.com", "password", "firstname", "lastname")
      user = resp.json()['token']
      return user

def check_added(token, channel, user_id):
    members = channel_details_v2_request(token, channel).json()['all_members']
    assert any(user['u_id'] == user_id for user in members)

# Tests for valid input for channels_create_v2_request 

def test_channel_name_too_long(user):
      assert channels_create_v2_request(user, "anextremelylongchannelname", True).status_code == 400
            
def test_channel_name_too_short(user):
      assert channels_create_v2_request(user, "", True).status_code == 400

def test_invalid_auth_id():
      assert channels_create_v2_request(20, "channelname", True).status_code == 403

def test_invalid_too_long():
      assert channels_create_v2_request(23467895, "anextremelylongchannelname", True).status_code == 403

def test_invalid_too_short():
      assert channels_create_v2_request(23467895, "", True).status_code == 403

# Test for correct output

def test_channel_id_uniqueness(user):
      used_channel_ids = set()
      
      channel_id1 = channels_create_v2_request(user, "firstchannel", True).json()['channel_id']
      used_channel_ids.add(channel_id1)

      channel_id2 = channels_create_v2_request(user, "firstchannel", True).json()['channel_id']
      assert channel_id2 not in used_channel_ids
      used_channel_ids.add(channel_id2)

      channel_id3 = channels_create_v2_request(user, "firstchannel", True).json()['channel_id']
      assert channel_id3 not in used_channel_ids


def test_success_200(user):
      assert channels_create_v2_request(user, "firstchannel", True).status_code == 200

def test_valid_integer_output(user):
      channel_id6 = channels_create_v2_request(user, "firstchannel", True).json()['channel_id']
      assert isinstance(channel_id6, int)

def test_owner_in_channel_public(user):
      c_id = channels_create_v2_request(user, "newchannel", True).json()['channel_id']
      user_id = auth_login_v2_request("player1@mail.com", "password").json()['auth_user_id']
      check_added(user, c_id, user_id)

def test_owner_in_channel_private(user):
      c_id = channels_create_v2_request(user, "newchannel", False).json()['channel_id']
      user_id = auth_login_v2_request("player1@mail.com", "password").json()['auth_user_id']
      check_added(user, c_id, user_id)

def test_owner(user):
      c_id = channels_create_v2_request(user, "newchannel", True).json()['channel_id']

      details = channel_details_v2_request(user, c_id).json()
      owners = details['owner_members']

      # Get the channel creator's ID
      user_id = auth_login_v2_request("player1@mail.com", "password").json()['auth_user_id']

      # Ensure the creator is an owner
      assert any(owner['u_id'] == user_id for owner in owners)

def test_owner_with_other_members():
      token1 = auth_register_v2_request("user1@mail.com", "password", "first", "last").json()['token']
      uid1 = auth_login_v2_request("user1@mail.com", "password").json()['auth_user_id']
      c_id = channels_create_v2_request(token1, "newchannel", True).json()['channel_id']
      
      token2 = auth_register_v2_request("user2@mail.com", "password", "blake", "morris").json()['token']
      uid2 = auth_login_v2_request("user2@mail.com", "password").json()['auth_user_id']
      channel_join_v2_request(token2, c_id)
      
      token3 = auth_register_v2_request("user3@mail.com", "password", "redmond", "mobbs").json()['token']
      uid3 = auth_login_v2_request("user3@mail.com", "password").json()['auth_user_id']
      channel_join_v2_request(token3, c_id)

      details = channel_details_v2_request(token1, c_id).json()
      owners = details['owner_members']

      # Check that all 3 users are channel members
      check_added(token1, c_id, uid1)
      check_added(token1, c_id, uid2)
      check_added(token1, c_id, uid3)

      # Check that correct member is owner
      assert any(owner['u_id'] == uid1 for owner in owners)
      assert not any(owner['u_id'] == uid2 for owner in owners)
      assert not any(owner['u_id'] == uid3 for owner in owners)

def test_owner_with_other_members_private():
      token1 = auth_register_v2_request("user1@mail.com", "password", "first", "last").json()['token']
      uid1 = auth_login_v2_request("user1@mail.com", "password").json()['auth_user_id']
      c_id = channels_create_v2_request(token1, "newchannel", False).json()['channel_id']
      
      auth_register_v2_request("user2@mail.com", "password", "blake", "morris").json()['token']
      uid2 = auth_login_v2_request("user2@mail.com", "password").json()['auth_user_id']
      channel_invite_v2_request(token1, c_id, uid2)
      
      auth_register_v2_request("user3@mail.com", "password", "redmond", "mobbs").json()['token']
      uid3 = auth_login_v2_request("user3@mail.com", "password").json()['auth_user_id']
      channel_invite_v2_request(token1, c_id, uid3)

      details = channel_details_v2_request(token1, c_id).json()
      owners = details['owner_members']

      # Check that all 3 users are channel members
      check_added(token1, c_id, uid1)
      check_added(token1, c_id, uid2)
      check_added(token1, c_id, uid3)

      # Check that correct member is owner
      assert any(owner['u_id'] == uid1 for owner in owners)
      assert not any(owner['u_id'] == uid2 for owner in owners)
      assert not any(owner['u_id'] == uid3 for owner in owners)