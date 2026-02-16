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


class engine:
    def __init__(self, queuesList):

        self.queuesList = queuesList

        self.currentSpeed = 0
        self.speed = 0

        self.currentSteering = 0
        self.steering = 0

        self.currentState = None

        self.subscribe()
        self.subscribe_senders()

    def subscribe(self):
        self.stateMessage = messageHandlerSubscriber(self.queuesList, StateChange, 'lastOnly', True)

        self.signReceiver = messageHandlerSubscriber(self.queuesList, signDetection, "lastOnly", True)
        self.laneReceiver = messageHandlerSubscriber(self.queuesList, laneDetection, "lastOnly", True)

        self.angleCVReceiver = messageHandlerSubscriber(self.queuesList, CalculatedAngle, "lastOnly", True)

    def subscribe_senders(self):
        self.klemSender = messageHandlerSender(self.queuesList, Klem)
        self.speedSender = messageHandlerSender(self.queuesList, SpeedMotor)
        
    def update(self):
        recv = self.stateMessage.receive()
        if recv is not None:
            self.currentState = recv

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
            self.angleCV = recv
        else:
            self.angleCV = None

    def sendMessage(self, msgID, msg):
        if msgID == Klem:
            self.klemSender.send(msg)
        elif msgID == SpeedMotor:
            self.speedSender.send(msg)
        else:
            print("WRONG MESSAGE ID !")

    def getState(self):
        return self.currentState
    
    def getLane(self):
        return self.currentLane
    
    def getSign(self):
        return self.currentSign
    
    def getAngleCV(self):
        return self.angleCV