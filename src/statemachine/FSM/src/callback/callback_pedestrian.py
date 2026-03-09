from . import config
import time
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

from src.statemachine.FSM.src.states import OBJECT_CLASSES

_desiredSpeed = 0
_startTime: int = 0
_stopTime: int = 2.5e9
_start_position = 0
_desired_position = 0
_calculate_position = False
_calculate_time = 1e9
_last_calculate_time = 0
_left = False
_right = False
_last_time_saw_pedestrian = 0
_last_time_saw_pedestrian_time = 3.5e9
_left_side_region = 0.25
_right_side_region = 0.75

def stateCallbackEnter_pedestrian(engine: engine):
    global _desiredSpeed, _startTime, _stopTime, _start_position, _desired_position, _calculate_position, _calculate_position, _last_calculate_time, _left, _right, _last_time_saw_pedestrian
    global _left_side_region, _right_side_region

    _calculate_position = False
    _left = _right = False
    _last_calculate_time = 0

    print(engine.getStateParameters("start_position"))    
    
    engine.setSpeed(_desiredSpeed)
    
    _startTime = _last_time_saw_pedestrian = _last_calculate_time = time.monotonic_ns()
    _start_position = engine.getStateParameters("start_position")
    if _start_position < _left_side_region*512:
         _desired_position = _right_side_region*512
         _left = True
    elif _start_position > _right_side_region*512:
        _desired_position = _left_side_region*512
        _right = True
    else:
        _calculate_position = True


def stateCallback_pedestrian(engine: engine):
    global _calculate_time, _last_calculate_time, _left, _right, _last_time_saw_pedestrian, _calculate_position, _desired_position
    global _left_side_region, _right_side_region, _startTime, _last_time_saw_pedestrian_time
    
    if time.monotonic_ns() -_last_time_saw_pedestrian > _last_time_saw_pedestrian_time:
        engine.setState(States.FOLLOW_LINE)

    sign = engine.getSign()
    if sign == None:
        return
    else:
        sign = sign.split()
    
    if sign[0] == OBJECT_CLASSES[States.PEDESTRIAN]:
        _last_time_saw_pedestrian = time.monotonic_ns()
    else:
        return
    
    if int(sign[3]) > _left_side_region*512 and int(sign[3]) < _right_side_region*512:
        _startTime = time.monotonic_ns() 

    if not _calculate_position:
        if _left:
            if (time.monotonic_ns() - _startTime  > _stopTime or int(sign[3]) < _desired_position):
                engine.setLastSign(OBJECT_CLASSES[States.PEDESTRIAN])
                engine.setState(States.AFTER_SIGN)
                print("PREBACUJEM SE NAKON ", sign[3])
        if _right:
            print("VIDIM PESAKA DESNOOOOOOOOOO")
            if (time.monotonic_ns() - _startTime  > _stopTime or int(sign[3]) > _desired_position):
                engine.setLastSign(OBJECT_CLASSES[States.PEDESTRIAN])
                engine.setState(States.AFTER_SIGN)
                print("PREBACUJEM SE NAKON ", sign[3])
    else:
        if time.monotonic_ns() - _last_calculate_time > _calculate_time:
            _last_calculate_time = time.monotonic_ns()
            if abs(_start_position - int(sign[3])) > 33:
                if _start_position - int(sign[3]) < 0:
                    _right = True
                    _calculate_position = False
                    _desired_position = _right_side_region*512
                else:
                    _left = True
                    _calculate_position = False
                    _desired_position = _left_side_region*512
                
                print("CURRENT POSITION ", _start_position)
                print("DESIRED POSITION ", _desired_position)
                

