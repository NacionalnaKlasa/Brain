from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

# FROM DASHBOARD (ME)
from src.utils.messages.allMessages import SpeedMotor, SteerMotor, Brake, Klem, DrivingMode

# FROM NUCLEO
from src.utils.messages.allMessages import CurrentSpeed, CurrentSteer

# FROM BFMC statemachine
from src.utils.messages.allMessages import StateChange

# FROM MY CODE
from src.utils.messages.allMessages import signDetection, laneDetection, CalculatedAngle
from src.statemachine.FSM.src.states import States

import time


class engine:
    def __init__(self, queuesList):

        self.queuesList = queuesList        
        self.reset()
        self.sendAgainNucleo = 40

        self.subscribe()
        self.subscribe_senders()

    def subscribe(self):
        self.stateMessage = messageHandlerSubscriber(self.queuesList, StateChange, 'lastOnly', True)
        self.klemReceiver = messageHandlerSubscriber(self.queuesList, Klem, "lastOnly", True)

        self.signReceiver = messageHandlerSubscriber(self.queuesList, signDetection, "lastOnly", True)
        self.laneReceiver = messageHandlerSubscriber(self.queuesList, laneDetection, "lastOnly", True)

        self.angleCVReceiver = messageHandlerSubscriber(self.queuesList, CalculatedAngle, "lastOnly", True)

        self.currentSpeedReceiver = messageHandlerSubscriber(self.queuesList, CurrentSpeed, "lastOnly", True)
        self.currentAngleReceiver = messageHandlerSubscriber(self.queuesList, CurrentSteer, "lastOnly", True)

    def subscribe_senders(self):
        self.klemSender = messageHandlerSender(self.queuesList, Klem)
        self.speedSender = messageHandlerSender(self.queuesList, SpeedMotor)
        self.angleSender = messageHandlerSender(self.queuesList, SteerMotor)
        
    def reset(self):
        self.BFMCState = "STOP"
        
        self.currentState = States.IDLE
        self.previousState = None
        self.lastState = None
        self.desiredState:States = States.IDLE

        self.currentKlem = 0
        self.desiredKlem = 0
        self.klemSendNucleo = 0
        
        self.currentSpeed = 0
        self.desiredSpeed = 0
        self.speedSendNucleo = 0
        
        self.currentAngle = 0
        self.desiredAngle = 0
        self.calculatedAngle = 0
        self.angleSendNucleo = 0
        
        self.currentSign = None
        self.lastSign = None
        
        self.currentLane = None
        self.lastLane = None

        self.stateParameters = {}
        self.counter = 0
        
        self.highway = 0
        
        
    def update(self):
        # print("update")
        recv = self.stateMessage.receive()
        if recv is not None:
            self.BFMCState = recv

        recv = self.klemReceiver.receive()
        if recv is not None:
            self.currentKlem = int(recv)

        recv = self.signReceiver.receive()
        if recv is not None:
            self.currentSign = recv
        else:
            self.currentSign = None

        recv = self.laneReceiver.receive()
        if recv is not None:
            self.currentLane = recv
        else:
            self.currentLane = None

        recv = self.angleCVReceiver.receive()
        if recv is not None:
            self.calculatedAngle = int(recv)
        else:
            self.calculatedAngle = None

        recv = self.currentSpeedReceiver.receive()
        if recv is not None:
            pass
            # print("Current speed is ", recv, time.monotonic_ns())
            self.currentSpeed = recv
            
        recv = self.currentAngleReceiver.receive()
        if recv is not None:
            # print("Current angle is ", recv, time.monotonic_ns())
            self.currentAngle = recv
            
    def tick(self):
        self.previousState = self.currentState
        if self.currentState != self.desiredState:
            self.currentState = self.desiredState
            
        if self.currentKlem != self.desiredKlem:
            if self.klemSendNucleo < self.sendAgainNucleo:
                self.klemSendNucleo += 1
            else:
                self.sendMessage(Klem, str(self.desiredKlem))
                self.klemSendNucleo = 0
        
        # print("Current speed: ", self.currentSpeed, "     Desired speed: ", self.desiredSpeed)
        if self.currentSpeed != self.desiredSpeed:
            if self.speedSendNucleo < self.sendAgainNucleo:
                self.speedSendNucleo += 1
            else:
                # print("trebalo bi da sam poslao brzinu", self.desiredSpeed, " ", self.currentSpeed)
                self.sendMessage(SpeedMotor, str(self.desiredSpeed))
                self.speedSendNucleo = 0
        
        # print("Current angle: ", self.currentAngle, ", desired angle: ", self.desiredAngle)
        if self.currentAngle != self.desiredAngle:
            if self.angleSendNucleo < self.sendAgainNucleo:
                # print("povecaj counter")
                self.angleSendNucleo += 1
            else:
                # print("posalji ugao engine ?", self.desiredAngle)
                self.sendMessage(SteerMotor, str(self.desiredAngle))
                self.angleSendNucleo = 0

    def sendMessage(self, msgID, msg):
        if self.BFMCState == "AUTO" and self.BFMCState != "STOP":
            if msgID == Klem:
                self.klemSender.send(msg)
            elif msgID == SpeedMotor:
                self.speedSender.send(msg)
                # print("poslao brzinu", msg, time.monotonic_ns())
            elif msgID == SteerMotor:
                self.angleSender.send(msg)
                # print("poslao ugao", msg, time.monotonic_ns())
            else:
                print("WRONG MESSAGE ID !")
            
    def getBFMCState(self):
        return self.BFMCState

    def getState(self):
        return self.currentState
    
    def setState(self, state:States, params:dict = None):
        self.desiredState = state

        self.stateParameters.clear()
        if params is not None:
            self.stateParameters.update(params)
        
    def getPreviousState(self):
        return self.previousState
    
    def getStateParameters(self, key: str):
        return self.stateParameters.get(key)
    
    def getCurrentKlem(self):
        return self.currentKlem
    
    def setKlem(self, klem):
        self.desiredKlem = klem
        self.klemSendNucleo = self.sendAgainNucleo
    
    def getLane(self):
        return self.currentLane
    
    def getSign(self):
        return self.currentSign
    
    def getAngle(self):
        return self.currentAngle
    
    def getCalculatedAngle(self):
        return self.calculatedAngle
    
    def setAngle(self, angle):
        # print("primio sam ugao u engine ???")
        self.desiredAngle = angle

    def getSpeed(self):
        return self.currentSpeed
    
    def setSpeed(self, speed):
        self.desiredSpeed = speed
        
    def setLastSign(self, sign):
        self.lastSign = sign
        
    def getLastSign(self):
        return self.lastSign