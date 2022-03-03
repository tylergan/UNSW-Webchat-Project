from src.error import AccessError, InputError
from src.validation import email_is_valid, valid_token, token_user, valid_user_id, get_user_details
from src.data_store import data_store

def users_all_v1(token):
	'''
	Returns information about all users.

	Arguments:
		token (string)		- authorisation token of the user (session) requesting a user list

	Exceptions:
		AccessError - Occers when:
			> token is invalid

	Return Value:
		Returns a list of users containing 'u_id', 'email', 'name_first', 'name_last', 'handle_str', 'profile_img_url'
	'''
	if not valid_token(token):
		raise AccessError(description='Token is invalid')

	store = data_store.get()
	users = store['users']

	return {'users': [get_user_details(u['u_id']) for u in users if u['u_id'] != None]}

def users_stats_v1(token):
    '''
    Returns analytics about the utilisation of UNSW streams as a whole

    Arguments: 
        token (string)	- authorisation token of the user requesting the analytics

    Exceptions:
        AccessError - Occurs when:
            > token is invalid

    Return Value:
        Returns a workplace_stats dictionary containing 'channels_exist', 'dms_exist', 'messages_exist', 'utilisation_rate'
    '''

    if not valid_token(token):
        raise AccessError(description="Invalid token")

    store = data_store.get()
    stat_block = dict(store['workplace_stats'])

    numerator = 0
    for user in store['users']:
        if user['stats']['channels_joined'][-1]['num_channels_joined'] > 0 or user['stats']['dms_joined'][-1]['num_dms_joined'] > 0:
            numerator += 1

    denominator = len(store['users'])

    utilisation_rate = numerator/denominator

    stat_block['utilisation_rate'] = utilisation_rate

    return {
        'workplace_stats': stat_block
    }