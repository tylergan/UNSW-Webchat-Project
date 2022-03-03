from src.error import AccessError
from src.validation import *
from src.data_store import data_store

def notifications_get_v1(token):
	'''
    Provides the 20 most recent notifications of the user.

    Arguments:
        token (str)  - token of the user requesting notifications

    Exceptions:
        AccessError  - Occurs when:
            > token is invalid

    Return Value:
        Returns a dictionary containing the list of the 20 most recent notifications
		(most recent in index 0)
    '''
	if not valid_token(token):
		raise AccessError(description="Invalid token")

	u_id = token_user(token)
	store = data_store.get()

	return {'notifications': store['users'][u_id]['notifications'][:20]}

def send_notification(user, text, channel=-1, dm=-1):
	print(f"notification sent to {user}: {text}")
	store = data_store.get()
	notification = {
		'channel_id': channel, 
		'dm_id': dm,
		'notification_message': text
	}
	store['users'][user]['notifications'].insert(0, notification)
	data_store.set(store)