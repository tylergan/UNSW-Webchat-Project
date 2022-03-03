Assumed name case doesn't matter: 'HAYDEN' is the same name as 'Hayden' and 'hayden'. This is because in handle creation, names are converted to all lowercase, and to reflect the real-world semantics of names.

Assumed that names should contain only alphanumeric characters, non-alphanumeric characters will be removed when registering. This is because the handle creation removes non-alphanumeric characters.

Assumed IDs for channels and users are unique, as they are used to differentiate users and channels which may otherwise have the same properties

Assumed that the return types of all functions matches the specifications during testing (e.g. assume that auth_login returns a dictionary with key auth_user_id and an integer value). This is because these formats are universal across different implementations.

Assumed that an input error should be thrown if channel_messages is called with a negative start value. This is because a negative number is not a valid index when the most recent message is given index 0.

Assumed that there are repeatable channel names as they are differentiated via their channel
ids.
