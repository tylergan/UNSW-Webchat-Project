import pytest

from src.make_request_test import *


@pytest.fixture(autouse=True)
def clear():
    clear_v1_request()


def test_basic_listall():
    inviter_id = auth_register_v2_request("inviter@email.com", "password", "mister", "inviter").json()['token']
    channels_create_v2_request(inviter_id, 'The Funky Bunch', True)

    assert channels_listall_v2_request(inviter_id).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'The Funky Bunch',
            }
        ]
    }


def test_basic_mult_list():
    inviter_id1 = auth_register_v2_request("inviter1@email.com", "password", "mister", "inviter1").json()['token']

    channels_create_v2_request(inviter_id1, 'The Funky Bunch', True)
    channels_create_v2_request(inviter_id1, 'The Wonky Bunch', True)
    channels_create_v2_request(inviter_id1, 'The Lanky Bunch', True)

    assert channels_listall_v2_request(inviter_id1).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'The Funky Bunch',
            },
            {
                'channel_id': 1,
                'name': 'The Wonky Bunch',
            },
            {
                'channel_id': 2,
                'name': 'The Lanky Bunch',
            }
        ]
    }

    inviter_id2 = auth_register_v2_request("inviter2@email.com", "password", "mister", "inviter2").json()['token']
    channels_create_v2_request(inviter_id2, 'The Funky Bunch', True)
    channels_create_v2_request(inviter_id2, 'The Wonky Bunch', True)
    channels_create_v2_request(inviter_id2, 'The Lanky Bunch', True)

    assert channels_listall_v2_request(inviter_id1).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'The Funky Bunch',
            },
            {
                'channel_id': 1,
                'name': 'The Wonky Bunch',
            },
            {
                'channel_id': 2,
                'name': 'The Lanky Bunch',
            },
            {
                'channel_id': 3,
                'name': 'The Funky Bunch',
            },
            {
                'channel_id': 4,
                'name': 'The Wonky Bunch',
            },
            {
                'channel_id': 5,
                'name': 'The Lanky Bunch',
            }
        ]
    }


def test_private_channels():
    inviter_id = auth_register_v2_request("inviter@email.com", "password", "mister", "inviter").json()['token']

    channels_create_v2_request(inviter_id, 'The Funky Bunch', False)
    channels_create_v2_request(inviter_id, 'The Wonky Bunch', True)
    channels_create_v2_request(inviter_id, 'The Lanky Bunch', False)

    assert channels_listall_v2_request(inviter_id).json() == {
        'channels': [
            {
                'channel_id': 0,
                'name': 'The Funky Bunch',
            },
            {
                'channel_id': 1,
                'name': 'The Wonky Bunch',
            },
            {
                'channel_id': 2,
                'name': 'The Lanky Bunch',
            }
        ]
    }


def test_basic_DNE_id():
    channels_listall_v2_request(22302).status_code == 403
