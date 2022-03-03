from src.error import AccessError, InputError
from src.data_store import data_store
from src.validation import *
from src.user import stat_update, global_stat_update
from src.notifications import send_notification

def channel_invite_v1(token, channel_id, u_id):
    '''
    Adds the user given by u_id to a channel given by channel_id
    User is added to the channel immediately
    All channel members are able to invite other users

    Arguments:
        auth_user_id (int)	- id of the user inviting another user to a channel
        channel_id (int)	- id of the channel the user is being invited to
        u_id (int)			- id of the user being invited to the channel

    Exceptions:
        InputError  - Occurs when:
            > channel_id does not refer to an existing channel
            > u_id does not refer to an existing user
            > User with id u_id is already a member of the channel
        AccessError	- Occurs when:
            > channel_id is valid but auth_user_id is not a member
            > auth_user_id does not refer to an existing user

    Return Value:
        Returns an empty dictionary
    '''

    data = data_store.get()
    if not valid_token(token):
        raise AccessError(description='Invalid token')

    if not valid_user_id(u_id):
        raise InputError(description='Invited user does not exist')

    if not valid_channel_id(channel_id):
        raise InputError(description='Channel does not exist')

    auth_user_id = token_user(token)

    if not user_is_member(auth_user_id, channel_id):
        raise AccessError(description='Inviter is not a member of the channel')

    if user_is_member(u_id, channel_id):
        raise InputError(description='This user has already been added to the channel')

    # Update statistics
    stat_update(u_id, 'channels_joined', 1)

    # Notify the user that they've been added
    handle = data['users'][auth_user_id]['handle_str']
    ch_name = data['channels'][channel_id]['name']
    send_notification(u_id, f"{handle} added you to {ch_name}", channel=channel_id)

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel['all_members'].append(u_id)

    return {
    }


def channel_details_v1(token, channel_id):
    '''
    Provides details about a channel that the user is auth_user_id

    Arguments:
        auth_user_id (int)	- ID of the user making the request for channel details
        channel_id (int)	- ID of the channel to get the details of

    Exceptions:
        InputError  - Occurs when:
            > channel_id does not refer to an existing channel
        AccessError	- Occurs when:
            > channel_id is valid but the user auth_user_id is not a member
            > auth_user_id does not refer to a valid user

    Return Value:
        Returns a dictionary containing: {
            name:			name of the channel (string)
            is_public: 		true if the channel is public, false if private (bool)
            owner_members: 	a list of users who are owners of the channel (list)
            all_members: 	a list of users who are members of the channel (list)
        }
        The member lists are lists of dictionaries containing: {
            u_id:			id of the user (int)
            email:			email address of the user (string)
            name_first:		first name of the user (string)
            last_first:		last name of the user (string)
            handle_str:		the user's unique handle (string)
        }
    '''

    # Check if channel is valid
    if not valid_channel_id(channel_id):
        raise InputError(description="Channel does not exist")

    # Check if user is valid
    if not valid_token(token):
        raise AccessError(description="User ID does not belong to a user")

    auth_user_id = token_user(token)

    # Check if user is in the channel
    if not user_is_member(auth_user_id, channel_id):
        raise AccessError(description="User is not a member of the channel")	


    # Implement the function
    owners = []
    members = []
    channel_details = {}
    store = data_store.get()
    channels = store['channels']

    for channel in channels:

        # Find the channel_id in data_store
        if channel_id == channel['channel_id']:
            channel_name = channel.get('name')
            status = channel['is_public']

            # Add all members in channel list of all_members[] dictionary to members[] list
            # Use get_user_details function to get user's details 
            # from the data store.
            for user_member in channel['all_members']:
                temp_member = get_user_details(user_member)
                members.append(temp_member)

            # Add all owners in channel list of owner_member dictionary to owners[] list
            for user_owner in channel['owner_members']:
                temp_owner = get_user_details(user_owner)
                owners.append(temp_owner)

    channel_details = {
        'name': channel_name,
        'is_public': status,
        'owner_members': owners,
        'all_members': members,
    }

    return channel_details 



