import pytest


from src.make_request_test import *

# Clears existing data for all tests
@pytest.fixture(autouse=True)
def clear():
    clear_v1_request()

# Tests for valid output for channels_list_v2_request_test.py

def test_channels_list_basic():
    user_1 = auth_register_v2_request("user1@gmail.com", "password1", "firstname", "lastname").json()['token']
    channels_create_v2_request(user_1, "channel", True)

    assert channels_list_v2_request(user_1).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'channel',
            }
        ]
    }


def test_channels_list_multiple():
    user_1 = auth_register_v2_request("user1@gmail.com", "password1", "firstname", "lastname").json()['token']
    user_2 = auth_register_v2_request("user2@gmail.com", "password2", "firstname", "lastname").json()['token']

    channels_create_v2_request(user_1, "channel", True)
    channels_create_v2_request(user_1, "channel2", True)
    channels_create_v2_request(user_2, "channel3", True)
    channels_create_v2_request(user_2, "channel4", True)

    assert channels_list_v2_request(user_1).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'channel',
            },
            {
                'channel_id': 1,
                'name': 'channel2',
            }
        ]
    }

    assert channels_list_v2_request(user_2).json() == {
        'channels': [
            {
                'channel_id': 2,
                'name': 'channel3',
            },
            {
                'channel_id': 3,
                'name': 'channel4',
            }
        ]
    }

def test_channels_list_private():
    user_1 = auth_register_v2_request("user1@mail.com", "password", "first", "last").json()['token']
    user_2 = auth_register_v2_request("user2@mail.com", "password", "first", "last").json()['token']

    channel_1 = channels_create_v2_request(user_1, "channel1", False).json()['channel_id']
    channels_create_v2_request(user_1, "channel2", False)

    assert channels_list_v2_request(user_1).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'channel1'
            },
            {
                'channel_id': 1,
                'name': 'channel2'
            }
        ]
    }

    assert channels_list_v2_request(user_2).json() == {'channels': []}

    # Get user 2's id to invite
    user_2_id = auth_login_v2_request("user2@mail.com", "password").json()['auth_user_id']

    assert channel_invite_v2_request(user_1, channel_1, user_2_id)

    assert channels_list_v2_request(user_2).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'channel1'
            }
        ]
    }

# Tests for valid user ID
def test_invalid_auth_id():
    assert channels_list_v2_request(1234).status_code == 403
