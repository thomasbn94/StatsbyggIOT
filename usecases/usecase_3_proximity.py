''' Implements use-case no. 3.  This use-case is about checking whether a door (proximity sensor)
    is opened (changes state to NOT_PRESENT) outside scheduled opening hours.

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
import datetime
import os


class usecase_3_proximity(object):
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

        allowed_days, allowed_hours = self.load_other_config_parameters()
        self.surveil_door_state(allowed_days, allowed_hours)

        producer_thread.join()
        
    ''' Surveils door state. When opened, checks current time against scheduled opening hours'''
    def surveil_door_state(self, allowed_days, allowed_hours):

        while True:
            data_point = None
            try:
                data_point = self.queue.get()

                #Get current state and timestamp from queue
                state = data_point['result']['event']['data']['objectPresent']['state']
                time_of_state_change = data_point['result']['event']['data']['objectPresent']['updateTime']
                #Remove superfluous data from time string and parse to datetime
                time_of_state_change = datetime.datetime.strptime(time_of_state_change[:10] + " " + time_of_state_change[11:26], "%Y-%m-%d %H:%M:%S.%f")

                if state == "PRESENT":
                    print("Door closed at %s" % (time_of_state_change))
                elif state == "NOT_PRESENT":
                    print("Door opened at %s" % (time_of_state_change))
                    self.check_if_within_scheduled_hours(time_of_state_change, allowed_days, allowed_hours)

            except queue.Queue.Empty as e:
                print("Queue is empty...")

            ''' Break out of loop upon interrupt signal'''
            if self.interrupted == True:
                self.thread_kill = True
                break

    ''' Check if current time is a weekday or inside scheduled opening hours '''
    def check_if_within_scheduled_hours(self, time_of_state_change, allowed_days, allowed_hours):
        hour_open = allowed_hours['open']
        hour_close = allowed_hours['close']
        #Check if current time is a weekday or inside scheduled opening hours
        if  not time_of_state_change.isoweekday() in allowed_days \
            or (time_of_state_change.hour < hour_open) \
            or (time_of_state_change.hour >= hour_close):
            print("Warning! Door is open outside scheduled hours.\nScheduled opening hours are %s to %s" % (hour_open, hour_close))
        

    ''' Loads scheduled opening hours from config file '''
    def load_other_config_parameters(self):
        try:
            json_config_file = open(os.path.dirname(__file__) + '\\configuration\\usecase_3_proximity_configuration.json', 'r')
            allowed_days = json.loads(json_config_file.read())["allowed_time_interval"]['days']
            json_config_file.close()
            json_config_file = open(os.path.dirname(__file__) + '\\configuration\\usecase_3_proximity_configuration.json', 'r')
            allowed_hours = json.loads(json_config_file.read())["allowed_time_interval"]['hours']
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)
        return allowed_days, allowed_hours

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
            json_config_file = open(os.path.dirname(__file__) + '\\configuration\\usecase_3_proximity_configuration.json', 'r')
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
    uc_1 = usecase_3_proximity()
