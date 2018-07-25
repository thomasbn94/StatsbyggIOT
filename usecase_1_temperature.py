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


class usecase_1_temperature(object):
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

        # Read the maximum temperature from the config file
        max_temp = self.get_max_temperature()

        # Perform use-case logic
        self.surveil_temperature(max_temp)
        producer_thread.join()
        

    ''' Checks temperature reading for illegal values '''
    def surveil_temperature(self, max_temp):

        ''' Use-case logic '''
        while True:
            data_point = None
            try:
                data_point = self.queue.get()
                sensor_temp = data_point['result']['event']['data']['temperature']['value']
                if sensor_temp > max_temp:
                    self.send_notification(max_temp, sensor_temp, data_point)

            except queue.Queue.Empty as e:
                print("Queue is empty...")

            ''' Break out of loop upon interrupt signal '''
            if self.interrupted == True:
                self.thread_kill = True
                break


    ''' Send a notification to notify an end-user '''
    def send_notification(self, expected_temperature, actual_temperature, json_config):
        timestamp = json_config['result']['event']['data']['temperature']['updateTime']
        print("Too high temperature. Should be", expected_temperature,". Was", actual_temperature," at", timestamp)



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


    ''' Returns the temperature used in this use-case '''
    def get_max_temperature(self):
        # Load temperature from config file
        try:
            json_config_file = open('usecase_1_temperature.json', 'r')
            max_temp = json.loads(json_config_file.read())["other_parameters"]["max_temperature"]
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)
        
        return max_temp



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
    uc_1 = usecase_1_temperature()
