from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (Klem, SteerMotor, CurrentSteer, StateChange, CalculatedAngle, SpeedMotor, CurrentSpeed)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

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

        self.angle = 0
        self.new_angle = 0

        self.speed = 0
        self.new_speed = 0

        self.autoSpeed = 260
        self.running = False

        time.sleep(5)
        self._init_subscribes()
        self._init_senders()
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
        self.SpeedMotorSend = messageHandlerSender(self.queuesList, SpeedMotor)
        pass

    def state_change_handler(self):
        pass

    def thread_work(self):
        # Reading Klem from nucleo
        rec = self.KlemReceive.receive()
        if rec is not None:
            print("Current klem from nucleo: ", rec)

        # Reading Angle from nucleo
        rec = self.currentSteeringAngle.receive()
        if rec is not None:
            print("Current angle from nucleo: ", rec)

        # Reading Speed from nucleo
        rec = self.SpeedMotorReceive.receive()
        if rec is not None:
            print("Current speed from nucleo: ", rec)
            self.speed = int(rec)

        # Receiving calculated angle from computer vision
        rec = self.calculatedSteeringAngle.receive()
        if rec is not None:
            if self.running:
                self.new_angle = int(rec)

        # Sending Angle and Speed on nucleo if runnig is enabled
        if self.running == True:
            if self.new_angle != self.angle:
                self.sendSteer(self.new_angle)
                self.angle = self.new_angle

            if self.speed != self.new_speed:
                self.sendSpeed(self.new_speed)

        # Reading MODE from Dashboard
        rec = self.DrivingMode.receive()
        if rec is not None:
            print(rec)
            if rec == "AUTO":
                self.sendKlem(30)
                self.running = True
                self.SpeedMotorSend.send(str(self.autoSpeed))
                self.new_speed = self.autoSpeed

            elif rec == "STOP":
                self.new_speed = 0
                self.sendKlem(0)
                self.running = False

    def sendKlem(self, klMode):
        # print("I guess I sent klem ", klMode)
        self.setKlemSender.send(str(klMode))

    def sendSteer(self, angle):
        # print("I guess I sent angle", angle)
        self.setSteeringAngleSender.send(str(angle))

    def sendSpeed(self, speed):
        # print("I guess I sent speed", speed)
        self.SpeedMotorSend.send(str(speed))