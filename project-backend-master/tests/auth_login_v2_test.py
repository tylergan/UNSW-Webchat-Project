import pytest
from src.error import InputError
from src.other import clear_v1

from src.make_request_test import *

# Reset application data before each test is run
@pytest.fixture(autouse=True)
def clear_data():
	clear_v1_request()

# Tests
def test_user_registered_1():
    user_reg = auth_register_v2_request("name@email.com", "password", "firstname", "lastname").json()
    user_log = auth_login_v2_request("name@email.com", "password").json()
    assert user_reg['auth_user_id'] == user_log['auth_user_id']
    assert user_reg['token'] != user_log['token']


def test_user_registered_2():
    user_reg = auth_register_v2_request("imashellio@gmail.com", "99Blueballoons", "Redmond", "Mobbs").json()
    user_log = auth_login_v2_request("imashellio@gmail.com", "99Blueballoons").json()
    assert user_reg['auth_user_id'] == user_log['auth_user_id']
    assert user_reg['token'] != user_log['token']


def test_multiple_users_registered():
    user1_reg = auth_register_v2_request("Avagrenouille@funkymail.com", "h1pp1tyh0pp1ty", "Ava", "Grenouille").json()
    user2_reg = auth_register_v2_request("Worrange@gmail.com", "7heReverend", "William", "Orange").json()
    user3_reg = auth_register_v2_request("haydensmith@outlook.com", "God1lovecomputerscience", "Hayden", "Smith").json()

    user2_log = auth_login_v2_request("Worrange@gmail.com", "7heReverend").json()
    user3_log = auth_login_v2_request("haydensmith@outlook.com", "God1lovecomputerscience").json()
    user1_log = auth_login_v2_request("Avagrenouille@funkymail.com", "h1pp1tyh0pp1ty").json()

    assert user1_reg['auth_user_id'] == user1_log['auth_user_id']
    assert user2_reg['auth_user_id'] == user2_log['auth_user_id']
    assert user3_reg['auth_user_id'] == user3_log['auth_user_id']

    assert user1_reg['token'] != user1_log['token']
    assert user2_reg['token'] != user2_log['token']
    assert user3_reg['token'] != user3_log['token']


def test_unregistered_email():
    auth_register_v2_request("name@email.com", "password", "firstname", "lastname")
    assert auth_login_v2_request("name@squeemail.com", "password").status_code == 400

def test_no_registered_emails():
    assert auth_login_v2_request("boost@juicemail.com", "Mang0Mag1c").status_code == 400

def test_incorrect_password():
    auth_register_v2_request("JamisonFawkes@gigglemail.boom", "Junkrat", "Jamison", "Fawkes")
    auth_register_v2_request("TheEngineer@mercmail.tf", "PracticalProblems", "Dell", "Conagher")

    assert auth_login_v2_request("JamisonFawkes@gigglemail.boom", "Roadhog").status_code == 400
    assert auth_login_v2_request("TheEngineer@mercmail.tf", "ConundrumsOfPhilosophy").status_code == 400

def test_removed_user():
    admin = auth_register_v2_request("JamisonFawkes@gigglemail.boom", "Junkrat", "Jamison", "Fawkes").json()['token']
    user = auth_register_v2_request("dsdfgh@gigglemail.boom", "Junkrat", "Jamison", "Fawkes").json()['auth_user_id']
    admin_user_remove_v1_request(admin, user)
    auth_login_v2_request("JamisonFawkes@gigglemail.boom", "Junkrat")
