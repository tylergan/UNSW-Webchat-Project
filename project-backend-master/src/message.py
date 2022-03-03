from logging import Handler
from src.data_store import data_store
from src.error import AccessError, InputError
from src.validation import *
from datetime import datetime, timezone
from src.user import stat_update, global_stat_update
from src.notifications import send_notification
import re
import time
from threading import Lock

LOCK = Lock()

# Returns a list of u_ids from tags in 'message' referring to an existing user.
def find_tags(message):
	# Find tag matches in the message
	# Remove the '@' to get just the handles
	handles = [s[1:] for s in re.findall('@[a-zA-Z0-9]+', message)]

	# Convert to u_ids, excluding invalid handles
	users = data_store.get()['users']
	u_ids = [u['u_id'] for u in users if u['handle_str'] in handles]
	return u_ids


def message_send_v1(token, channel_id, message, ignore_len=False, message_id=None):
	'''
	Sends a message to a channel (channel_id) from a user (token).
	The message is saved with a message_id, the u_id of the sender, the message contents and
	time_created as an integer Unix timestamp.

	Arguments:
		token (string)		- authorisation token of the user (session) sending the message
		channel_id (int)	- id of the channel to which the message is being sent
		message (string)	- contents of the message to send

	Exceptions:
		InputError - Occurs when:
			> channel_id does not refer to a valid channel
			> length of message is not 1..1000 characters (inclusive)
		
		AccessError - Occers when:
			> token is invalid
			> user is not a member of the (valid) channel

	Return Value:
		Returns a dictionary containing a unique integer 'message_id'
	'''
	### Error handling ###
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	if not valid_channel_id(channel_id):
		raise InputError(description="Invalid channel_id")

	u_id = token_user(token)

	if not user_is_member(u_id, channel_id):
		raise AccessError(description="User is not a member of this channel")
	
	if (not 1 <= len(message) <= 1000) and not ignore_len:
		raise InputError(description="Message length must be between 1 and 1000 chars (inclusive)")
	
	### Implementation ###

	# Update statistics
	stat_update(u_id, 'messages_sent', 1)
	global_stat_update('messages_exist', 1)

	# Get the channel to send the message to
	store = data_store.get()
	channel = store['channels'][channel_id]

	# Assign a unique message_id
	if message_id is None:
		message_id = store['curr_message_id']
		store['curr_message_id'] += 1

	# Ping tagged users who are members of the channel
	handle = store['users'][u_id]['handle_str']
	ch_name = store['channels'][channel_id]['name']

	for user in filter(lambda x: user_is_member(x, channel_id), find_tags(message)):
		send_notification(user, f"{handle} tagged you in {ch_name}: {message[:20]}", channel_id)

	# Add the message to the channel
	# Add to the front of the list due to channel/messages implementation
	msg = {
		'message_id': message_id,
		'u_id': u_id,
		'message': message,
		'time_created': int(datetime.now(timezone.utc).timestamp()),
		'reacts': [{'react_id': 1, 'u_ids': []}],
		'is_pinned': False
	}

	channel['messages'].insert(0, msg)

	# Update the message info mapping
	store['message_info'][message_id] = {
		'type': 'channels',
		'sender': u_id,
		'to': channel_id
	}

	data_store.set(store)

	return {'message_id': message_id}


