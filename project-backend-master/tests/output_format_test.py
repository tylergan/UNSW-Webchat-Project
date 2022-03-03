import pytest
from src.make_request_test import *


@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("user@mail.com", "password", "first", "last").json()['token']

@pytest.fixture
def user_2():
	return auth_register_v2_request("user2@mail.com", "password", "first", "last").json()['token']

@pytest.fixture
def user_2_id(user_2):
	return  auth_login_v2_request("user2@mail.com", "password").json()['auth_user_id']

@pytest.fixture
def channel(user):
	return channels_create_v2_request(user, "channel", True).json()['channel_id']

@pytest.fixture
def priv_channel(user):
	return channels_create_v2_request(user, "channel", False).json()['channel_id']

def test_auth_register():
	out = auth_register_v2_request("user@mail.com", "password", "first", "last").json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'auth_user_id', 'token'}
	assert isinstance(out['auth_user_id'], int)
	assert isinstance(out['token'], str)


def test_auth_login(user):
	out = auth_login_v2_request("user@mail.com", "password").json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'auth_user_id', 'token'}
	assert isinstance(out['auth_user_id'], int)
	assert isinstance(out['token'], str)


def test_channels_create(user):
	out = channels_create_v2_request(user, "channel", True).json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'channel_id'}
	assert isinstance(out['channel_id'], int)


def test_channels_list_empty(user_2):
	out = channels_list_v2_request(user_2).json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'channels'}
	assert isinstance(out['channels'], list)


def test_channels_list_not_empty(user, channel, priv_channel):
	out = channels_list_v2_request(user).json()
	channel = out['channels'][0]
	assert isinstance(channel, dict)
	assert set(channel.keys()) == {'channel_id', 'name'}
	assert isinstance(channel['channel_id'], int)
	assert isinstance(channel['name'], str)
	assert len(out['channels']) == 2


def test_channels_listall_empty(user_2):
	out = channels_listall_v2_request(user_2).json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'channels'}
	assert isinstance(out['channels'], list)


def test_channels_listall_not_empty(user, channel, priv_channel):
	out = channels_listall_v2_request(user).json()
	channel = out['channels'][0]
	assert isinstance(channel, dict)
	assert set(channel.keys()) == {'channel_id', 'name'}
	assert isinstance(channel['channel_id'], int)
	assert isinstance(channel['name'], str)
	assert len(out['channels']) == 2


def test_channel_details(user, channel):
	out = channel_details_v2_request(user, channel).json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'name', 'is_public', 'owner_members', 'all_members'}
	assert isinstance(out['name'], str)
	assert isinstance(out['is_public'], bool)
	assert isinstance(out['owner_members'], list)
	assert isinstance(out['all_members'], list)
	
	own = out['owner_members'][0]
	assert isinstance(own, dict)
	assert set(own.keys()) == {'u_id', 'email', 'name_first', 'name_last', 'handle_str', 'profile_img_url'}
	assert isinstance(own['u_id'], int)
	assert isinstance(own['email'], str)
	assert isinstance(own['name_first'], str)
	assert isinstance(own['name_last'], str)
	assert isinstance(own['handle_str'], str)
	assert isinstance(own['profile_img_url'], str)

	memb = out['all_members'][0]
	assert isinstance(memb, dict)
	assert set(memb.keys()) == {'u_id', 'email', 'name_first', 'name_last', 'handle_str', 'profile_img_url'}
	assert isinstance(memb['u_id'], int)
	assert isinstance(memb['email'], str)
	assert isinstance(memb['name_first'], str)
	assert isinstance(memb['name_last'], str)
	assert isinstance(memb['handle_str'], str)
	assert isinstance(memb['profile_img_url'], str)


def test_channel_join(user_2, channel):
	out = channel_join_v2_request(user_2, channel).json()
	assert isinstance(out, dict)
	assert len(out.keys()) == 0


def test_channel_invite(user, user_2_id, channel):
	out = channel_invite_v2_request(user, channel, user_2_id).json()
	assert isinstance(out, dict)
	assert len(out.keys()) == 0


def test_channel_messages(user, channel):
	out = channel_messages_v2_request(user, channel, 0).json()
	assert isinstance(out, dict)
	assert set(out.keys()) == {'messages', 'start', 'end'}
	assert isinstance(out['messages'], list)
	assert isinstance(out['start'], int)
	assert isinstance(out['end'], int)

	msgs = out['messages']
	assert len(msgs) == 0


def test_clear():
	out = clear_v1_request().json()
	assert isinstance(out, dict)
	assert len(out.keys()) == 0
