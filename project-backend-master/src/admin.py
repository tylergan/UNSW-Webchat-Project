from src.data_store import data_store
from src.error import AccessError, InputError
from src.validation import valid_token, valid_user_id, token_user 

def admin_userpermission_change_v1(token, u_id, permission_id):
	'''
	Given a valid owner token, updates a certain user's global permissions to those
	of an owner, or those of a member, as requested.

	Arguments:
		token (string) 		- token of the user requesting the change
		u_ids (int)	        - id of the user being affected
		permission_id (int) - global permission the user will be given

	Exceptions: 
		InputError - Occurs when:
			> u_id is invalid
			> permission_id is invalid
			> u_id refers to the only global owner who is being demoted
		AccessError - Occurs when:
			> token refers to a user who is not a global owner
			> token is invalid

	Return value:
		Returns an empty dictionary
	'''

	# Check that arguments are valid
	if not valid_token(token):
		raise AccessError(description='Invalid token')

	if not valid_user_id(u_id):
		raise InputError(description='Invalid u_id')

	if permission_id not in (1, 2):
		raise InputError(description='Invalid permission_id')
	
	caller_id = token_user(token)

	store = data_store.get()

	num_owners = 0
	for user in store['users']:
		# Count the number of owners
		if user['global_permissions'] == 1:
			num_owners += 1
		# Raise AccessError if the caller is found not to be a global owner
		elif user['u_id'] == caller_id:
			raise AccessError(description='Caller must be a global owner')

	for user in store['users']:
		if user['u_id'] == u_id:
			# Raise an InputError if the caller is the last global owner and attempts to
			# demote themselves
			if u_id == caller_id and num_owners < 2 and permission_id == 2:
				raise InputError(description='A solitary owner cannot demote themselves')
			else:
				user['global_permissions'] = permission_id

	# Apply changes made to the store
	data_store.set(store)

	return {}

def admin_user_remove_v1(token, u_id):
	'''
	Given a valid owner token, removes a user from streams. They should be removed from
	all channels and dms, while the content of their messages becomes 'Removed user'.
	Their email and handle should be reusable, however their profile should still be
	found by user/profile, although their first and last names should be changes to
	'Removed', 'user'.

	Arguments:
		token (string) 		- token of the user requesting the removal
		u_ids (int)	        - id of the user being removed

	Exceptions: 
		InputError - Occurs when:
			> u_id is invalid
			> u_id refers to the only global owner
		AccessError - Occurs when:
			> token refers to a user who is not a global owner
			> token is invalid

	Return value:
		Returns an empty dictionary
	'''

	# Check that arguments are valid
	if not valid_token(token):
		raise AccessError(description='Invalid token')

	if not valid_user_id(u_id):
		raise InputError(description='Invalid u_id')

	store = data_store.get()

	caller_id = token_user(token)

	# Count the number of owners, raise InputError if there are less than 2
	num_owners = 0
	for user in store['users']:
		if user['global_permissions'] == 1:
			num_owners += 1
		# Raise AccessError if the caller is found not to be a global owner
		elif user['u_id'] == caller_id:
			raise AccessError(description='Caller must be a global owner')
	if caller_id == u_id  and num_owners < 2:
		raise InputError(description='A solitary owner cannot remove themselves')

	# Loop through each channel and remove provided u_id from their member lists,
	# update messages with 'Removed user'.
	for channel in store['channels']:
		in_channel = False
		if u_id in channel['all_members']: # Remove u_id from members list
			in_channel = True
			channel['all_members'].remove(u_id)
		if u_id in channel['owner_members']: # Remove u_id from owners list
			channel['owner_members'].remove(u_id)
		if in_channel == True: 
			for message in channel['messages']: # Replace user's messages with 'Removed user' if user was in the channel
				if message['u_id'] == u_id:
					message['message'] = 'Removed user'

	# Identical block of code to the one above, with 'channel' replaced by 'dm':
	# Loop through each dm and remove provided u_id from their member lists,
	# update messages with 'Removed user'.
	for dm in store['dms']:
		in_dm = False
		if u_id in dm['all_members']: # Remove u_id from members list
			in_dm = True
			dm['all_members'].remove(u_id)
		if u_id in dm['owner_members']: # Remove u_id from owners list
			dm['owner_members'].remove(u_id)
		if in_dm == True: 
			for message in dm['messages']: # Replace user's messages with 'Removed user' if user was in the dm
				if message['u_id'] == u_id:
					message['message'] = 'Removed user'


	for user in store['users']:
		if user['u_id'] == u_id:
			user['email'] = ''
			user['handle_str'] = ''
			user['name_first'] = 'Removed'
			user['name_last'] = 'user'
			user['global_permissions'] = 3

	# Apply changes made to the store
	data_store.set(store)

	return {}