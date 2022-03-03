from werkzeug.exceptions import default_exceptions
from src.error import AccessError, InputError
from src.validation import message_with_user_react, token_user, valid_token, user_is_member
from src.data_store import data_store

def search_v1(token, query_str):
	'''
	Searches for all messages containing query_str in channels that the authorised user is a member of.

	Arguments:
		token (string)		- token of the user performing a search
		query_str (string)	- substring to search for messages containing

	Exceptions:
		InputError - Occurs when:
			> query_str is not 1..1000 chars inclusive
		AccessError - Occers when:
			> Token is invalid

	Return Value:
		Returns a dictionary containing a list of matching messages
	'''

	if not valid_token(token):
		raise AccessError(description="Invalid token")

	if not 1 <= len(query_str) <= 1000:
		raise InputError(description="Query string must be 1..1000 characters")

	u_id = token_user(token)
	store = data_store.get()

	results = []

	# Populate results with messages matching the query from channels the user is in
	for ch in filter(lambda ch: user_is_member(u_id, ch['channel_id']), store['channels']):
		results += filter(lambda m: query_str in m['message'], ch['messages'])

	for dm in filter(lambda dm: user_is_member(u_id, dm['dm_id'], chat_type='dms'), store['dms']):
		results += filter(lambda m: query_str in m['message'], dm['messages'])
	
	# Update results to include user's react information
	results = list(map(lambda m: message_with_user_react(m, u_id), results))

	return {'messages': results}