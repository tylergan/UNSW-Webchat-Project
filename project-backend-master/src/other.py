from src.data_store import data_store
import os
from shutil import rmtree

def clear_v1():
    '''
    Clears the data store to reset the state of the program

    No arguments
    No exceptions
    No return value
    '''

    store = data_store.get()
    store['users'] = []
    store['sessions'] = []
    store['channels'] = []
    store['dms'] = []
    store['passwords'] = []
    store['curr_channel_id'] = 0
    store['curr_session_id'] = 0
    store['message_info'] = {}
    store['workplace_stats'] = {}
    store['current_profile_img'] = 0
    store['user_sessions'] = []
    store['msg_queue'] = []
    data_store.set(store)

    images = 'profile_imgs'
    for filename in os.listdir(images):
        if filename == 'profile_img_default.jpg':
            continue
        file_path = os.path.join(images, filename)
        os.unlink(file_path)

    return {}