def message_senddm_v1(token, dm_id, message, ignore_len=False, message_id=None):
	'''
	Sends a message to a dm (dm_id) from a user (token).
	The message is saved with a message_id, the u_id of the sender, the message contents and
	time_created as an integer Unix timestamp.

	Arguments:
		token (string)		- authorisation token of the user (session) sending the message
		dm_id (int)			- id of the dm to which the message is being sent
		message (string)	- contents of the message to send

	Exceptions:
		InputError - Occurs when:
			> dm_id does not refer to a valid dm
			> length of message is not 1..1000 characters (inclusive)
		
		AccessError - Occers when:
			> token is invalid
			> user is not a member of the (valid) dm

	Return Value:
		Returns a dictionary containing a unique integer 'message_id'
	'''
	### Error handling ###
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	if not valid_dm_id(dm_id):
		raise InputError(description="Invalid dm_id")

	u_id = token_user(token)

	if not user_is_member(u_id, dm_id, 'dms'):
		raise AccessError(description="User is not a member of this dm")
	
	if (not 1 <= len(message) <= 1000) and not ignore_len:
		raise InputError(description="Message length must be between 1 and 1000 chars (inclusive)")
	
	### Implementation ###

	# Update statistics
	stat_update(u_id, 'messages_sent', 1)
	global_stat_update('messages_exist', 1)

	# Get the channel to send the messgae to
	store = data_store.get()
	dm = store['dms'][dm_id]

	# Assign a unique message_id
	if message_id is None:
		message_id = store['curr_message_id']
		store['curr_message_id'] += 1

	# Ping tagged users who are members of the dm
	handle = store['users'][u_id]['handle_str']
	dm_name = store['dms'][dm_id]['name']
	
	for user in filter(lambda x: user_is_member(x, dm_id, chat_type='dms'), find_tags(message)):
		send_notification(user, f"{handle} tagged you in {dm_name}: {message[:20]}", dm=dm_id)

	# Add the message to the channel
	# Add to the front of the list due to channel/messages implementation
	msg = {
		'message_id': message_id,
		'u_id': u_id,
		'message': message,
		'time_created': int(datetime.now(timezone.utc).timestamp()),
		'reacts': [{'react_id': 1, 'u_ids': []}],
		'is_pinned': False
	}
	
	dm['messages'].insert(0, msg)

	# Update the message info mapping
	store['message_info'][message_id] = {
		'type': 'dms',
		'sender': u_id,
		'to': dm_id
	}

	data_store.set(store)

	return {'message_id': message_id}

def set_message_contents(message_id, to, chat_type, contents):
	store = data_store.get()
	for i, msg in enumerate(store[chat_type][to]['messages']):
		if msg['message_id'] == message_id:
			store[chat_type][to]['messages'][i]['message'] = contents
	data_store.set(store)

def remove_message(message_id, to, chat_type):
	# Update statistics
	global_stat_update('messages_exist', -1)

	store = data_store.get()
	for i, msg in enumerate(store[chat_type][to]['messages']):
		if msg['message_id'] == message_id:
			store[chat_type][to]['messages'].pop(i)
	data_store.set(store)

def message_edit_v1(token, message_id, message):
	'''
	Edits a message (message_id) to contain the text (message).
	If the new (message) is empty, the message is deleted.

	Arguments:
		token (string)		- authorisation token of the user (session) editing the message
		message_id (int)	- id of the message to edit
		message (string)	- contents of the message to replace previous version with

	Exceptions:
		InputError - Occurs when:
			> message_id does not refer to a valid message within a channel/dm that the user
			  has joined
			> length of message is more than 1000 characters
		
		AccessError - Occers when:
			> token is invalid
			> message_id is valid AND user is a member of the channel
			  AND message was not sent by the user AND user does not have owner permissions
			  in the channel

	Return Value:
		Returns an empty dictionary
	'''
	### Error handling ###
	
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	u_id = token_user(token)

	store = data_store.get()
	
	# Get the message_id -> details mapping
	msgs = store['message_info']

	if message_id not in msgs.keys():
		raise InputError(description="Message does not exist")

	# Determine whether the message is in a channel or a dm
	chat_type = msgs[message_id]['type']
	
	# Determine the specific channel or dm the message is in
	to = msgs[message_id]['to']

	if not user_is_member(u_id, to, chat_type):
		raise InputError(description="Message does not exist")
	
	sender = msgs[message_id]['sender']

	# Access error if the user isn't either the sender of the message or a channel/global owner
	if not (sender == u_id or user_has_owner_perms(u_id, to, chat_type)):
		raise AccessError(description="User does not have permission to edit this message")
	
	if len(message) > 1000:
		raise InputError(description="Message must not be over 1000 chars")

	### Implementation ###

	# Get the old message
	old_msg = list(filter(lambda x: x['message_id'] == message_id, store[chat_type][to]['messages']))[0]['message']
	
	# Ping tagged users who are members of the channel/dm and weren't already tagged in the message
	old_tags = find_tags(old_msg)
	new_tags = find_tags(message)

	diff_tags = set(new_tags) - set(old_tags)

	handle = store['users'][u_id]['handle_str']
	chat_name = store[chat_type][to]['name']
	dm_id = to if chat_type == 'dms' else -1
	channel_id = to if chat_type == 'channels' else -1
	
	for user in filter(lambda x: user_is_member(x, to, chat_type=chat_type), diff_tags):
		send_notification(user, f"{handle} tagged you in {chat_name}: {message[:20]}", channel_id, dm_id)

	# If the new message is empty, the message is deleted
	if message == "":
		remove_message(message_id, to, chat_type)
		return {}

	set_message_contents(message_id, to, chat_type, message)


	return {}

