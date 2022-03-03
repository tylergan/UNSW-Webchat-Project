import pytest
from src.make_request_test import *

@pytest.fixture(autouse=True)
def clear():
	clear_v1_request()

@pytest.fixture
def user():
	return auth_register_v2_request("e@mail.com", "psword", "user", "one").json()['token']

@pytest.fixture
def user2():
	return auth_register_v2_request("u@mail.com", "psword", "user", "two").json()

@pytest.fixture
def channel(user):
	return channels_create_v2_request(user, "newchannel", True).json()['channel_id']



def test_status(user):
	"Tests that a successful request returns with status 200."

	assert notifications_get_v1_request(user).status_code == 200

def test_invalid_token(user):
	"Tests that a made up, tampered or logged out token causes an access error"

	assert notifications_get_v1_request("qwerty").status_code == 403
	assert notifications_get_v1_request(user[1:]).status_code == 403
	auth_logout_v1_request(user)
	assert notifications_get_v1_request(user).status_code == 403

def test_no_notifications(user):
	"Tests that an empty list is returned when the user has no notifications"

	assert notifications_get_v1_request(user).json() == {'notifications': []}

def test_added_channel(user, channel, user2):
	"Tests that the correct notification format is returned when a user is added to a channel"

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	channel_invite_v2_request(user, channel, user2['auth_user_id'])
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone added you to newchannel"
		}]
	}

def test_added_dm(user, user2):
	"Tests that the correct notification format is returned when a user is added to a dm"

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	dm = dm_create_v1_request(user, [user2['auth_user_id']]).json()['dm_id']
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': -1,
			'dm_id': dm,
			'notification_message': "userone added you to userone, usertwo"
		}]
	}

def test_tagged_channel(user, channel, user2):
	"""Tests that the correct notification ocurrs when a user is tagged in a channel,
		and that the notifications are in the right order"""

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	channel_invite_v2_request(user, channel, user2['auth_user_id'])
	message_send_v1_request(user, channel, "hi @usertwo, can i borrow your credit card number")
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[
			{
				'channel_id': channel,
				'dm_id': -1,
				'notification_message': "userone tagged you in newchannel: hi @usertwo, can i b"
			},
			{
				'channel_id': channel,
				'dm_id': -1,
				'notification_message': "userone added you to newchannel"
			},
		]
	}

def test_tagged_dm(user, user2):
	"""Tests that the correct notification ocurrs when a user is tagged in a dm,
		and that the notifications are in the right order"""

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	dm = dm_create_v1_request(user, [user2['auth_user_id']]).json()['dm_id']
	message_senddm_v1_request(user, dm, "hello @usertwo")
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[
			{
				'channel_id': -1,
				'dm_id': dm,
				'notification_message': "userone tagged you in userone, usertwo: hello @usertwo"
			},
			{
				'channel_id': -1,
				'dm_id': dm,
				'notification_message': "userone added you to userone, usertwo"
			},
		]
	}

def test_tagged_edit(user, channel, user2):
	"Tests that the user is notified when a message is edited to add a tag"

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	channel_join_v2_request(user2['token'], channel)
	msg = message_send_v1_request(user, channel, "hi usertwo").json()['message_id']
	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	message_edit_v1_request(user, msg, "hi @usertwo!!!")
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo!!!"
		}]
	}

def test_tagged_share(user, channel, user2):
	channel_join_v2_request(user2['token'], channel)
	msg = message_send_v1_request(user, channel, "hello").json()['message_id']
	message_share_v1_request(user, msg, "@usertwo", channel, -1)
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': 'userone tagged you in newchannel: @usertwo\n > "hello"'
		}]
	}

def test_tagged_not_member(user, channel, user2):
	"Tests that the user is only notified when tagged if they are a member of the channel"

	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	message_send_v1_request(user, channel, "hi @usertwo!!!")
	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}

def test_react(user, channel, user2):
	assert notifications_get_v1_request(user2['token']).json() == {'notifications': []}
	channel_join_v2_request(user2['token'], channel)
	msg = message_send_v1_request(user2['token'], channel, "hello world").json()['message_id']
	message_react_v1_request(user, msg, 1)
	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone reacted to your message in newchannel"
		}]
	}

def test_many_notifications(user, channel, user2):
	"Tests that notification/get returns 20 notifications when the user has more"

	channel_join_v2_request(user2['token'], channel)
	for _ in range(25):
		message_send_v1_request(user, channel, "@usertwo ping")
	assert len(notifications_get_v1_request(user2['token']).json()['notifications']) == 20


def test_tag_multiple_users(user, channel, user2):
	"Tests that when multiple users are tagged in a message, they are all notified"

	user3 = auth_register_v2_request("a@mail.com", "psword", "user", "three").json()

	channel_join_v2_request(user2['token'], channel)
	channel_join_v2_request(user3['token'], channel)

	message_send_v1_request(user, channel, "hi @usertwo and @userthree")

	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo and @use"
		}]
	}

	assert notifications_get_v1_request(user3['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo and @use"
		}]
	}

def test_tag_multiple_users_multiple_times(user, channel, user2):
	"Tests that when multiple users are tagged multiple times, they are only notified once"

	user3 = auth_register_v2_request("a@mail.com", "psword", "user", "three").json()

	channel_join_v2_request(user2['token'], channel)
	channel_join_v2_request(user3['token'], channel)

	message_send_v1_request(user, channel, "hi @usertwo and @userthree and also @usertwo and @userthree")

	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo and @use"
		}]
	}

	assert notifications_get_v1_request(user3['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo and @use"
		}]
	}


def test_no_notification_on_previous_tag_edit(user, channel, user2):
	"""Tests that when a user is tagged in a message and this message is then edited,
		the user initially tagged is not notified again"""
		
	user3 = auth_register_v2_request("a@mail.com", "psword", "user", "three").json()

	channel_join_v2_request(user2['token'], channel)
	channel_join_v2_request(user3['token'], channel)

	msg = message_send_v1_request(user, channel, "hi @usertwo").json()['message_id']

	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo"
		}]
	}

	assert notifications_get_v1_request(user3['token']).json() == {'notifications': []}

	message_edit_v1_request(user, msg, "hi @usertwo and @userthree")

	assert notifications_get_v1_request(user2['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo"
		}]
	}
	
	assert notifications_get_v1_request(user3['token']).json() == \
	{'notifications':
		[{
			'channel_id': channel,
			'dm_id': -1,
			'notification_message': "userone tagged you in newchannel: hi @usertwo and @use"
		}]
	}