import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

from src.statemachine.FSM.src.states import States, OBJECT_CLASSES
from src.computer_vision.signDetection.threads.config import Types, OBJECT_TYPES
from .config import FORBIDEN_STATES

_startTime: int = 0
_stopTime: int = 3e9
nextState = None

def stateCallbackEnter_stop(engine: engine):
    global _startTime

    engine.setKlem(0)
    _startTime = time.monotonic_ns()
    
def stateCallback_stop(engine: engine):
    global _startTime, _stopTime, nextState
    
    sign = engine.getSign()
    if sign is not None:
        sign = sign.split()
        if sign[0] == OBJECT_CLASSES[States.STOP_LINE]:
            nextState = States.STOP_LINE
            
    if time.monotonic_ns() - _startTime > _stopTime:
        # engine.setLastSign("stop")
        params = {FORBIDEN_STATES: [States.STOP]}
        engine.setState(States.FOLLOW_LINE, params)