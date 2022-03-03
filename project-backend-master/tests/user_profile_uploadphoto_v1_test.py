import pytest
from src.make_request_test import *

jas = 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg'

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("u@m.com", "psword", "first", "last").json()

@pytest.fixture
def user2():
	return auth_register_v2_request("u2@m.com", "psword", "first", "last").json()

def test_invalid_token():
	assert user_profile_uploadphoto_v1_request('scarnoncunce', 'http://via.placeholder.com/150.JPG/FFFF00/000000/?text=1', 0, 0, 0, 0).status_code == 403

def test_boundaries(user):
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.JPG/FFFF00/000000/?text=2', 0, 0, 149, 149).status_code == 200
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.JPG/FFFF00/000000/?text=3', 0, 0, 150, 150).status_code == 400
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.JPG/FFFF00/000000/?text=4', 69, 0, 68, 1).status_code == 400
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.JPG/FFFF00/000000/?text=5', 0, 69, 1, 68).status_code == 400

def test_bad_url(user):
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://www.facebook.com/trololololol.JPG', 0, 0, 0, 0).status_code == 400
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://www.veryveryfakewebsitethatdoesntexist.com/blargh.JPG', 0, 0, 0, 0).status_code == 400

def test_bad_filetype(user):
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.PNG/FFFF00/000000/?text=6', 0, 0, 0, 0).status_code == 400
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/150.GIF/FFFF00/000000/?text=7', 0, 0, 0, 0).status_code == 400

def test_successful(user):
    assert user_profile_uploadphoto_v1_request(user['token'], jas, 50, 50, 140, 140).status_code == 200

def test_multiple_changes(user, user2):
    assert user_profile_uploadphoto_v1_request(user['token'], 'http://via.placeholder.com/100.JPG/FFFF00/000000/?text=userwon', 10, 10, 90, 90).status_code == 200
    assert user_profile_uploadphoto_v1_request(user2['token'], 'http://via.placeholder.com/100.JPG/FFFF00/000000/?text=usertoo', 0, 0, 99, 99).status_code == 200
    assert user_profile_uploadphoto_v1_request(user['token'], jas, 50, 50, 140, 140).status_code == 200