import pytest
from src.make_request_test import *
import time


@pytest.fixture(autouse=True)
def clear():
    clear_v1_request()


@pytest.fixture
def user():
    user = auth_register_v2_request("u@mail.com", "psword", "blake", "morris").json()
    print(f"User ID: {user['auth_user_id']}")
    return user['token']


@pytest.fixture
def user2():
    return auth_register_v2_request("u2@mail.com", "psword", "hayden", "smith").json()['token']


@pytest.fixture
def channel(user):
    return channels_create_v2_request(user, "channel", True).json()['channel_id']


def test_status(user, channel):
    standup_start_v1_request(user, channel, 1)
    assert standup_send_v1_request(
        user, channel, "my catfish ate a kmart toaster").status_code == 200
    time.sleep(1.1)


def test_invalid_channel(user):
    standup_send_v1_request(user, 12345678, "hello").status_code == 400


def test_invalid_length(user, channel):
    standup_start_v1_request(user, channel, 1)
    assert standup_send_v1_request(user, channel, "").status_code == 400
    assert standup_send_v1_request(user, channel, "a").status_code == 200
    assert standup_send_v1_request(
        user, channel, "a" * 1000).status_code == 200
    assert standup_send_v1_request(
        user, channel, "a" * 1001).status_code == 400
    time.sleep(1.1)


def test_no_standup(user, channel):
    assert standup_send_v1_request(user, channel, "hello").status_code == 400


def test_not_member(user2, user, channel):
    standup_start_v1_request(user, channel, 1)
    assert standup_send_v1_request(user2, channel, "hello").status_code == 403
    time.sleep(1.1)


def test_invalid_token(user, channel):
    standup_start_v1_request(user, channel, 1)

    assert standup_send_v1_request(
        "qwerty", channel, "hello").status_code == 403

    assert standup_send_v1_request(
        "~" + user[1:], channel, "hello").status_code == 403

    auth_logout_v1_request(user)

    assert standup_send_v1_request(user, channel, "hello").status_code == 403
    time.sleep(1.1)


def test_one_message(user, channel):
    standup_start_v1_request(user, channel, 1)

    standup_send_v1_request(user, channel, "my catfish ate a kmart toaster")

    time.sleep(1.1)

    assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['message'] \
        == "blakemorris: my catfish ate a kmart toaster"


def test_multiple_messages(user, channel):
    standup_start_v1_request(user, channel, 1)

    standup_send_v1_request(user, channel, "aaa")
    standup_send_v1_request(user, channel, "bbb")
    standup_send_v1_request(user, channel, "ccc")

    time.sleep(1.25)

    assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['message'] \
        == "blakemorris: aaa\nblakemorris: bbb\nblakemorris: ccc"


def test_multiple_users(user, user2, channel):
    print("TEST_MULTIPLE_USERS")
    channel_join_v2_request(user2, channel)

    standup_start_v1_request(user, channel, 1)

    standup_send_v1_request(user2, channel, "aaa")
    standup_send_v1_request(user, channel, "bbb")
    standup_send_v1_request(user2, channel, "ccc")

    time.sleep(1.25)

    assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['message'] \
        == "haydensmith: aaa\nblakemorris: bbb\nhaydensmith: ccc"


def test_concurrent(user, user2, channel):
    print("TEST_CONCURRENT")
    channel2 = channels_create_v2_request(
        user, "channel2", True).json()['channel_id']

    channel_join_v2_request(user2, channel)
    channel_join_v2_request(user2, channel2)

    standup_start_v1_request(user, channel, 1)
    standup_start_v1_request(user, channel2, 1)

    standup_send_v1_request(user2, channel, "aaa")
    standup_send_v1_request(user, channel2, "aaa")

    standup_send_v1_request(user, channel, "bbb")
    standup_send_v1_request(user2, channel2, "bbb")

    standup_send_v1_request(user2, channel, "ccc")
    standup_send_v1_request(user, channel2, "ccc")

    time.sleep(1.25)

    assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['message'] \
        == "haydensmith: aaa\nblakemorris: bbb\nhaydensmith: ccc"

    assert channel_messages_v2_request(user, channel2, 0).json()['messages'][0]['message'] \
        == "blakemorris: aaa\nhaydensmith: bbb\nblakemorris: ccc"


def test_long(user, channel):
    print("TEST_LONG")

    # Check that a standup where the compiled length exceeds the usual message length limit
    # is sent correctly

    standup_start_v1_request(user, channel, 1)

    standup_send_v1_request(user, channel, "a" * 1000)
    standup_send_v1_request(user, channel, "b" * 1000)

    time.sleep(1.25)

    assert channel_messages_v2_request(user, channel, 0).json()['messages'][0]['message'] \
        == f"blakemorris: {'a' * 1000}\nblakemorris: {'b' * 1000}"
