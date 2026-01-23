from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, Klem, SteerMotor, CurrentSteer, StateChange, MenjaUgao)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import sys

class threadtestSteering(ThreadWithStop):
    """This thread handles testSteering.
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
        self.running = False

        time.sleep(5)
        self.subscribe()
        # self.sendKlem()
        # self.sendSteer()
        super(threadtestSteering, self).__init__()

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.setKlemSender = messageHandlerSender(self.queuesList, Klem)
        self.setSteeringAngleSender = messageHandlerSender(self.queuesList, SteerMotor)

        self.KlemReceive = messageHandlerSubscriber(self.queuesList, Klem, "lastOnly", True)
        self.SteeringAngle = messageHandlerSubscriber(self.queuesList, CurrentSteer, "lastOnly", True)
        self.DrivingMode = messageHandlerSubscriber(self.queuesList, StateChange, "lastOnly", True)
        self.ReceiveSteeringAngle = messageHandlerSubscriber(self.queuesList, MenjaUgao, "lastOnly", True)

    def state_change_handler(self):
        pass

    def thread_work(self):
        if self.test == 0:
            self.test += 1
            print("RADI THREAD")

        rec = self.KlemReceive.receive()
        if rec is not None:
            print(rec)

        rec = self.SteeringAngle.receive()
        if rec is not None:
            print(rec)

        rec = self.ReceiveSteeringAngle.receive()
        if rec is not None:
            self.sendSteer(rec)

        rec = self.DrivingMode.receive()
        if rec is not None:
            print(rec)
            if rec == "AUTO":
                self.sendKlem(30)
            elif rec == "STOP":
                self.sendKlem(0)
            else:
                self.sendKlem(0)

    def sendKlem(self, klMode):
        print("Valjda sam poslao klem")
        self.setKlemSender.send(str(klMode))

    def sendSteer(self, angle):
        print("Valjda sam poslao ugao")
        self.setSteeringAngleSender.send(str(angle))