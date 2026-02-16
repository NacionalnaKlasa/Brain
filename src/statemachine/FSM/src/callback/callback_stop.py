import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

_startTime: int = 0
_stopTime: int = 3e9

def stateCallbackEnter_stop(engine: engine):
    global _startTime

    engine.sendMessage(Klem, "0")
    _startTime = time.monotonic_ns()
    
def stateCallback_stop(engine: engine):
    global _startTime, _stopTime

    nextState = None
    if time.monotonic_ns() - _startTime > _stopTime:
        nextState = States.FOLLOW_LINE

    return nextState