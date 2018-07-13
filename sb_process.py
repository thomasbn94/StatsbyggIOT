import multiprocessing
import signal
from threading import Thread



class SB_Process(multiprocessing.Process):
    def __init__(self, work_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.work_queue = work_queue
        self.daemon = True
        self.start()


    def run(self):        
        print("Here I am: " + str(self.pid))

        while not self.exit.is_set():
            self.work_queue.get()