def message_remove_v1(token, message_id):
	'''
	Removes a message (message_id) from a channel or dm.

	Arguments:
		token (string)		- authorisation token of the user (session) removing the message
		message_id (int)	- id of the message to remove

	Exceptions:
		InputError - Occurs when:
			> message_id does not refer to a valid message within a channel/dm that the user
			  has joined
		
		AccessError - Occers when:
			> token is invalid
			> message_id is valid AND user is a member of the channel
			  AND message was not sent by the user AND user does not have owner permissions
			  in the channel

	Return Value:
		Returns an empty dictionary
	'''
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	u_id = token_user(token)

	store = data_store.get()
	
	# Get the message_id -> details mapping
	msgs = store['message_info']

	if message_id not in msgs.keys():
		raise InputError(description="Message does not exist")

	# Determine whether the message is in a channel or a dm
	chat_type = msgs[message_id]['type']
	
	# Determine the specific channel or dm the message is in
	to = msgs[message_id]['to']

	if not user_is_member(u_id, to, chat_type):
		raise InputError(description="Message does not exist")
	
	sender = msgs[message_id]['sender']

	# Access error if the user isn't either the sender of the message or a channel/global owner
	if not (sender == u_id or user_has_owner_perms(u_id, to, chat_type)):
		raise AccessError(description="User does not have permission to edit this message")
	
	# Remove the message from the chat
	remove_message(message_id, to, chat_type)

	# Remove the message from the message info mapping
	msgs.pop(message_id)

	data_store.set(store)
	return {}

def message_react_v1(token, message_id, react_id):
	'''
	Adds a reaction 'react_id' to the message 'message_id' from the authorised user.

	Arguments:
		token (string)		- authorisation token of the user (session) reacting to the message
		message_id (int)	- id of the message to react to
		react_id (int)		- id of the reaction type to add

	Exceptions:
		InputError - Occurs when:
			> message_id does not refer to a valid message within a channel/dm that the user
			  has joined
			> react_id does not refer to a valid react type - see the list 'valid_reacts' below
			> The user has already reacted to this message with this react_id
		
		AccessError - Occers when:
			> token is invalid

	Return Value:
		Returns an empty dictionary
	'''
	valid_reacts = [1]

	# Error handling
	if not valid_token(token):
		raise AccessError(description="Token is invalid")

	if react_id not in valid_reacts:
		raise InputError(description="Invalid react ID")

	u_id = token_user(token)


	# Get the message_id -> details mapping
	store = data_store.get()
	msgs = store['message_info']

	if message_id not in msgs.keys():
		raise InputError(description="Message does not exist")

	# Determine whether the message is in a channel or a dm
	chat_type = msgs[message_id]['type']
	
	# Determine the specific channel or dm the message is in
	to = msgs[message_id]['to']

	if not user_is_member(u_id, to, chat_type):
		raise InputError(description="Message does not exist")

	if user_has_reacted(u_id, message_id, react_id):
		raise InputError(description="User has already reacted to this message with this react")

	# Implementation
	# Add the react to the message
	for i, msg in enumerate(store[chat_type][to]['messages']):
		if msg['message_id'] == message_id:
			store[chat_type][to]['messages'][i]['reacts'][i - 1]['u_ids'].append(u_id)
	data_store.set(store)


	# Notify the message sender
	sender = msgs[message_id]['sender']
	handle = store['users'][u_id]['handle_str']
	chat_name = store[chat_type][to]['name']
	dm_id = to if chat_type == 'dms' else -1
	channel_id = to if chat_type == 'channels' else -1

	send_notification(sender, f"{handle} reacted to your message in {chat_name}", channel_id, dm_id)

	return {}

