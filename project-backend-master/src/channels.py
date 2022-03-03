from src.data_store import data_store
from src.error import InputError, AccessError
from src.validation import valid_user_id, valid_token, token_user
from src.user import stat_update, global_stat_update

def channels_list_v1(token):
    '''
    Provides the list of channels with associated details that an authorised user is part of.

    Arguments:
        auth_user_id (integer)  - id of a registered user

    Exceptions:
        AccessError  - Occurs when:
            > A user has not been registered and thus does not have a valid ID.

    Return Value:
        Returns a dictionary of a list of dictionaries containing 'channel_id'
        and channel 'name'.
    '''

    #check for valid user_id
    if not valid_token(token):
        raise AccessError(description="User ID does not exist")
    
    auth_user_id = token_user(token)

    #empty list for dictionary of channels
    list_channels = []

    #Loop through channel
    #Check if user is in channel, then append to channel list
    store = data_store.get()
    for channel in store['channels']:
        if auth_user_id in channel['all_members']:
            list_channels.append({
                'channel_id': channel['channel_id'],
                'name': channel['name'],
            })

    return {
        'channels': list_channels
    }


def channels_listall_v1(token):
    '''
    Provides a list of all existing channels

    Arguments:
        auth_user_id (integer)  - id of a registered user

    Exceptions:
        None

    Return Value:
        Returns a dictionary containing 'channels', with a list of channels
        Each channel in the list is a dictionary with keys 'channel_id' and 'name'
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid user token")


    channels = data_store.get()['channels']
    owners_channels = {
        'channels' : [{
            'channel_id': channel['channel_id'],
            'name': channel['name']
        } for channel in channels]
    }

    return owners_channels


def channels_create_v1(token, name, is_public):
    '''
    Creates and names a new channel that will be either public or private, automatically
    adding the user who created it as the owner.

    Arguments:
        token (string)          - token of a registered user
        name (string)           - name of the channel
        is_public (boolean)     - indicates if channel is public (True) or private (False)

    Exceptions:
        InputError  - Occurs when:
            > Channel name is not between 1 to 20 characters

        AccessError - Occurs when:
            > A user has not been registered and thus does not have a valid ID.

    Return Value:
        Returns a dictionary containing 'channel_id'
    '''

    store = data_store.get()
    channels = store['channels']

    #Check for valid user_id
    if not valid_token(token):
        raise AccessError(description="Token is invalid")

    u_id = token_user(token)

    #Check for valid channel name
    if not 1 <= len(name) <= 20:
        raise InputError(description='Invalid Channel Name. Name must be between 1 to 20 characters')

    # Update statistics
    stat_update(u_id, 'channels_joined', 1)
    global_stat_update('channels_exist', 1)
    
    # Create channel_id
    channel_id = len(channels)
    
    channels_details = {
        'channel_id': channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [u_id],
        'all_members': [u_id],
        'messages': [],
        'standup': {'is_active': False, 'time_finish': None, 'msg_queue': []}
    }
    
    store['channels'].append(channels_details)
    
    # Apply changes
    data_store.set(store)

    return {
        'channel_id': channel_id,
    }

