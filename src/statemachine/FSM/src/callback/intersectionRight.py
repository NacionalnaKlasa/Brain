import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

from src.statemachine.FSM.src.callback.common.follow_line import follow_line

_startTime: int = 0
_stopAfterStraight = 3.5e9
_fff = 0.3e9
_followLineTimeout = _fff

_stopAfterTurn = 3e9 + _followLineTimeout
_stop: bool = False

_speed: int = 200 
_angle: int = 160

_state: int = 0
setFirst = False

#####

# SHOULD GO TO NEXT STATE IN THE IF 
#           AND REMOVE "and not _stop" FROM IF CONDITION

#####

def Enter_intersectionRight(engine: engine):
    print("ENTER INTERSECTION RIGHT")
    global _startTime, _stop, _speed, setFirst, _angle, _stopAfterTurn, _followLineTimeout, _fff
    
    engine.setKlem(30)
    engine.setSpeed(_speed)
    
    _startTime = time.monotonic_ns()
    # print(_startTime)
    print("engine counter", engine.counter)
    if engine.counter == 2:
        print("pa onda sam povecao ????")
        _followLineTimeout = 0
    elif engine.counter == 5:
        _followLineTimeout = 1e9
    else:
        _followLineTimeout = _fff
    
    # print(_startTime)
    # print(_startTime + _stopAfterTurn)
    # print(_startTime, " ", _stopAfterTurn)
    
    # _stop = False
    # setFirst = False
    
    
def Execute_intersectionRight(engine: engine):
    global _startTime, _stopAfterTurn, _state, _followLineTimeout, _angle
    t = time.monotonic_ns()
    if t - _startTime < _followLineTimeout:
        follow_line(engine)
        print("OVDE BIH TREBAO MALO DA IDEM PRAVO PRVO")
        # _startTime = time.monotonic_ns()
        # print("STANIIIIII")
        # engine.setSpeed(0)
        # engine.setAngle(0)
    elif t - _startTime < _stopAfterTurn:
        # print("MOLIM TE POSTAVI UGAO NA ", _angle)
        engine.setAngle(_angle)
    else:
        engine.setState(States.FOLLOW_LINE)
        
        
        
        
    # global _state
    
    # if _state == 0:
    #     _firstMove(engine)
    # elif _state == 1:
    #     _secondMove(engine)
    # else:
    #     print("vratio sam se na follow")
    #     engine.setState(States.FOLLOW_LINE)
        
        
def _firstMove(engine: engine):
    """
    Go straight a little bit to exit road
    """
    global _startTimeAAA, _stopAfterStraight, _state, _speed, setFirst
    
    if engine.getAngle() != 5 or engine.getSpeed() != _speed:
        return
    else:
        if not setFirst:
            # print("postavio vreme")
            setFirst = True
            _startTimeAAA = time.monotonic_ns()
    
    if time.monotonic_ns() - _startTimeAAA > _stopAfterStraight:
        _startTimeAAA = time.monotonic_ns()
        setFirst = False
        # print("idem dalje prvi put")
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
            # print("postavio vreme")
            setFirst = True
            _startTimeAAA = time.monotonic_ns()
    
    if time.monotonic_ns() - _startTimeAAA > _stopAfterTurn:
        # print("idem dalje drugi put")
        _state = 2
    