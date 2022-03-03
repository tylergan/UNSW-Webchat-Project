import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user_email():
    user_email = 'dummyemail6767@gmail.com'
    auth_register_v2_request(user_email, "password", "firstname", "lastname")
    return user_email

def test_invalid_email():
    assert auth_passwordreset_v1_request('c8786').status_code == 200

def test_working_passwordreset_request(user_email):
    assert auth_passwordreset_v1_request(user_email).status_code == 200

def test_passwordreset_same_user_twice(user_email):
    assert auth_passwordreset_v1_request(user_email).status_code == 200
    auth_login_v2_request(user_email, "password")
    assert auth_passwordreset_v1_request(user_email).status_code == 200

def test_passwordreset_multiple_users():
    auth_register_v2_request("user1@gmail.com", "password", "firstname", "lastname")
    auth_register_v2_request("user2@gmail.com", "password", "firstname", "lastname")
    auth_register_v2_request("user3@gmail.com", "password", "firstname", "lastname")

    assert auth_passwordreset_v1_request("user1@gmail.com").status_code == 200
    assert auth_passwordreset_v1_request("user2@gmail.com").status_code == 200
    assert auth_passwordreset_v1_request("user3@gmail.com").status_code == 200

def test_passwordreset_logout_sessions_with_functions():
    user = auth_register_v2_request("dummyemail6767@gmail.com", "password", "first", "last").json()['token']
    auth_passwordreset_v1_request("dummyemail6767@gmail.com")
    assert auth_logout_v1_request(user).status_code == 403

def test_no_users():
    assert auth_passwordreset_v1_request("blake@mail.com").status_code == 200