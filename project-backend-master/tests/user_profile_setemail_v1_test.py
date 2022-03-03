import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("u@m.com", "psword", "first", "last").json()

def test_status(user):
	assert user_profile_setemail_v1_request(user['token'], "new@email.com").status_code == 200

def test_return(user):
	assert user_profile_setemail_v1_request(user['token'], "new@email.com").json() == {}

def test_email_changed(user):
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['email'] == "u@m.com"
	user_profile_setemail_v1_request(user['token'], "new@email.com").json()
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['email'] == "new@email.com"

def test_invalid_email_format(user):
	assert user_profile_setemail_v1_request(user['token'], "usermail.com").status_code == 400	
	assert user_profile_setemail_v1_request(user['token'], "user@mail").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "@mail.com").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "user*@mail.com").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "user@mail.").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "user@mail.c").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "user").status_code == 400
	assert user_profile_setemail_v1_request(user['token'], "").status_code == 400

def test_email_in_use(user):
	u2 = auth_register_v2_request("u2@m.com", "psword", "blake", "morris").json()['token']
	assert user_profile_setemail_v1_request(user['token'], "u2@m.com").status_code == 400
	user_profile_setemail_v1_request(u2, "new@email.com")
	assert user_profile_setemail_v1_request(user['token'], "u2@m.com").status_code == 200
	assert user_profile_v1_request(user['token'], user['auth_user_id']).json()['user']['email'] == "u2@m.com"

def test_invalid_token(user):
	assert user_profile_setemail_v1_request('sdfjgkl', 'new@email.com').status_code == 403

	assert user_profile_setemail_v1_request(user['token'][:-1] + '~', 'new@email.com').status_code == 403

	auth_logout_v1_request(user['token'])
	assert user_profile_setemail_v1_request(user['token'], 'new@email.com').status_code == 403
