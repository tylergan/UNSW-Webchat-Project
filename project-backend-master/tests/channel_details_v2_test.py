import pytest
from src import config
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

def test_invalid_channel_id():
    '''
    Test for invalid channel id
    '''
    token = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']
    assert channel_details_v2_request(token, 3).status_code == 400


def test_invalid_user_id():
    '''
    Test for valid channel id but invalid user id
    '''
    token = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']
    channel_id = channels_create_v2_request(token, "test channel", True).json()['channel_id']
    assert channel_details_v2_request(-1, channel_id).status_code == 403

def test_user_not_authorised():
    '''
    Test when channel_id is valid and the authorised user is not a member of the channel
    '''
    token = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']
    token2 = auth_register_v2_request("secondtestemail@gmail.com", "password", "david", "smith").json()['token']
    channel_id = channels_create_v2_request(token, "test channel", True).json()['channel_id']
    assert channel_details_v2_request(token2, channel_id).status_code == 403

def test_valid_channel_id():
    '''
    Test for valid channel id and user id
    '''
    reg = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()
    u_id = reg['auth_user_id']
    token = reg['token']
    channel_id = channels_create_v2_request(token, "test channel", True).json()['channel_id']
    channel_detail = {}
    channel_detail = channel_details_v2_request(token, channel_id).json()
    assert channel_detail == {
        'name': 'test channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'name_first': 'vu',
                'name_last': 'luu',
                'email': 'testemail@gmail.com',
                'handle_str': 'vuluu',
                'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
            },
        ],
        'all_members': [
            {
                'u_id': u_id ,
                'name_first': 'vu',
                'name_last': 'luu',
                'email': 'testemail@gmail.com',
                'handle_str': 'vuluu',
                'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
            },
        ],
    }

def test_private_channel():
    '''
    Test for valid channel id and user id
    '''
    reg = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()
    u_id = reg['auth_user_id']
    token = reg['token']
    channel_id = channels_create_v2_request(token, "test channel", False).json()['channel_id']
    channel_detail = {}
    channel_detail = channel_details_v2_request(token, channel_id).json()
    assert channel_detail == {
        'name': 'test channel',
        'is_public': False,
        'owner_members': [
            {
                'u_id': u_id,
                'name_first': 'vu',
                'name_last': 'luu',
                'email': 'testemail@gmail.com',
                'handle_str': 'vuluu',
                'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
            },
        ],
        'all_members': [
            {
                'u_id': u_id ,
                'name_first': 'vu',
                'name_last': 'luu',
                'email': 'testemail@gmail.com',
                'handle_str': 'vuluu',
                'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg'
            },
        ],
    }


def test_multiple_users():

    #Test when channel have multiple user and is public

    token = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']
    token2 = auth_register_v2_request("secondtestemail@gmail.com", "password", "david", "smith").json()['token']
    token3 = auth_register_v2_request("thirdtestemail@gmail.com", "password", "sam", "nguyen").json()['token']

    channel_id = channels_create_v2_request(token, "test channel", True).json()['channel_id']
    channel_join_v2_request(token2, channel_id)
    channel_join_v2_request(token3, channel_id)
    channel_detail = {}

    channel_detail = channel_details_v2_request(token, channel_id).json()

    assert set(channel_detail.keys()) == {'name', 'is_public', 'owner_members', 'all_members'}
    assert channel_detail['name'] == 'test channel'
    assert channel_detail['is_public'] == True
    assert len(channel_detail['owner_members']) == 1
    assert len(channel_detail['all_members']) == 3


def test_multiple_users_priv():
    token = auth_register_v2_request("testemail@gmail.com", "password", "vu", "luu").json()['token']
    
    auth_register_v2_request("secondtestemail@gmail.com", "password", "david", "smith").json()['token']
    uid2 = auth_login_v2_request("secondtestemail@gmail.com", "password").json()['auth_user_id']
    
    auth_register_v2_request("thirdtestemail@gmail.com", "password", "sam", "nguyen").json()['token']
    uid3 = auth_login_v2_request("thirdtestemail@gmail.com", "password").json()['auth_user_id']

    channel_id = channels_create_v2_request(token, "test channel", False).json()['channel_id']

    channel_invite_v2_request(token, channel_id, uid2)
    channel_invite_v2_request(token, channel_id, uid3)
    channel_detail = {}

    channel_detail = channel_details_v2_request(token, channel_id).json()
    
    assert set(channel_detail.keys()) == {'name', 'is_public', 'owner_members', 'all_members'}
    assert channel_detail['name'] == 'test channel'
    assert channel_detail['is_public'] == False
    assert len(channel_detail['owner_members']) == 1
    assert len(channel_detail['all_members']) == 3
