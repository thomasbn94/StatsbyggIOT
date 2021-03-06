''' Implements use-case no. 2. This use-case send an alert if the
    specified object (a notebook) has been removed from its docking-station
    for longer than the allowed time (proximity sensor in the "NOT-PRESENT" state) 
'''

from threading import Thread
from lib.sb_sseStream import SB_SSEClient
import requests
import json
import pprint
import sseclient
import credentials
import sys
import threading
import queue
import signal
import time
import datetime
import os

class usecase_2_proximity(object):
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

        # Perform use-case logic
        self.surveil_sensorstate()
        producer_thread.join()

    ''' Monitors state of a proximity sensor '''
    def surveil_sensorstate(self):
        
        while True:
            data_point = None
            try:
                data_point = self.queue.get()

                #Get current state and timestamp from queue
                state = data_point['result']['event']['data']['objectPresent']['state']
                time_of_state_change = data_point['result']['event']['data']['objectPresent']['updateTime']

                #Remove superfluous data from time string and parse to datetime
                time_of_state_change = datetime.datetime.strptime(time_of_state_change[:10] + " " + time_of_state_change[11:26], "%Y-%m-%d %H:%M:%S.%f")

                max_duration = self.max_open_duration()
                if state == "PRESENT":
                    print("Notebook present at %s" % (time_of_state_change))
                elif state == "NOT_PRESENT":
                    timer = 0
                    print("Notebook removed at %s" % (time_of_state_change))
                    while state == "NOT_PRESENT" and self.queue.empty():
                        timer += 1

                        if timer > max_duration:
                            alert = "ALERT: Notebook gone since %s,\nalert issued at %s" %(time_of_state_change, datetime.datetime.utcnow())
                            self.print_alert(alert)
                            break

                        time.sleep(1)

            except queue.Queue.Empty as e:
                print("Queue is empty...")

            ''' Break out of loop upon interrupt signal '''
            if self.interrupted == True:
                self.thread_kill = True
                break

    ''' For future use (displaying alert externally) '''
    def print_alert(self, alert):
        print(alert)
        
    ''' Returns the max allowed duration for a sensor to remain open '''
    def max_open_duration(self):
        # Load duration limit for an open state from config file
        try:
            json_config_file = open(os.path.dirname(__file__) + '\\configuration\\usecase_2_proximity_configuration.json', 'r')
            max_open_duration = json.loads(json_config_file.read())["other_parameters"]["max_open_duration"]
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)
        
        return max_open_duration

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
            json_config_file = open(os.path.dirname(__file__) + '\\configuration\\usecase_2_proximity_configuration.json', 'r')
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
    uc_1 = usecase_2_proximity()