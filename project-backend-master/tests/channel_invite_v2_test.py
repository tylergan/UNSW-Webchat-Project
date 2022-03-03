import pytest

from src.make_request_test import *


@pytest.fixture(autouse=True)
def clear():
    clear_v1_request()

@pytest.fixture
def inviter():
    return auth_register_v2_request("inviter@email.com", "password", "mister", "inviter").json()['token']

@pytest.fixture
def public(inviter):
    return channels_create_v2_request(inviter, 'The Funky Bunch', True).json()['channel_id']

@pytest.fixture
def private(inviter):
    return channels_create_v2_request(inviter, 'The Funky Bunch', False).json()['channel_id']

@pytest.fixture
def invitee_tkn():
    return auth_register_v2_request('invitee_id@email.com', 'password', 'mister', 'invited').json()['token']

@pytest.fixture
def invitee_id(invitee_tkn):
    return auth_login_v2_request('invitee_id@email.com', 'password').json()['auth_user_id']

@pytest.fixture
def invitee_id2():
    auth_register_v2_request('invitee_id2@email.com', 'password', 'mister', 'invited').json()['token']
    return auth_login_v2_request('invitee_id2@email.com', 'password').json()['auth_user_id']


def check_added(token, channel, user_id):
    members = channel_details_v2_request(token, channel).json()['all_members']
    assert any(user['u_id'] == user_id for user in members)



def test_successful_inv_public(inviter, public, invitee_id):
    assert channel_invite_v2_request(inviter, public, invitee_id).status_code == 200
    check_added(inviter, public, invitee_id)


def test_successful_inv_private(inviter, private, invitee_id):
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 200
    check_added(inviter, private, invitee_id)

def test_multiple_members_invited(inviter, private, invitee_id, invitee_id2):
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 200
    assert channel_invite_v2_request(inviter, private, invitee_id2).status_code == 200
    check_added(inviter, private, invitee_id)
    check_added(inviter, private, invitee_id2)

def test_invalid_auth_id(inviter, private, invitee_id):
    assert channel_invite_v2_request(1234, private, invitee_id).status_code == 403

def test_invalid_invitee_id(inviter, private):
    assert channel_invite_v2_request(inviter, private, 1234).status_code == 400

def test_invalid_channel_id(inviter, private, invitee_id):
    assert channel_invite_v2_request(inviter, 12356487, invitee_id).status_code == 400

def test_already_member(inviter, private, invitee_id):
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 200
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 400

def test_already_member_multiple(inviter, private, invitee_id, invitee_id2):
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 200
    assert channel_invite_v2_request(inviter, private, invitee_id2).status_code == 200

    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 400
    assert channel_invite_v2_request(inviter, private, invitee_id2).status_code == 400

def test_inviter_not_a_member(public, private, invitee_tkn, invitee_id2):
    assert channel_invite_v2_request(invitee_tkn, public, invitee_id2).status_code == 403
    assert channel_invite_v2_request(invitee_tkn, private, invitee_id2).status_code == 403

def test_invite_transitivity(inviter, private, invitee_id, invitee_tkn, invitee_id2):
    assert channel_invite_v2_request(invitee_tkn, private, invitee_id2).status_code == 403
    assert channel_invite_v2_request(inviter, private, invitee_id).status_code == 200
    assert channel_invite_v2_request(invitee_tkn, private, invitee_id2).status_code == 200
    check_added(inviter, private, invitee_id)
    check_added(inviter, private, invitee_id2)

def test_invite_removed_user(public, inviter, invitee_id):
    assert admin_user_remove_v1_request(inviter, invitee_id).status_code == 200
    assert channel_invite_v2_request(inviter, public, invitee_id).status_code == 400
