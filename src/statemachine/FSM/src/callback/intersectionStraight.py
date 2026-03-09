import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

_startTime: int = 0
_stopAfter: int = 5e9
_stop: bool = False

_heartbeat = 200
_last_heartbeat = 0

_speed: int = 200 
_angle: float = 0.0
_final_angle: float = -150.0
_step_angle :float = _final_angle / (_stopAfter/(1e6*_heartbeat))



#####

# SHOULD GO TO NEXT STATE IN THE IF 
#           AND REMOVE "and not _stop" FROM IF CONDITION

#####

def Enter_intersectionStraight(engine: engine):
    global _startTime, _stop, _angle, _speed, _step_angle, _last_heartbeat
 
    _angle = 0.0
    _last_heartbeat = 0
    # print(_step_angle)
    
    engine.setAngle(int(_angle))
    engine.setSpeed(_speed)
    _startTime = time.monotonic_ns()
    
def Execute_intersectionStraight(engine: engine):
    global _startTime, _stopAfter, _stop, _angle, _final_angle, _step_angle, _heartbeat, _last_heartbeat
    
    # print(int(_angle), _step_angle)

    if _last_heartbeat > _heartbeat:
        _last_heartbeat = 0
        engine.setAngle(int(_angle))
        if abs(_angle) < abs(_final_angle):
            _angle += _step_angle
        else:
            _angle = _final_angle
    else:
        _last_heartbeat += 1 

    if time.monotonic_ns() - _startTime > _stopAfter:
        engine.setState(States.FOLLOW_LINE)
        # engine.setAngle(0)
        # engine.setSpeed(0)
        # engine.setKlem(0)
    
 