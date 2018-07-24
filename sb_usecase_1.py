''' Implements use-case no. 1. This use-case is about keeping track of 
    the temperature of the VR3 computer case. 
'''

from threading import Thread
from sb_sseStream import SB_SSEClient
import requests
import json
import pprint
import sseclient
import credentials
import sys
import threading
import queue
import signal


class SB_Usecase_No1(object):
    def __init__(self):

        # Get HTTP parameters 
        self.sensor_filter = self.get_HTTP_parameters()

        # Signal handler and booleans. Usd to kill parent and thread
        self.interrupted = False
        self.thread_kill = False
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Thread-safe FIFO queue
        self.queue = queue.Queue()
        self.run()


    def run(self):
        print("Here I am: use-case no. 1")

        # Open up a connection and stream data from a DT cloud
        sse_client = SB_SSEClient()
        response = sse_client.getResponse(self.sensor_filter)
        client = sseclient.SSEClient(response)
    
        # Producer thread. Stream data and insert into queue
        producer_thread = threading.Thread(target=self.stream_data, args=(client, ))
        producer_thread.start()

        #LOGIC GOES HERE

        producer_thread.join()
        


    ''' Listen for live sensor data and insert them into a FIFO queue '''
    def stream_data(self, client):
        print("Streaming live sensor data...")

        while True:
            for event in client.events():
                try:
                    self.queue.put(json.loads(event.data))
                except queue.Queue.Full as e:
                    print("Queue is full. Dropping events...")
                    continue

                ''' Make sure to break out of this infinite loop '''
                if self.thread_kill == True:
                    print("Thread killed")
                    return



    ''' Returns the HTTP parameters used in streaming '''
    def get_HTTP_parameters(self):
        # Load sensor data as HTTP parameters
        try:
            json_config_file = open('sb_usecase_1_configuration.json', 'r')
            http_parameters = json.loads(json_config_file.read())["http_parameters"]
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)

        return http_parameters




    
    ''' Signal handler '''
    def signal_handler(self, signal, frame):
        self.interrupted = True




if __name__ == '__main__':
    uc_1 = SB_Usecase_No1()