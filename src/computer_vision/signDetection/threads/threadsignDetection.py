from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time

class threadsignDetection(ThreadWithStop):
    """This thread handles signDetection.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging

        self.test = 0
        time.sleep(5)
        self.subscribe()
        super(threadsignDetection, self).__init__()

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        pass

    def state_change_handler(self):
        pass

    def thread_work(self):
        if self.test == 0:
            print("signDetection thread is running")
            self.test = 1

