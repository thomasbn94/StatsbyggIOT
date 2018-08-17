import requests
import json
import pprint
import sseclient
import credentials
import sys


class SB_SSEClient(object):

    ''' Read credentials from file (DEVELOPMENT ONLY) '''
    def __init__(self):
        self.username = credentials.DT_USERNAME  # this is the key
        self.password = credentials.DT_PASSWORD # this is the secret. FROM CREATING SERVICE ACCOUNT
        self.projectId = credentials.PROJECT_ID
        self.apiUrlBase = "https://api.disruptive-technologies.com/v2"


    ''' Streams live data from the cloud '''
    def getResponse(self, sensor_filter=None):
        #devices_list_url = "{}/projects/{}/devices".format(apiUrlBase, projectId)
        devices_stream_url = "{}/projects/{}/devices:stream".format(self.apiUrlBase, self.projectId)

        response = None
        max_retries = 10

        ''' Try at most max_retries times to connect to the cloud. 
            If all fails, exit the process
        '''
        for i in range(0, max_retries):

            ''' Catch any potential exceptions '''
            try:
                if sensor_filter != None:
                    #print("Filter supplied: " + sensor_filter)
                    response = requests.get(devices_stream_url, auth=(self.username, self.password), headers={'accept':'text/event-stream'}, stream=True, params=sensor_filter)
                else:
                    #print("filter not supplied")
                    response = requests.get(devices_stream_url, auth=(self.username, self.password), headers={'accept':'text/event-stream'}, stream=True)
            except requests.exceptions.ConnectionError as e:
                print(e)
            except requests.exceptions.Timeout as e:
                print(e)
            else:
                break
        
        else:
            print("Network connection seems to be broken. Exiting...")
            sys.exit(1)

        ''' Used for streaming from the cloud service elsewhere '''
        return response
        
