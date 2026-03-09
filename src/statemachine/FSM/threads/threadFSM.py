from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, MyStateChange)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender
from src.utils.messages.allMessages import SpeedMotor, SteerMotor, Brake, Klem, DrivingMode

from src.statemachine.FSM.src.callback.config import FORBIDEN_STATES

import time

# FSM
from src.statemachine.FSM.src.callback.config import *
from src.statemachine.FSM.src.states import States
from src.statemachine.FSM.src.transition import transition_table, callback_table

from src.statemachine.FSM.src.engine import engine

class threadFSM(ThreadWithStop):
    """This thread handles FSM.
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

        self.subscribe()
        super(threadFSM, self).__init__()

        self.engine = engine(queueList)
        self._lastHeartbeat = 0
        self._Heartbeat = 500
    
    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.stateSender = messageHandlerSender(self.queuesList, MyStateChange)

    def state_change_handler(self):
        pass

    def thread_work(self):
        self._lastHeartbeat += 1
        if self._lastHeartbeat > self._Heartbeat:
            self.stateSender.send(str(self.engine.getState()))
            self._lastHeartbeat = 0
        
        self.engine.update()
        state = self.engine.getState()
        stateBFMC = self.engine.getBFMCState()
        if stateBFMC == "AUTO" and state == States.IDLE:
            #self.engine.setState(States.TRAFIC_LIGHT)
            # self.engine.setState(States.INTERSECTION)
            # params = {FORBIDEN_STATES:[States.PARKING]}
            self.engine.setState(States.FOLLOW_LINE) 
            # self.engine.setState(States.PARKING)        
            
        elif stateBFMC == "STOP" and state != States.IDLE:
            # self.engine.sendMessage(Klem, str(0))
            self.engine.highway = 0
            self.engine.counter = 0
            self.engine.klemSender.send("0")
            self.engine.setState(States.IDLE)
            
        if state != self.engine.getPreviousState():
            enterTick = callback_table[state][CALLBACK_ENTER]
            enterTick(self.engine)

        tick = callback_table[state][CALLBACK_EXECUTE]
        tick(self.engine)
        self.engine.tick()



        
        

        

