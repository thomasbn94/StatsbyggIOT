''' Fetch historical data in the interval specified in 'sensors.json'.
'''

import requests
import json
import credentials
import sys
import os


class Fetch_data(object):
    def __init__(self):

        # Get JSON configuration
        self.json_config = self.get_configurations()
        self.run()


    def run(self):
        device_list = self.json_config['device_ids']

        for device_id in device_list:
            file_name = "big queries/insert " + self.json_config['sensors'][device_id] + " into db.sql"
            file = open(file_name, "w")

            http_parameters = {
                "event_types": "temperature",
                "start_time": self.json_config['start_time'],
                "project": self.json_config['project_id'],
                "page_token": self.json_config['page_token'],
                "device": device_id
            }

            sensor_data = self.get_sensor_data_batch(http_parameters, device_id)
            self.generate_query(sensor_data, file)
            file.close()            

            print("Generated " + file_name)
        
        print("Done. Check \'big queries\' folder")

    ''' Print SQL query to 'file '''
    def generate_query(self, sensor_data, file):
        file.write("Insert into SB_temperature_events values\n")
        i = 0

        for element in sensor_data['events']:
            event_id = element['eventId']
            device_id = element['targetName'].split("/devices/")[1]
            sensor_name = self.json_config['sensors'][device_id]
            temperature = element['data']['temperature']['value']
            datestamp =  element['timestamp']

            if len(sensor_data['events']) - 1 == i:
                file.write("(\'" + event_id + "\' , \'" + sensor_name + "\', " + str(temperature) + ", \'" + datestamp + "\');")
            else:
                file.write("(\'" + event_id + "\' , \'" + sensor_name + "\', " + str(temperature) + ", \'" + datestamp + "\'),\n")

            i += 1


    ''' Returns a batch of sensor from HTTP response '''
    def get_sensor_data_batch(self, params, device):
        username = credentials.DT_USERNAME  # this is the key
        password = credentials.DT_PASSWORD # this is the secret. FROM CREATING SERVICE ACCOUNT
        projectId = credentials.PROJECT_ID
        apiUrlBase = "https://api.disruptive-technologies.com/v2"
        api_url = "{}/projects/{}/devices/{}/events".format(apiUrlBase, projectId, device)

        try:
            response = requests.get(api_url, 
                auth=(username, password), 
                headers={'accept':'application/json'}, 
                params=params
            )
        except requests.exceptions.ConnectionError as e:
            print(e)
        except requests.exceptions.Timeout as e:
            print(e)
        
        return json.loads(response.content)


    ''' Returns the HTTP parameters used in streaming '''
    def get_configurations(self):
        # Load sensor data as HTTP parameters
        try:
            json_config_file = open('data_fetch_config.json', 'r')
            json_object = json.loads(json_config_file.read())
            json_config_file.close()
        except IOError:
            print("Could not read or open config file. Exiting...")
            sys.exit(1)
        
        return json_object
        
        return 2
    

if __name__ == '__main__':
    fd = Fetch_data()