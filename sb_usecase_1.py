''' Implements use-case no. 1. The use-case is about keeping track of 
    which doors are open at a given time. In particular, we want to alert end-users if 
    certain doors or windows are open when they shouldn't be. 
'''

import multiprocessing
import signal
from threading import Thread
from sb_process import SB_Process
from sb_sseStream import SB_SSEClient
import requests
import json
import pprint
import sseclient
import credentials
import sys
import threading
import queue

class SB_Usecase_No1(object):
    def __init__(self):

        ''' For this use-case, all we want is to read the temperature '''
        self.sensor_filter = {
            "device_types": "temperature",
            "event_types": "temperature",
            "kit": "think-evening-finish"
        }

        self.run()


    def run(self):
        print("Here I am: use-case no. 1")

        ''' Open up a connection and stream data from a DT cloud '''
        sse_client = SB_SSEClient()
        response = sse_client.getResponse(self.sensor_filter)
        client = sseclient.SSEClient(response)
        
        ''' Producer thread. Stream data and insert into queue '''
        producer_thread = threading.Thread(target=self.stream_data, args=(client, ))
        producer_thread.start()
        producer_thread.join()

        '''
        data_point = None
        return
        while True:
            try:
                data_point = data_queue.get()
                print(data_point)
            except queue.Queue.Empty as e:
                    print("Queue is empty...")
        '''

    def stream_data(self, client):
        print("Hola")
        while True:
            for event in client.events():
                #pprint.pprint(json.loads(event.data))
                try:
                    #self.data_queue.put(json.loads(event.data))
                    pprint.pprint(json.loads(event.data))
                except queue.Queue.Full as e:
                    print("Queue is full. Dropping events...")
                    continue


if __name__ == '__main__':
    uc_1 = SB_Usecase_No1()