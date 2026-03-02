import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

_startTimeAAA = 0
_stopAfterStraight = 3.5e9
_stopAfterTurn = 4e9
_stop: bool = False

_speed: int = 200 
_angle: int = 170

_state: int = 0
setFirst = False

#####

# SHOULD GO TO NEXT STATE IN THE IF 
#           AND REMOVE "and not _stop" FROM IF CONDITION

#####

def Enter_intersectionRight(engine: engine):
    print("ENTER INTERSECTION RIGHT")
    global _startTimeAAA, _stop, _state, _speed, setFirst
    
    engine.setKlem(30)
    if engine.getAngle() != 0:
        engine.setAngle(5)
        
    if engine.getSpeed() != _speed:
        engine.setSpeed(_speed)
    
    _stop = False
    _state = 0
    setFirst = False
    
    
def Execute_intersectionRight(engine: engine):
    global _state
    
    if _state == 0:
        _firstMove(engine)
    elif _state == 1:
        _secondMove(engine)
    else:
        print("vratio sam se na follow")
        engine.setState(States.FOLLOW_LINE)
        
        
def _firstMove(engine: engine):
    """
    Go straight a little bit to exit road
    """
    global _startTimeAAA, _stopAfterStraight, _state, _speed, setFirst
    
    if engine.getAngle() != 5 or engine.getSpeed() != _speed:
        return
    else:
        if not setFirst:
            print("postavio vreme")
            setFirst = True
            _startTimeAAA = time.monotonic_ns()
    
    if time.monotonic_ns() - _startTimeAAA > _stopAfterStraight:
        _startTimeAAA = time.monotonic_ns()
        setFirst = False
        print("idem dalje prvi put")
        engine.setSpeed(0)
        engine.setAngle(0)
        _state = 1

def _secondMove(engine: engine):
    """
    Now turn to the right
    """
    global _startTimeAAA, _stopAfterTurn, _state, _angle, _speed, setFirst
    
    engine.setSpeed(_speed)
    engine.setAngle(_angle)
    if engine.getAngle() != _angle or engine.getSpeed() != _speed:
        return
    else:
        if not setFirst:
            print("postavio vreme")
            setFirst = True
            _startTimeAAA = time.monotonic_ns()
    
    if time.monotonic_ns() - _startTimeAAA > _stopAfterTurn:
        print("idem dalje drugi put")
        _state = 2
    