def message_unreact_v1(token, message_id, react_id):
	'''
	Removes a reaction 'react_id' from the message 'message_id' from the authorised user.

	Arguments:
		token (string)		- authorisation token of the user (session) unreacting to the message
		message_id (int)	- id of the message to remove react from
		react_id (int)		- id of the reaction type to remove

	Exceptions:
		InputError - Occurs when:
			> message_id does not refer to a valid message within a channel/dm that the user
			  has joined
			> react_id does not refer to a valid react type - see the list 'valid_reacts' below
			> The user has not reacted to this message with this react_id
		
		AccessError - Occers when:
			> token is invalid

	Return Value:
		Returns an empty dictionary
	'''
	valid_reacts = [1]

	# Error handling
	if not valid_token(token):
		raise AccessError(description="Token is invalid")

	if react_id not in valid_reacts:
		raise InputError(description="Invalid react ID")

	u_id = token_user(token)


	# Get the message_id -> details mapping
	store = data_store.get()
	msgs = store['message_info']

	if message_id not in msgs.keys():
		raise InputError(description="Message does not exist")

	# Determine whether the message is in a channel or a dm
	chat_type = msgs[message_id]['type']
	
	# Determine the specific channel or dm the message is in
	to = msgs[message_id]['to']

	if not user_is_member(u_id, to, chat_type):
		raise InputError(description="Message does not exist")

	if not user_has_reacted(u_id, message_id, react_id):
		raise InputError(description="User has not reacted to this message with this react")

	# Implementation
	# Remove the react from the message
	for i, msg in enumerate(store[chat_type][to]['messages']):
		if msg['message_id'] == message_id:
			store[chat_type][to]['messages'][i]['reacts'][i - 1]['u_ids'].remove(u_id)
	data_store.set(store)

	return {}

def message_pin_v1(token, message_id):
	if not valid_token(token):
		raise AccessError(description="Token is invalid")

	u_id = token_user(token)
	pin_message(u_id, message_id)

	return {}

def message_unpin_v1(token, message_id):
	if not valid_token(token):
		raise AccessError(description="Token is invalid")

	u_id = token_user(token)
	pin_message(u_id, message_id, pin_mode=False)

	return {}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
	if not valid_token(token):
		raise AccessError(description="Token is invalid")
	
	if channel_id != -1 and dm_id != -1:
		raise InputError(description="Channel ID or DM ID must be -1")
	
	if not (valid_channel_id(channel_id) or valid_dm_id(dm_id)):
		raise InputError(description="Channel/DM ID is invalid")
	
	# Get the message_id -> details mapping
	store = data_store.get()
	msgs = store['message_info']
	u_id = token_user(token)

	if og_message_id not in msgs.keys():
		raise InputError(description="Message does not exist")

	# Determine whether the message is in a channel or a dm
	chat_type = msgs[og_message_id]['type']
	
	# Determine the specific channel or dm the message is in
	to = msgs[og_message_id]['to']

	if not user_is_member(u_id, to, chat_type):
		raise InputError(description="Message does not exist")

	if len(message) > 1000:
		raise InputError(description="Message must be less thatn 1000 chars")

	# Get the contents of the shared message
	og_text = list(filter(lambda m: m['message_id'] == og_message_id, store[chat_type][to]["messages"]))[0]['message']

	share_message = f'{message}\n > "{og_text}"'

	if dm_id == -1:
		m_id = message_send_v1(token, channel_id, share_message, ignore_len=True)['message_id']
	
	else:
		m_id = message_senddm_v1(token, dm_id, share_message, ignore_len=True)['message_id']
	

	return {'shared_message_id': m_id}