def channel_messages_v1(token, channel_id, start):
	'''
	Returns a page of messages from the channel matching channel_id.
	Returns up to 50 messages, starting from index 'start' (where 0
	is the most recent message sent to the channel).

	Arguments:
		auth_user_id (integer)	- id of the user making the request
		channel_id (integer)	- id of the channel to retrieve messages from
		start (integer)			- index of the first message to retrieve

	Exceptions:
		InputError  - Occurs when:
			> The channel does not exist
			> Start is greater than the number of messages in the channel
		AcessError	- Occurs when:
			> auth_user_id does not belong to a user
			> User is not a member of the channel

	Return Value:
		Returns a dictionary containing 'messages' (a list of the up to 50 messages),
		'start', and 'end' (start + 50, or -1 if the last message of the channel has been
		retrieved)
	'''

	# Error cases
	if not valid_token(token):
		raise AccessError(description="User ID does not belong to a user")

	auth_user_id = token_user(token)

	if not valid_channel_id(channel_id):
		raise InputError(description="Channel does not exist")

	if not user_is_member(auth_user_id, channel_id):
		raise AccessError(description="User is not a member of the channel")
	
	store = data_store.get()

	# Get the list of messages, and for each add the user's react information
	messages = store['channels'][channel_id]['messages']
	messages = list(map(lambda m: message_with_user_react(m, auth_user_id), messages))


	if start > len(messages):
		raise InputError(description="Start must not be greater than the number of messages in the channel")

	if start < 0:
		raise InputError(description="Start must not be negative")
	
	# Get the up to 50 most recent messages from start
	page = messages[start : start + 50]

	# Get the index of the end of the page, or -1 if there are no messages after the page
	end = (start + 50) if (start + 50) < len(messages) else -1

	return {
		'messages': page,
		'start': start,
		'end': end,
	}

def channel_join_v1(token, channel_id):
    '''
    Adds a user to a given channel, provided they have the permissions to join it.

    Arguments:
        token (string) 					- token of the user joining the channel
        channel id (int) 				- id of the channel being joined

    Exceptions:
        InputError  - Occurs when:
            > Channel_id does not refer to a valid channel
            > The authorised user is already a member of the channel
        AccessError - Occurs when:
            > Auth_user_id does not belong to a user
            > Channel_id refers to a channel that is private and the authorised user\
            > is not already a channel member and is not a global owner

    Return Value:
        Returns an empty dictionary
    '''

    store = data_store.get()
    channels = store['channels']
    joining_user = {}
    joining_channel = {}

    # Find user dictionary with corresponding token, raise AccessError if it does not exist
    if not valid_token(token):
        raise AccessError(description="Token does not belong to a user")

    auth_user_id = token_user(token)

    joining_user = store['users'][auth_user_id]

    # Find channel dictionary with corresponding c_id, raise InputError if it does not exist
    for channel in channels:
        if channel['channel_id'] == channel_id:
            joining_channel = channel
            break
    if joining_channel == {}:
        raise InputError(description="Channel ID does not describe an existing channel")

    # Check whether user is already a member of the given channel, raise InputError if the case
    for member in joining_channel['all_members']:
        if member == auth_user_id:
            raise InputError(description="User is already a member of this channel")


    # Check if channel is private and user is not a global owner, raise AccessError if the case
    if not joining_channel['is_public'] and joining_user['global_permissions'] != 1:
        raise AccessError(description="User does not have permissions to join channel")

    # Update statistics
    stat_update(auth_user_id, 'channels_joined', 1)

    # Append user to the channel all_members list
    joining_channel['all_members'].append(joining_user['u_id'])

    data_store.set(store)
    
    return {}

