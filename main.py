import requests
import json
import pprint
import sseclient
import credentials
import sys
from sb_usecase_1 import SB_Process_No1
import multiprocessing
import signal

''' Implements a sensor-streaming interface '''
class SB_Project(object):

    ''' Read credentials from file (DEVELOPMENT ONLY) '''
    def __init__(self):
        pass

    ''' Manages the processes that implement different use-cases '''
    def process_management(self):
        
        ''' List of processes to be spawned '''
        process_list = []

        ''' Insert processes to spawn here. When their classes are constructed,
            they start executing immediately. 
        '''
        process_list.append(SB_Process_No1()) # use-case no. 1

        ''' Wait for them to complete'''
        # Handle SIGINTs 
        for p in process_list:
            p.join()


    ''' Main method '''
    def main(self):

        ''' The queue shared by all processes '''
        self.process_management()
        



 
 

if __name__ == '__main__':
    ss = SB_Project()
    ss.main()