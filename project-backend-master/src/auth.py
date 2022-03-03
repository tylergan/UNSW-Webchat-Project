import hashlib

import jwt
import src
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.data_store import data_store
from src.error import AccessError, InputError
from src.validation import valid_token, email_is_valid, reset_code_is_valid
from datetime import datetime, timezone
from src import config

SECRET = "irAh55GJ0H" # Ideally this would be an environment variable or similar

# Creates a JWT token for a user's session
def create_token(u_id):
	store = data_store.get()
	user_sessions = store['user_sessions']
	# Get the next sequential ID to use
	s_id = store['curr_session_id']

	store['sessions'].append(s_id)
	user_sessions = store['user_sessions']

	for user in user_sessions:
		if user['u_id'] == u_id:
			store['user_sessions'][u_id]['sessions'].append(s_id)
	else:
		user_session = {
			'u_id': u_id,
			'sessions': [s_id]
		}
		store['user_sessions'].append(user_session)

	# Increment sequential ID for next session to use
	store['curr_session_id'] += 1

	# Create the JSW token with the user ID and session ID
	token = jwt.encode({'u_id': u_id, 's_id': s_id}, SECRET, algorithm='HS256')

	data_store.set(store)
	return token

def auth_login_v1(email, password):
	'''
	Logs a user in by checking and identifying the given email and password combination.

	Arguments:
		email (string)		- email address of the user logging in
		password (string)	- logging in user's password

	Exceptions:
		InputError - Occurs when:
			> email entered does not belong to a user
			> password is not correct

	Return Value:
		Returns a dictionary containing 'auth_user_id'
	'''


	#Initialising lists
	email_registered = False
	user_list = data_store.get()['users']
	password_list = data_store.get()['passwords']

	#Loop through users to find one with matching email
	for user in user_list:
		if user['email'] == email:
			user_id = user['u_id']
			email_registered = True
			break

	#Raise InputError if no user if found with corresponding email
	if email_registered == False:
		raise InputError(description='No user is registered with this Email')
		
	#Raise InputError if password is incorrect
	hashed_pword = hashlib.sha256(password.encode()).hexdigest()

	if password_list[user_id] != hashed_pword:
		raise InputError(description='Incorrect Password')

	if user_list[user_id]['global_permissions'] == 3:
		raise InputError(description="User has been removed")

	return {
		'auth_user_id': user_id,
		'token': create_token(user_id),
	}

# Returns a copy of 'string' with all non-alphanumeric characters removed
def remove_non_alnum(string):
	result = ''
	for ch in string:
		if ch.isalnum():
			result += ch
	return result

# Generates a unique handle for a user by concatenating first and last names
# Number appended to end to differentiate users with the same name
# Handle contains only alphanumeric characters
# Handle is truncated to 20 name characters, exluding number for duplicate names
def create_handle(first, last):
	# Generate handle from first 20 alphanum characters
	store = data_store.get()
	users = store['users']
	base_handle = remove_non_alnum(first.lower() + last.lower())[:20]

	# If taken, append with a number
	occurrences = 0
	handle = base_handle
	for user in users:
		if user['handle_str'] == handle:
			handle = base_handle + f"{occurrences}"
			occurrences += 1
	
	
	return handle

# Returns true if email address has not yet been used by a registered user in the data store
def email_is_unique(email):
	store = data_store.get()
	users = store['users']

	for user in users:
		if user['email'] == email:
			return False

	return True


