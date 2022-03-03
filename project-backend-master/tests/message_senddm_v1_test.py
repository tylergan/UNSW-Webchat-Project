import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def dm_owner():
	return auth_register_v2_request('u@mail.com', 'password', 'first', 'last').json()['token']

@pytest.fixture
def dm(dm_owner):
	return dm_create_v1_request(dm_owner, []).json()['dm_id']

def test_status_code(dm_owner, dm):
	assert message_senddm_v1_request(dm_owner, dm, "hello world").status_code == 200

def test_dm_ids_unique(dm_owner, dm):
	used_ids = set()
	m_id = message_senddm_v1_request(dm_owner, dm, "a").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm, "b").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm, "c").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm, "d").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)

def test_dm_ids_unique_multiple(dm_owner, dm):
	dm2 = dm_create_v1_request(dm_owner, []).json()['dm_id']
	used_ids = set()
	m_id = message_senddm_v1_request(dm_owner, dm, "a").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm2, "b").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm, "c").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)
	m_id = message_senddm_v1_request(dm_owner, dm2, "d").json()['message_id']
	assert m_id not in used_ids
	used_ids.add(m_id)

def test_invalid_dm_id(dm_owner):
	assert message_senddm_v1_request(dm_owner, 12356748, "play outer wilds").status_code == 400

def test_invalid_token(dm_owner, dm):
	# Not a token
	assert message_senddm_v1_request(dm_owner, dm, "message").status_code == 200
	assert message_senddm_v1_request("QWERTY", dm, "message").status_code == 403

	# Tampered token
	assert message_senddm_v1_request(dm_owner[:-1] + '~', dm, "message").status_code == 403

	# Session ended
	assert message_senddm_v1_request(dm_owner, dm, "message").status_code == 200
	auth_logout_v1_request(dm_owner)
	assert message_senddm_v1_request(dm_owner, dm, "message").status_code == 403

def test_invalid_msg_len(dm_owner, dm):
	# Too short
	assert message_senddm_v1_request(dm_owner, dm, "").status_code == 400
	
	# OK
	assert message_senddm_v1_request(dm_owner, dm, "a").status_code == 200
	assert message_senddm_v1_request(dm_owner, dm, "a" * 1000).status_code == 200
	
	# Too long
	assert message_senddm_v1_request(dm_owner, dm, "a" * 1001).status_code == 400

def test_not_member(dm):
	user = auth_register_v2_request("u2@mail.com", "password", "first", "last").json()['token']
	assert message_senddm_v1_request(user, dm, "!@#$%^&*()").status_code == 403

def test_left_dm(dm_owner, dm):
	assert message_senddm_v1_request(dm_owner, dm, "ok").status_code == 200
	dm_leave_v1_request(dm_owner, dm)
	assert message_senddm_v1_request(dm_owner, dm, "ok").status_code == 403