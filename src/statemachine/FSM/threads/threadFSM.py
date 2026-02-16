from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender


# BFMC statemachine 
from src.utils.messages.allMessages import StateChange

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
        self.subscribe()
        super(threadFSM, self).__init__()

        self.currentStateAuto = None
        self.previousState = None
        self.currentState = States.IDLE

        self.engine = engine(queueList)

    def subscribe(self):
        """Subscribes to the messages you are interested in"""

    def state_change_handler(self):
        pass

    def thread_work(self):
        self.engine.update()
        state = self.engine.getState()
        if state is not None:
            if state == "AUTO" and self.currentState == States.IDLE:
                self.currentState = States.FOLLOW_LINE
            elif state == "STOP":
                self.currentState = States.IDLE

        if self.currentState != self.previousState:
            enterTick = callback_table[self.currentState][CALLBACK_ENTER]
            enterTick(self.engine)

        tick = callback_table[self.currentState][CALLBACK_EXECUTE]
        nextState = tick(self.engine)

        self.previousState = self.currentState
        if nextState is not None:
            self.currentState = nextState



        
        

        