def message_sendlater_v1(token, channel_id, message, time_sent):
	'''
	Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.

	Arguments:
		token (string)		- authorisation token of the user (session) unreacting to the message
		channel_id (int)    - id of the targeted channel
		message (string)	- id of the message to remove react from
		time_sent (int)		- time for when message will be sent

	Exceptions:
		InputError - Occurs when:
			> channel_id does not refer to a valid channel
			> length of message is over 1000 characters
			> time_sent is a time in the past
		
		AccessError - Occers when:
			> token is invalid
			> channel_id is valid and the authorised user is not a member of the channel they are trying to post to

	Return Value:
		{ message_id }
	'''
	print("Send later channel")
	print(token, channel_id, message, time_sent)
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	if not valid_channel_id(channel_id):
		raise InputError(description="Invalid channel_id")

	if len(message) > 1000:
		raise InputError(description="Message length must be between 1 and 1000 chars (inclusive)")

	if int(time_sent) < int(time.time()):
		raise InputError(description='time_sent is a time in the past')

	u_id = token_user(token)
	if not user_is_member(u_id, channel_id):
		raise AccessError(description="User is not a member of this channel")

	with LOCK:
		store = data_store.get()
		message_id = store['curr_message_id']
		store['curr_message_id'] += 1

		msg_data = {
			'token': token,
			'channel_id': channel_id,
			'type': 'channels',
			'message_id': message_id,
			'message': message,
			'time_sent': int(time_sent)
		}

		store['msg_queue'].append(msg_data)
		store['msg_queue'].sort(key=lambda x: x['time_sent'])
		data_store.set(store)

	return {'message_id': message_id}

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
	'''
	Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.
	Arguments:
		token (string)		- authorisation token of the user (session) unreacting to the message
		dm_id (int)         - id of the targeted dm
		message (string)	- id of the message to remove react from
		time_sent (int)		- time for when message will be sent

	Exceptions:
		InputError - Occurs when:
			> channel_id does not refer to a valid channel
			> length of message is over 1000 characters
			> time_sent is a time in the past
		
		AccessError - Occers when:
			> token is invalid
			> channel_id is valid and the authorised user is not a member of the channel they are trying to post to

	Return Value:
		{ message_id }
	'''
	print("Send later DM")
	print(token, dm_id, message, time_sent)
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	if not valid_dm_id(dm_id):
		raise InputError(description="Invalid dm_id")

	if len(message) > 1000:
		raise InputError(description="Message length must be between 1 and 1000 chars (inclusive)")

	if int(time_sent) < int(time.time()):
		raise InputError(description='time_sent is a time in the past')

	u_id = token_user(token)
	if not user_is_member(u_id, dm_id, chat_type='dms'):
		raise AccessError(description="User is not a member of this dm")

	with LOCK:
		store = data_store.get()
		message_id = store['curr_message_id']
		store['curr_message_id'] += 1

		msg_data = {
			'token': token,
			'dm_id': dm_id,
			'type': 'dms',
			'message_id': message_id,
			'message': message,
			'time_sent': int(time_sent)
		}

		store['msg_queue'].append(msg_data)
		store['msg_queue'].sort(key=lambda x: x['time_sent'])
		data_store.set(store)

	return {'message_id': message_id}
