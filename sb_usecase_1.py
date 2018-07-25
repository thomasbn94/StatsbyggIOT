''' Implements use-case no. USE CASE NO. This use-case is about 
    DETAILS GO HERE. 

    REMEMBER TO FILL OUT AND CHANGE ACCORDING TO USE CASE

    REMEMBER TO CHANGE 1) CLASS NAME (AND MAIN FUNCTION), 2) .py FILE NAME, 
    3) CONFIGURATION FILE NAME AND 4) CONFIG FILE PATH ACCORDING TO USE CASE!!
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


class changeme_1_temperature(object):
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

        # Open up a connection and stream data from a DT cloud
        sse_client = SB_SSEClient()
        response = sse_client.getResponse(self.sensor_filter)
        client = sseclient.SSEClient(response)
    
        # Producer thread. Stream data and insert into queue
        producer_thread = threading.Thread(target=self.stream_data, args=(client, ))
        producer_thread.start()

        self.use_case_logic()

        producer_thread.join()
        
    ''' CHANGE NAME ACCORDING TO USE CASE'''
    def use_case_logic(self):

        while True:
            data_point = None
            try:
                data_point = self.queue.get()

                # Use case logic goes here

            except queue.Queue.Empty as e:
                print("Queue is empty...")

            ''' Break out of loop upon interrupt signal'''
            if self.interrupted == True:
                self.thread_kill = True
                break

    ''' Loads other_parameters from config file '''
    def load_other_config_parameters(self):
        try:
            #change
            json_config_file = open('CHANGE.ME.json', 'r')
            #change
            max_open_duration = json.loads(json_config_file.read())["other_parameters"]["CHANGE_ME"]
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)

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
            #change
            json_config_file = open('CHANGE.ME.json', 'r')
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
    uc_1 = changeme_1_temperature()