def auth_register_v1(email, password, name_first, name_last):
	'''
	Registers a user by adding them to the users list of the data store and assigning an ID

	Arguments:
		email (string)		- email address of the user being registered
		password (string)	- password of the user
		name_first (string)	- first name of the user
		name_last (string)	- last name of the user

	Exceptions:
		InputError  - Occurs when:
			> Email address has already been used by a registered user
			> Email does not match the format of a valid email address
			> First or last name is not between 1 and 50 characters long (inclusive)
			> Password is less than 6 characters long

	Return Value:
		Returns a dictionary containing 'auth_user_id' and 'token'
	'''
	# Normalise case of names
	name_first = name_first.lower()
	name_last = name_last.lower()

	# Check if email is valid
	if not email_is_unique(email):
		raise InputError(description='Email has already been used to register a user')
	
	if not email_is_valid(email):
		raise InputError(description='Email is invalid')

	# Check if names are valid
	if not 1 <= len(name_first) <= 50:
		raise InputError(description='First name must be between 1 and 50 characters')
	
	if not 1 <= len(name_last) <= 50:
		raise InputError(description='Last name must be between 1 and 50 characters')

	# Check if password is valid
	if len(password) < 6:
		raise InputError(description='Password must not be less than 6 characters')

	# Add to users list in data store
	store = data_store.get()
	users = store['users'] # List of users, index = id

	handle = create_handle(name_first, name_last)
	u_id = len(users)

	# User is global owner if joined first (if id is 0)
	perm_id = 1 if u_id == 0 else 2

	token = create_token(u_id)

	# Add new user statistics block
	time = int(datetime.now(timezone.utc).timestamp())
	stats = {
		'channels_joined': [{'num_channels_joined': 0, 'time_stamp': time}],
		'dms_joined': [{'num_dms_joined': 0, 'time_stamp': time}],
		'messages_sent': [{'num_messages_sent': 0, 'time_stamp': time}]
	}

	# Start statistics recording for the whole server when the first user joins
	if u_id == 0:
		time = int(datetime.now(timezone.utc).timestamp())
		store['workplace_stats'] = {
			'channels_exist': [{'num_channels_exist': 0, 'time_stamp': time}], 
			'dms_exist': [{'num_dms_exist': 0, 'time_stamp': time}], 
			'messages_exist': [{'num_messages_exist': 0, 'time_stamp': time}]
		}

	users.append({
		'u_id': u_id,
		'email': email,
		'name_first': name_first,
		'name_last': name_last,
		'handle_str': handle,
		'global_permissions': perm_id,
		'stats': stats,
		'reset_code': None,
		'profile_img_url': config.url + 'profile_imgs/profile_img_default.jpg',
		'notifications': []
	})

	# Add password to data store
	hashed_pword = hashlib.sha256(password.encode()).hexdigest()
	store['passwords'].append(hashed_pword)


	data_store.set(store)
	
	return {
		'auth_user_id': u_id,
		'token': token,
	}

def auth_logout_v1(token):
	'''
	Logs out a user by invalidating the token for their current session

	Arguments:
		token (string)		- JWT token of the user session to end


	Exceptions:
		AccessError  - Occurs when:
			> Token does not reference a valid session or valid auth_user_id
	Return Value:
		Returns an empty dictionary
	'''

	store = data_store.get()
	sessions = store['sessions']

	if not valid_token(token):
		raise AccessError(description='Invalid token')
	
	# Find the session ID associated with the token, and delete it
	s_id = jwt.decode(token, src.auth.SECRET, algorithms=['HS256'])['s_id']
	sessions.remove(s_id)

	data_store.set(store)
	
	return {}

def auth_passwordreset_request_v1(email):
	'''
	Given a registered user's email address, sends an email with a secret code
	used to verify them when changing passwords. They should also be
	logged out of all current sessions.

	Arguments:
		email (string)		- Email of a registered user

	Return Value:
		Returns an empty dictionary
	'''

	# Check if email given is valid
	if not email_is_valid(email):
		return {}

	store = data_store.get()
	users = store['users']
	sessions = store['sessions']
	user_sessions = store['user_sessions']

	# Generate a reset code using secrets module
	reset_code = secrets.token_hex(4)

	u_id = None

	# Store reset code and logout from all current sessions
	for user in users:
		if user['email'] == email:
			u_id = user['u_id']

	if u_id == None:
		return {}

	for s_id in user_sessions[u_id]['sessions']:
		if s_id in sessions:
			sessions.remove(s_id)
	
	users[u_id]['reset_code'] = reset_code
	user_sessions[u_id]['sessions'].clear()
	
	# Set up SMTP server and send email
	sender_email = 'dummyemail6767@gmail.com'
	receiver_email = email

	msg = MIMEMultipart()
	txt = MIMEText(reset_code, 'plain')
	msg['From'] = sender_email
	msg['To'] = email
	msg['Subject'] = 'Your Reset Code'
	msg.attach(txt)

	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.login("dummyemail6767@gmail.com", "Dummy123")
	server.sendmail(sender_email, receiver_email, msg.as_string())
	server.quit()

	data_store.set(store)
	return {}
	

def auth_passwordreset_reset_v1(reset_code, new_password):
	'''
    Change user password 

    Arguments:
        reset_code (int): Reset code that was sent to user's email
        new_password (str): New password 

    Exceptions:
		InputError > Occur when:
        	> Reset code is invalid
        	> New_password is less than 6 characters

    Return Value:
        Returns an empty dictionary
    '''

	if not reset_code_is_valid(reset_code):
		raise InputError(description='Invalid reset code')

	if len(new_password) < 6:
		raise InputError(description='Password entered is less than 6 characters long')

	store = data_store.get()
	users = store['users']

	for user in users:
		if user['reset_code'] == reset_code:
			u_id = user['u_id']
			break

	hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
	data_store.get()['passwords'][u_id] = hashed_password

	data_store.set(store)

	return {}

	



	





