from src.error import InputError, AccessError
from src.notifications import send_notification
from src.validation import message_with_user_react, valid_token, valid_user_id, token_user, get_user_details, valid_dm_id, valid_channel_id
from src.data_store import data_store
from src.user import stat_update, global_stat_update

def dm_create_v1(token, u_ids):
	'''
	Creates a new DM, owned by the authorised user and including the members referenced
	in u_ids.

	Arguments:
		token (string) 		- token of the user creating the dm
		u_ids (int list)	- ids of the users to add to the dm

	Exceptions:
		InputError  - Occurs when:
			> Any of the u_ids are invalid
		AccessError - Occurs when:
			> Token is invalid

	Return Value:
		Returns a dictionary containing the dm_id
	'''

	if not valid_token(token):
		raise AccessError(description='Invalid token')

	if any(not valid_user_id(u_id) for u_id in u_ids):
		raise InputError(description='One (or more) u_id is invalid')
	
	u_id = token_user(token)
	members = [u_id] + u_ids

	# Update statistics
	for individual in members:
		stat_update(individual, 'dms_joined', 1)
	global_stat_update('dms_exist', 1)

	store = data_store.get()

	# Create dm_id
	dm_id = len(store['dms'])

	# Create name
	handles = sorted([store['users'][u]['handle_str'] for u in members])
	name = ', '.join(handles)

	# Notify the users that they've been added
	owner_handle = store['users'][u_id]['handle_str']
	for user in u_ids:
		send_notification(user, f"{owner_handle} added you to {name}", dm=dm_id)

	dm_details = {
		'dm_id': dm_id,
		'name': name,
		'owner_members': [u_id],
		'all_members': members,
		'messages': []
	}
	
	store['dms'].append(dm_details)
	
	# Apply changes
	data_store.set(store)

	return {
		'dm_id': dm_id,
	}


def dm_details_v1(token, dm_id):
	store = data_store.get()

	if not valid_token(token):
		raise AccessError('Invalid token')

	if not valid_dm_id(dm_id):
		raise InputError('dm_id does not refer to a valid DM.')

	u_id = token_user(token)

	dm = store['dms'][dm_id]
	if u_id not in dm['all_members']:
		raise AccessError('dm_id is valid, but the authorised user is not a member of the DM.')

	return {
		'name': dm['name'],
		'members': [get_user_details(member) for member in dm['all_members']],
	}


def dm_messages_v1(token, dm_id, start):
	store = data_store.get()

	if not valid_token(token):
		raise AccessError('Invalid token')

	if not valid_dm_id(dm_id):
		raise InputError('dm_id does not refer to a valid DM.')

	u_id = token_user(token)

	dm = store['dms'][dm_id]
	if u_id not in dm['all_members']:
		raise AccessError('dm_id is valid, but the authorised user is not a member of the DM.')

	if start > len(dm['messages']) or start < 0:
		raise InputError('start is greater than the total number of messages in the channel.')

	messages = store['dms'][dm_id]['messages']
	messages = list(map(lambda m: message_with_user_react(m, u_id), messages))

	return {
		'messages': messages[start: start +  50],
		'start': start,
		'end': -1 if start + 50 >= len(dm['messages']) else start + 50
	}

def dm_leave_v1(token, dm_id):
	store = data_store.get()

	if not valid_token(token):
		raise AccessError('Invalid token')

	if not valid_dm_id(dm_id):
		raise InputError('dm_id does not refer to a valid DM.')

	u_id = token_user(token)

	dm = store['dms'][dm_id]
	if u_id not in dm['all_members']:
		raise AccessError('dm_id is valid, but the authorised user is not a member of the DM.')

	# Update statistics
	stat_update(u_id, 'dms_joined', -1)

	if u_id in dm['owner_members']:
		dm['owner_members'].remove(u_id)
	dm['all_members'].remove(u_id)

	data_store.set(store)

	return {}

def dm_list_v1(token):
	store = data_store.get()

	if not valid_token(token):
		raise AccessError(description='Invalid token')

	u_id = token_user(token)

	dms = list(filter(lambda dm: u_id in dm['all_members'], store['dms']))

	return {
		'dms': [{'dm_id': d['dm_id'], 'name': d['name']} for d in dms]
	}

def dm_remove_v1(token, dm_id):
	store = data_store.get()

	if not valid_token(token):
		raise AccessError('Invalid token')

	if not valid_dm_id(dm_id):
		raise InputError('dm_id does not refer to a valid DM.')

	u_id = token_user(token)

	if u_id not in store['dms'][dm_id]['owner_members']:
		raise AccessError('dm_id is valid, but the authorised user is not an owner of the DM.')

	# Update statistics
	for individual in store['dms'][dm_id]['all_members']:
		stat_update(individual, 'dms_joined', -1)
	global_stat_update('dms_exist', -1)

	# Set to an empty channel
	store['dms'][dm_id] = {
		'dm_id': None,
		'name': 'Deleted',
		'owner_members': [],
		'all_members': [],
		'messages': []
	}

	data_store.set(store)

	return {}
