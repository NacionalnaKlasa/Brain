from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, CalculatedAngle)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time

class threadtestPosaljiUgao(ThreadWithStop):
    """This thread handles testPosaljiUgao.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging
        self.increment = 25
        self.ugao = 0
        time.sleep(5)
        self.subscribe()
        super(threadtestPosaljiUgao, self).__init__()

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.posaljiUgao = messageHandlerSender(self.queuesList, CalculatedAngle)

    def state_change_handler(self):
        pass

    def thread_work(self):
        self.posaljiUgao.send(str(self.ugao))
        if abs(self.ugao + self.increment) >= 250:
            self.increment = -self.increment
        self.ugao += self.increment
        time.sleep(1)

