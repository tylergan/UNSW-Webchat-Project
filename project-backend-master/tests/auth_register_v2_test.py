import pytest
import json
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()
	pass

# Tests for valid registrations
def test_valid_register():
	register_return = auth_register_v2_request("user@mail.com", "password", "firstname", "lastname").json()
	login_return = auth_login_v2_request("user@mail.com", "password").json()
	assert register_return['auth_user_id'] == login_return['auth_user_id']
	assert register_return['token'] != login_return['token']

def test_multiple_valid_registers():
	register1_return = auth_register_v2_request("user1@mail.com", "password", "firstname", "lastname").json()
	login1_return = auth_login_v2_request("user1@mail.com", "password").json()
	assert register1_return['auth_user_id'] == login1_return['auth_user_id']
	assert register1_return['token'] != login1_return['token']

	register2_return = auth_register_v2_request("user2@mail.com", "password", "firstname", "lastname").json()
	login2_return = auth_login_v2_request("user2@mail.com", "password").json()
	assert register2_return['auth_user_id'] == login2_return['auth_user_id']
	assert register2_return['token'] != login2_return['token']


def test_user_token_unique():
	used_tokens = set()

	data = auth_register_v2_request("user1@mail.com", "password", "firstname", "lastname").json()
	assert data['token'] not in used_tokens
	used_tokens.add(data['token'])

	data = auth_register_v2_request("user2@mail.com", "password", "firstname", "lastname").json()
	assert data['token'] not in used_tokens
	used_tokens.add(data['token'])

	data = auth_register_v2_request("user3@mail.com", "password", "firstname", "lastname").json()
	assert data['token'] not in used_tokens
	used_tokens.add(data['token'])

	data = auth_register_v2_request("user4@mail.com", "password", "firstname", "lastname").json()
	assert data['token'] not in used_tokens
	used_tokens.add(data['token'])

def test_user_id():
	used_ids = set()

	data = auth_register_v2_request("user1@mail.com", "password", "firstname", "lastname").json()
	assert data['auth_user_id'] not in used_ids
	used_ids.add(data['auth_user_id'])

	data = auth_register_v2_request("user2@mail.com", "password", "firstname", "lastname").json()
	assert data['auth_user_id'] not in used_ids
	used_ids.add(data['auth_user_id'])

	data = auth_register_v2_request("user3@mail.com", "password", "firstname", "lastname").json()
	assert data['auth_user_id'] not in used_ids
	used_ids.add(data['auth_user_id'])

	data = auth_register_v2_request("user4@mail.com", "password", "firstname", "lastname").json()
	assert data['auth_user_id'] not in used_ids
	used_ids.add(data['auth_user_id'])

# Tests for invalid registrations

def test_invalid_email():
	assert auth_register_v2_request("usermail.com", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("user@mail", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("@mail.com", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("user*@mail.com", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("user@mail.", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("user@mail.c", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("user", "password", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("", "password", "firstname", "lastname").status_code == 400

def test_duplicate_email():
	auth_register_v2_request("user@mail.com", "password", "firstname", "lastname")
	assert auth_register_v2_request("user@mail.com", "password2", "firstname2", "lastname2").status_code == 400

	auth_register_v2_request("user2@mail.com", "password", "firstname", "lastname")
	assert auth_register_v2_request("user2@mail.com", "password2", "firstname2", "lastname2").status_code == 400
	assert auth_register_v2_request("user@mail.com", "password2", "firstname2", "lastname2").status_code == 400

def test_password_too_short():
	assert auth_register_v2_request("firstname@mail.com", "", "firstname", "lastname").status_code == 400
	assert auth_register_v2_request("firstname1@mail.com", "12345", "firstname", "lastname").status_code == 400

def test_first_name_empty():
	assert auth_register_v2_request("firstname@mail.com", "password", "", "lastname").status_code == 400

def test_first_name_too_long():
	assert auth_register_v2_request("firstname@mail.com", "password", "a" * 51, "lastname").status_code == 400

def test_last_name_empty():
	assert auth_register_v2_request("firstname@mail.com", "password", "firstname", "").status_code == 400

def test_last_name_too_long():
	assert auth_register_v2_request("firstname@mail.com", "password", "firstname", "a" * 51).status_code == 400