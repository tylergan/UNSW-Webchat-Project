import time
import pickle
from src.data_store import data_store
from src.message import (
    message_send_v1,
    message_senddm_v1
)

def interval_backup():
	store = data_store.get()
	print("Starting object:")
	print(store)
	while True:
		with open("data.p", "wb") as f:
			pickle.dump(data_store.get(), f)

		msg_queue = store['msg_queue']
		if len(msg_queue) == 0:
			continue
		
		first_msg = msg_queue[0]
		if int(time.time()) >= int(first_msg['time_sent']):
			print(first_msg)
			if first_msg['type'] == 'channels':
				message_send_v1(first_msg['token'], first_msg['channel_id'], first_msg['message'], message_id=first_msg['message_id'])
			else:
				message_senddm_v1(first_msg['token'], first_msg['dm_id'], first_msg['message'], message_id=first_msg['message_id'])
			msg_queue.pop(0)
			data_store.set(store)

