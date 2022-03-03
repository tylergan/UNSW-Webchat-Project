import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	user_data = auth_register_v2_request("u@mail.com", "password", "first", "last").json()
	return {'u_id': user_data['auth_user_id'], 'token': user_data['token']}

def test_logout_status(user):
	assert auth_logout_v1_request(user['token']).status_code == 200

def test_logout_bad_token():
	assert auth_logout_v1_request("QWERTY").status_code == 403

def test_logout_twice(user):
	assert auth_logout_v1_request(user['token']).status_code == 200
	assert auth_logout_v1_request(user['token']).status_code == 403

def test_logout_multiple_users():
	u1 = auth_register_v2_request("u1@mail.com", "password", "first", "last").json()['token']
	u2 = auth_register_v2_request("u2@mail.com", "password", "first", "last").json()['token']
	u3 = auth_register_v2_request("u3@mail.com", "password", "first", "last").json()['token']
	
	assert auth_logout_v1_request(u1).status_code == 200	
	assert auth_logout_v1_request(u2).status_code == 200
	assert auth_logout_v1_request(u3).status_code == 200

def test_logout_with_functions(user):
	assert channels_list_v2_request(user['token']).status_code == 200
	assert channels_listall_v2_request(user['token']).status_code == 200
	assert channels_create_v2_request(user['token'], 'channel', True).status_code == 200

	auth_logout_v1_request(user['token'])

	assert channels_list_v2_request(user['token']).status_code == 403
	assert channels_listall_v2_request(user['token']).status_code == 403
	assert channels_create_v2_request(user['token'], 'channel', True).status_code == 403

def test_logout_tampered_token(user):
	assert auth_logout_v1_request(user['token'] + 'a').status_code == 403