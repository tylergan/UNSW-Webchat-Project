import pytest

from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear_data():
	clear_v1_request()

def test_users_clear():
	# Successfully register and login a user
	user = auth_register_v2_request("user@mail.com", "password", "first", "last").json()['auth_user_id']
	assert auth_login_v2_request("user@mail.com", "password").json()['auth_user_id'] == user

	clear_v1_request()

	assert auth_login_v2_request("user@mail.com", "password").status_code == 400

def test_channels_clear():
	# Successfully register and login a user
	user = auth_register_v2_request("user@mail.com", "password", "first", "last").json()
	u_id = user['auth_user_id']
	assert auth_login_v2_request("user@mail.com", "password").json()['auth_user_id'] == u_id

	# Successfully create a channel and get its details
	channel = channels_create_v2_request(user['token'], "channel_name", True).json()
	assert channel_details_v2_request(user['token'], channel['channel_id']).status_code == 200

	clear_v1_request()

	assert channel_details_v2_request(user['token'], channel['channel_id']).status_code == 400

