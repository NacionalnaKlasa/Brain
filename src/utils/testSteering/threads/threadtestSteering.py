from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (Klem, SteerMotor, CurrentSteer, StateChange, CalculatedAngle, SpeedMotor, CurrentSpeed)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

from libraries.udp_broadcast.udp.types import DATA_TYPES
from libraries.udp_broadcast.udp.udp_receiver import UDP_Receiver

import time

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

        time.sleep(5)
        self._init_subscribes()
        self._init_senders()
        self.udp = UDP_Receiver(port=9999)
        print("INITIALIZING TEST STEERING")
        super(threadtestSteering, self).__init__()

    def _init_subscribes(self):
        """Subscribes to recive the messages you are interested in."""
        self.KlemReceive = messageHandlerSubscriber(self.queuesList, Klem, "lastOnly", True)
        self.currentSteeringAngle = messageHandlerSubscriber(self.queuesList, CurrentSteer, "lastOnly", True)
        self.DrivingMode = messageHandlerSubscriber(self.queuesList, StateChange, "lastOnly", True)
        self.calculatedSteeringAngle = messageHandlerSubscriber(self.queuesList, CalculatedAngle, "lastOnly", True)
        self.SpeedMotorReceive = messageHandlerSubscriber(self.queuesList, CurrentSpeed, "lastOnly", True)
    
    def _init_senders(self):
        """Subscribes to send the messages you are interested in."""
        self.setKlemSender = messageHandlerSender(self.queuesList, Klem)
        self.setSteeringAngleSender = messageHandlerSender(self.queuesList, SteerMotor)

    def state_change_handler(self):
        pass

    def thread_work(self):
        data, data_type = self.udp.recv()
        if data is not None and data_type is not None:
            print(f"Data type: {data_type}\nData: {data}\n")
            
            if data_type == DATA_TYPES.STRING:
                parts = data.split(":")
                
                if len(parts) == 2:
                    print(data)
                    if parts[0] == "kl":
                        self.sendKlem(parts[1])
                        
                    elif parts[0] == "angle":
                        self.sendSteer(parts[1])
            
        time.sleep(0.005)

    def sendKlem(self, klMode):
        self.setKlemSender.send(str(klMode))

    def sendSteer(self, angle):
        self.setSteeringAngleSender.send(str(angle))