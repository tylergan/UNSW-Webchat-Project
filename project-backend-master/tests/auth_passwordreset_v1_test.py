import pytest
from src.auth import data_store
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

def test_invalid_reset_code():
    assert auth_passwordreset_reset_v1_request(123, 'newpassword').status_code == 400
    assert auth_passwordreset_reset_v1_request(-1, 'newpassword').status_code == 400

def test_password_too_short():
    email = "testemail@gmail.com"
    auth_register_v2_request(email, "password", "vu", "luu")
    auth_passwordreset_v1_request('testemail@gmail.com')

    store = data_store.get()
    users = store['users']
    reset_code = ''
    for user in users:
        if user['email'] == email:
            reset_code = user['reset_code']
            break

    assert auth_passwordreset_reset_v1_request(reset_code, '123').status_code == 400








    

    