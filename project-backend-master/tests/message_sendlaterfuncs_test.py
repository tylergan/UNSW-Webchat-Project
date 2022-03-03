import pytest
import time
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def owner():
    return auth_register_v2_request('u@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def user():
	# Register an unused user to ensure not global owner
	auth_register_v2_request('u1@mail.com', 'password', 'first', 'last')
	return auth_register_v2_request('u2@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def ch_pub(owner):
	return channels_create_v2_request(owner, "public", True).json()['channel_id']

@pytest.fixture
def ch_priv(owner):
	return channels_create_v2_request(owner, "private", False).json()['channel_id']

@pytest.fixture
def dm(owner):
	return dm_create_v1_request(owner, []).json()['dm_id']

@pytest.fixture
def message():
    return 'Hello! I sent this message in the past!'

def test_status_code(owner, ch_pub, ch_priv, dm, message):
    time_sent = int(time.time()) + 3

    assert message_sendlater_v1_request(owner, ch_pub, message, time_sent).status_code == 200
    assert message_sendlater_v1_request(owner, ch_priv, message, time_sent).status_code == 200

    # will have to check this since it seemingly accepts a dm_id
    assert message_sendlaterdm_v1_request(owner, dm, message, time_sent).status_code == 200

def test_invalid_token(ch_pub, ch_priv, dm, message):
    time_sent = int(time.time()) + 3

    assert message_sendlater_v1_request('owner', ch_pub, message, time_sent).status_code == 403
    assert message_sendlater_v1_request('owner', ch_priv, message, time_sent).status_code == 403
    assert message_sendlater_v1_request('owner', dm, message, time_sent).status_code == 403

def test_invalid_channel_id(owner, message):
    time_sent = int(time.time()) + 3

    assert message_sendlater_v1_request(owner, 490234, message, time_sent).status_code == 400

def test_message_too_long(owner, ch_pub, ch_priv, dm):
    time_sent = int(time.time()) + 3
    message = 'a' * 1001

    assert message_sendlater_v1_request(owner, ch_pub, message, time_sent).status_code == 400
    assert message_sendlater_v1_request(owner, ch_priv, message, time_sent).status_code == 400
    assert message_sendlaterdm_v1_request(owner, dm, message, time_sent).status_code == 400

def test_sent_in_the_past(owner, ch_pub, ch_priv, message, dm):
    time_sent = int(time.time()) - 10
    assert message_sendlater_v1_request(owner, ch_pub, message, time_sent).status_code == 400
    assert message_sendlater_v1_request(owner, ch_priv, message, time_sent).status_code == 400
    assert message_sendlaterdm_v1_request(owner, dm, message, time_sent).status_code == 400

def test_user_is_not_member(user, ch_pub, ch_priv, dm, message):
    time_sent = int(time.time()) + 3

    assert message_sendlater_v1_request(user, ch_pub, message, time_sent).status_code == 403
    assert message_sendlater_v1_request(user, ch_priv, message, time_sent).status_code == 403
    assert message_sendlaterdm_v1_request(user, dm, message, time_sent).status_code == 403

def test_message_u_id(owner, ch_pub, ch_priv, message):
    time_sent = int(time.time()) + 1

    u_id = auth_login_v2_request('u@mail.com', 'password').json()['auth_user_id']

    assert message_sendlater_v1_request(owner, ch_pub, message, time_sent).status_code == 200
    assert message_sendlater_v1_request(owner, ch_priv, message, time_sent).status_code == 200

    time.sleep(1.5)

    message = channel_messages_v2_request(owner, ch_pub, 0).json()['messages'][0]
    assert message['u_id'] == u_id

    message = channel_messages_v2_request(owner, ch_priv, 0).json()['messages'][0]
    assert message['u_id'] == u_id 

def test_message_ids_unique_single_channel(owner, ch_pub, ch_priv):
    time_sent = int(time.time()) + 1
    used_ids = set()

    m_id = message_sendlater_v1_request(owner, ch_pub, "m", time_sent).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlater_v1_request(owner, ch_pub, "n", time_sent + 1).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlater_v1_request(owner, ch_priv, "o", time_sent + 2).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlater_v1_request(owner, ch_priv, "p", time_sent + 3).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)

def test_dm_ids_unique_multiple(owner, dm):
    time_sent = int(time.time()) + 1
    used_ids = set()

    dm2 = dm_create_v1_request(owner, []).json()['dm_id']

    m_id = message_sendlaterdm_v1_request(owner, dm, "m", time_sent).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlaterdm_v1_request(owner, dm, "n", time_sent + 1).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlaterdm_v1_request(owner, dm2, "o", time_sent + 2).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)
    m_id = message_sendlaterdm_v1_request(owner, dm2, "p", time_sent + 3).json()['message_id']
    assert m_id not in used_ids
    used_ids.add(m_id)

def test_timing(owner, ch_pub, dm):
    time_sent = int(time.time()) + 1
    m_id1 = message_sendlater_v1_request(owner, ch_pub, "m", time_sent).json()['message_id']
    m_id2 = message_sendlater_v1_request(owner, ch_pub, "n", time_sent + 1).json()['message_id']
    m_id3 = message_sendlater_v1_request(owner, ch_pub, "o", time_sent + 2).json()['message_id']

    time.sleep(3.1)

    messages = channel_messages_v2_request(owner, ch_pub, 0).json()['messages']

    for m_id, message in zip([m_id3, m_id2, m_id1], messages):
        assert m_id == message['message_id']

    time_sent = int(time.time()) + 1
    m_id1 = message_sendlaterdm_v1_request(owner, dm, "m", time_sent).json()['message_id']
    m_id2 = message_sendlaterdm_v1_request(owner, dm, "n", time_sent + 1).json()['message_id']
    m_id3 = message_sendlaterdm_v1_request(owner, dm, "o", time_sent + 2).json()['message_id']

    time.sleep(3.1)

    messages = dm_messages_v1_request(owner, dm, 0).json()['messages']

    for m_id, message in zip([m_id3, m_id2, m_id1], messages):
        assert m_id == message['message_id']