def channel_leave_v1(token, channel_id):
    '''
    Remove self from a given channel. The user's messages should remain, along with the
    channel itself even if that user was the last channel owner.

    Arguments:
        token (string) 					- id of user making request
        channel id (int) 				- id of the channel user is ti be removed from

    Exceptions:
        InputError  - Occurs when:
            > channel_id does not refer to a valid channel
        AccessError  - Occurs when:
            > channel_id is valid and the user is not a member of the channel
            > the token is invalid

    Return value:
        Returns an empty dictionary
    '''

    # Check that arguments are valid
    if not valid_token(token):
        raise AccessError(description='Invalid token')

    if not valid_channel_id(channel_id):
        raise InputError(description='Invalid channel_id')

    caller_id = token_user(token)

    if not user_is_member(caller_id, channel_id):
        raise AccessError(description='User must be channel member to leave channel')

    # Update statistics
    stat_update(caller_id, 'channels_joined', -1)

    store = data_store.get()

    store['channels'][channel_id]['all_members'].remove(caller_id)

    if caller_id in store['channels'][channel_id]['owner_members']:
        store['channels'][channel_id]['owner_members'].remove(caller_id)

    # Apply changes made to the store
    data_store.set(store)

    return {}


def channel_addowner_v1(token, channel_id, u_id): 
    '''
    Make a user an owner of the channel

    Arguments:
        token (string) 					- id of user making request
        channel id (int) 				- id of the channel user is to be added as owner
        u_id (int)						- id of user being added as owner


    Exceptions:
        InputError  - Occurs when:
            > Channel_id does not refer to a valid channel
            > U_id does not refer to a valid user
            > U_id refers to a user who is not a member of the channel
            > U_id refers to a user who is already an owner of the channel
        AccessError - Occurs when:
            > Channel_id is valid and the authorised user does not have owner
            permissions in the channel

    Return Value:
        Returns an empty dictionary
    '''
    # Validating Input

    store = data_store.get()
    channels = store['channels']

    if not valid_token(token):
        raise AccessError(description="User ID does not belong to a user")
    
    if not valid_channel_id(channel_id):
        raise InputError(description="Channel doesn't exist")

    auth_user_id = token_user(token)

    if not user_is_member(auth_user_id, channel_id):
        raise AccessError(description="Authorising user is currently not a member of the channel")

    if not user_has_owner_perms(token_user(token), channel_id):
        raise AccessError(description="User is not authorised to add an owner")

    if not user_is_member(u_id, channel_id):
        raise InputError(description="User is currently not a member of the channel")
        

    # if not valid_user_id(u_id): This case is handled by user_is_member

    
    #If user is already an owner
    for owner in channels[channel_id]['owner_members']:
        if owner == u_id:
            raise InputError(description="User is already an owner of this channel")

    store['channels'][channel_id]['owner_members'].append(u_id)

    return {}

def channel_removeowner_v1(token, channel_id, u_id):

    '''
    Removes a user as an owner of the channel

    Arguments:
        token (string) 					- id of user making request
        channel id (int) 				- id of the channel user is to be removed as an owner
        u_id (int)						- id of user being removed as an owner


    Exceptions:
        InputError  - Occurs when:
            > Channel_id does not refer to a valid channel
            > U_id does not refer to a valid user
            > U_id refers to a user who is not a member of the channel
            > U_id refers to a user who is not an owner of the channel
            > U_id refers to user who is the only owner of the channel
        AccessError - Occurs when:
            > Channel_id is valid and the authorised user does not have owner
            permissions in the channel

    Return Value:
        Returns an empty dictionary
    '''
    # Validating Input

    store = data_store.get()
    channels = store['channels']
    
    if not valid_token(token):
        raise AccessError(description="User ID does not belong to a user")
    
    if not valid_channel_id(channel_id):
        raise InputError(description="Channel doesn't exist")
    
    if not valid_user_id(u_id):
        raise InputError('User cannot be removed as owner as they do not exist')
    
    # If the authorised user has owner permissions
    if not user_has_owner_perms(token_user(token), channel_id):
        raise AccessError(description="User is not authorised to remove an owner")
    
    # If user to be removed as an owner is currently not an owner of the channel
    owners = channels[channel_id]['owner_members']
    if u_id not in owners:
        raise InputError(description="User is not an owner to be removed")
    
    # If user to be removed is the only owner of the channel
    if len(channels[channel_id]['owner_members']) == 1 and u_id in channels[channel_id]['owner_members']:
        raise InputError(description="User is currently the only owner of the channel")
        
    store['channels'][channel_id]['owner_members'].remove(u_id)

    return {}
