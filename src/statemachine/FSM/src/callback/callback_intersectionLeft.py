import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

_startTime: int = 0
_stopAfter: int = 6.5e9
_stop: bool = False

_speed: int = 200 
_angle: int = -250

#####

# SHOULD GO TO NEXT STATE IN THE IF 
#           AND REMOVE "and not _stop" FROM IF CONDITION

#####

def Enter_intersectionLeft(engine: engine):
    global _startTime, _stop
    
    engine.setAngle(_angle)
    engine.setSpeed(_speed)
    _startTime = time.monotonic_ns()
    _stop = False
    
def Execute_intersectionLeft(engine: engine):
    global _startTime, _stopAfter, _stop
    
    if time.monotonic_ns() - _startTime > _stopAfter and not _stop:
        # engine.setState(States.FOLLOW_LINE)
        _stop = True
        engine.setAngle(0)
        engine.setSpeed(0)
        engine.setKlem(0)