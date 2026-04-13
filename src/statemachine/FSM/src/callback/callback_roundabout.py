import time
from src.statemachine.FSM.src.engine import engine
from src.statemachine.FSM.src.states import States, OBJECT_CLASSES
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

__desiredSpeed = 200
__desiredExit : int = [2, 1, 3, 4, 2, 1, 3, 4]

_startTime: float = 0

_time_first_exit : float = 3.5
_time_second_exit : float = 7
_time_third_exit : float = 3 * _time_first_exit
_time_fourth_exit : float = 4 * _time_first_exit

_last_time_saw_roundabout : float = 0
_last_time_saw_roundabout_threshold : float = 1

_start_roundabout = False
_counter_done : int = 0

_time_right_turn_extraction_treshold : float = 2

_time_right_turn_inclusion_treshold : float = 2

_angle_for_inclusion_and_extraction : int = 200

_temp : bool = False

FIRST : int = 1
SECOND : int = 2
THIRD : int = 3
FOURTH : int = 4

def Enter_roundabout(engine: engine):
    global __desiredSpeed, _startTime, _start_roundabout, _counter_done, _last_time_saw_roundabout, _temp

    _last_time_saw_roundabout = _startTime = time.perf_counter()
    _start_roundabout = False
    _counter_done = 0
    _temp = False
    

def Execute_roundabout(engine: engine):
    global _last_time_saw_roundabout_threshold, _last_time_saw_roundabout, _startTime, _start_roundabout, _desiredExit, _temp

    if time.perf_counter() - _last_time_saw_roundabout > _last_time_saw_roundabout_threshold and not _start_roundabout and not _temp:
        _start_roundabout = True
        _startTime = time.perf_counter()
    
    sign = engine.getSign()
    if sign is not None:
        sign = sign.split()
        if sign[0] == OBJECT_CLASSES[States.ROUNDABOUT]:
            _last_time_saw_roundabout = time.perf_counter()
    
    if _start_roundabout:
        enter_roundabout(engine)

    if _temp:
        check_exit_and_go(engine)


def enter_roundabout(engine:engine):
    global _time_right_turn_inclusion_treshold, _angle_for_inclusion_and_extraction, _temp, _startTime, _start_roundabout

    if time.perf_counter() - _startTime < _time_right_turn_inclusion_treshold:
        engine.setAngle(_angle_for_inclusion_and_extraction)
    else:
        _startTime = time.perf_counter()
        print("idem daljeeeeeeeee")
        _temp = True
        _start_roundabout = False


def check_exit_and_go(engine:engine):
    global FIRST, SECOND, THIRD, FOURTH, __desiredExit
    global _time_first_exit, _time_second_exit, _time_third_exit, _time_fourth_exit
    
    if __desiredExit[engine.counterRoundabout] == FIRST:
        go(_time_first_exit, engine)
    elif __desiredExit[engine.counterRoundabout] == SECOND:
        go(_time_second_exit, engine)
    elif __desiredExit[engine.counterRoundabout] == THIRD:
        go(_time_third_exit, engine)
    elif __desiredExit[engine.counterRoundabout] == FOURTH:
        go(_time_fourth_exit, engine)


def go(_time, engine:engine):
    # print(_time)
    global _startTime, _time_right_turn_inclusion_treshold

    if time.perf_counter() - _startTime  <= _time:
        engine.setAngle(-250);
        # follow_line(engine)
    else:
        exit_roundabout(_time, engine)


def exit_roundabout(_time, engine:engine):
    global _angle_for_inclusion_and_extraction

    if time.perf_counter() - _startTime < _time_right_turn_extraction_treshold + _time:
        engine.setAngle(_angle_for_inclusion_and_extraction)
    else:
        engine.counterRoundabout += 1
        engine.setState(States.FOLLOW_LINE)










    
    