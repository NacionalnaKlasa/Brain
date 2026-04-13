from . import config
import time
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

from src.statemachine.FSM.src.states import OBJECT_CLASSES

from src.statemachine.FSM.src.callback.common.follow_line import follow_line

_desiredSpeed = 200
_desiredAngle_step_1_park_in : int = 0
_desiredAngle_step_2_park_in : int = 250
_desiredAngle_step_3_park_in : int = -250
_desiredAngle_step_4_park_in : int = 0
_desiredAngle_step_1_park_out : int = 0
_desiredAngle_step_2_park_out : int = -220

_startTime: float = 0
# _time_park_in_forward : int = 6e9
_time_park_in_forward : float = 6.8

# _time_park_in_back_right : int = 2.5e9
_time_park_in_back_right : float = 2.5

# _time_park_in_back_left : int = 4e9
_time_park_in_back_left : float = 4

# _time_park_in_spot_forward : int = 1e9
_time_park_in_spot_forward : float = 1

# __time_park_out_spot_back : int = 1e9
__time_park_out_spot_back : float = 1

# _time_park_out_forward_left : int = 1.5e9
_time_park_out_forward_left : float = 2.6

# _time_to_stay_on_spot: int = 3e9
_time_to_stay_on_spot: float = 3

# _last_time_saw_parking : int = 0
_last_time_saw_parking : float = 0

# _last_time_saw_parking_treshold : int = 2e9
_last_time_saw_parking_treshold : float = 2

_start_parking = False
_counter_done : int = 0

def stateCallbackEnter_parking(engine: engine):
    global _desiredSpeed, _startTime, _start_parking, _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _counter_done

    _start_parking = False

    _counter_done = 0 

    engine.setSpeed(_desiredSpeed)
    engine.setKlem(30)
    
    _startTime = time.perf_counter()
    # print(_startTime)


def stateCallback_parking(engine: engine):
    global _startTime, _last_time_saw_parking,_last_time_saw_parking_treshold, _start_parking, _time_park_in_forward, _time_park_in_back_right, _time_park_in_back_left, _time_park_in_spot_forward, __time_park_out_spot_back, _time_park_out_forward_left
    global _desiredSpeed, _desiredAngle_step_1_park_in, _desiredAngle_step_2_park_in, _desiredAngle_step_3_park_in, _desiredAngle_step_4_park_in,  _desiredAngle_step_1_park_out, _desiredAngle_step_2_park_out
    global  _counter_done, _desiredSpeed, _time_to_stay_on_spot

    if time.perf_counter() -_last_time_saw_parking > _last_time_saw_parking_treshold and not _start_parking:
        print("NE VIDIM VISE ZNAK")
        _start_parking = True
        _startTime = time.perf_counter()
        # print(_startTime)
        follow_line(engine)

    sign = engine.getSign()
    if sign is not None:
        sign = sign.split()
        if sign[0] == OBJECT_CLASSES[States.PARKING]:
            _last_time_saw_parking = time.perf_counter()
    
    if _start_parking:
        if _counter_done == 0:
            drive_forward_park_in(_time_park_in_forward, engine)
        elif _counter_done == 1:
            drive_back_right_park_in(_time_park_in_back_right, _desiredAngle_step_2_park_in, -_desiredSpeed, engine)
        elif _counter_done == 2:
            drive_back_left_park_in(_time_park_in_back_left, _desiredAngle_step_3_park_in, -_desiredSpeed, engine)
        elif _counter_done == 3:
            drive_forward_in_spot_park_in(_time_park_in_spot_forward, _desiredAngle_step_4_park_in, _desiredSpeed, engine)
        elif _counter_done == 4:
            stay_in_place(_time_to_stay_on_spot, 0, 0, engine)
        elif _counter_done == 5:
            drive_back_park_out_spot(__time_park_out_spot_back, _desiredAngle_step_1_park_out, -_desiredSpeed, engine)
        elif _counter_done == 6:
            drive_forward_left_park_out(_time_park_out_forward_left, _desiredAngle_step_2_park_out, _desiredSpeed, engine)
    
    if _counter_done == 7:
        _counter_done = 0
        engine.setState(States.FOLLOW_LINE)
    

def park(_time, _desiredAngle, _desiredSpeed, engine:engine):
    global _startTime
    if time.perf_counter() - _startTime <_time:
        # print("usao ovde ?")
        engine.setAngle(_desiredAngle)
        engine.setSpeed(_desiredSpeed)
        return True
    else:
        return False   

def drive_forward_park_in(_time, engine:engine):
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done
    global _desiredSpeed
    #print("USAO U KORAK 1")
    if time.perf_counter() - _startTime <_time:
        follow_line(engine)
        _step_1_park_in = True
    else:
        print("ZAVRSIO SAM KORAK 1 ", end="")
        # _step_1_park_in = False
        # _step_2_park_in = True
        # _step_3_park_in = False
        # _step_4_park_in = False
        # _step_1_park_out = False
        # _step_2_park_out = False
        _counter_done += 1
        follow_line(engine)
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_back_right_park_in(_time, _desiredAngle, _desiredSpeed, engine:engine):
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done
    #print("USAO U KORAK 2")
    if park(_time, _desiredAngle, _desiredSpeed, engine):
    #    print(f"KORAK 2 ULAZIM DA SALJEM UGAO: {_desiredAngle} i BRZINU: {_desiredSpeed}")
       _step_2_park_in = True
    else:
        print("ZAVRSIO SAM KORAK 2 ", end="")
        # _step_1_park_in = False
        # _step_2_park_in = False
        # _step_3_park_in = True
        # _step_4_park_in = False
        # _step_1_park_out = False
        # _step_2_park_out = False
        _counter_done += 1
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_back_left_park_in(_time, _desiredAngle, _desiredSpeed, engine:engine):
    #print("USAO U KORAK 3")
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done

    if park(_time, _desiredAngle, _desiredSpeed, engine):
    #    print(f"KORAK 3 ULAZIM DA SALJEM UGAO: {_desiredAngle} i BRZINU: {_desiredSpeed}")
       _step_3_park_in = True
    else:
        # _step_1_park_in = False
        # _step_2_park_in = False
        # _step_3_park_in = False
        # _step_4_park_in = True
        # _step_1_park_out = False
        # _step_2_park_out = False
        _counter_done += 1
        print("ZAVRSIO SAM KORAK 3 ", end="")
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_forward_in_spot_park_in(_time, _desiredAngle, _desiredSpeed, engine:engine):
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done

    if park(_time, _desiredAngle, _desiredSpeed, engine):
       _step_4_park_in = True
    else:
        # _step_1_park_in = False
        # _step_2_park_in = False
        # _step_3_park_in = False
        # _step_4_park_in = False
        # _step_1_park_out = True
        # _step_2_park_out = False
        _counter_done += 1
        print("ZAVRSIO SAM KORAK 4 ", end="")
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def stay_in_place(_time, _desiredSpeed, _desiredAngle, engine:engine):
    global _startTime, _counter_done

    if not park(_time, _desiredSpeed, _desiredAngle, engine):
        _counter_done += 1
        print("ZAVRSIO SAM KORAK 5 ", end="")
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_back_park_out_spot(_time, _desiredAngle, _desiredSpeed, engine:engine):
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done

    if park(_time, _desiredAngle, _desiredSpeed, engine):
       _step_1_park_out = True
    else:
        # _step_1_park_in = False
        # _step_2_park_in = True
        # _step_3_park_in = False
        # _step_4_park_in = False
        # _step_1_park_out = False
        # _step_2_park_out = True
        _counter_done += 1
        print("ZAVRSIO SAM KORAK 6 ", end="")
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_forward_left_park_out(_time, _desiredAngle, _desiredSpeed, engine:engine):
    global _step_1_park_in, _step_2_park_in, _step_3_park_in, _step_4_park_in, _step_1_park_out, _step_2_park_out, _startTime, _counter_done

    if park(_time, _desiredAngle, _desiredSpeed, engine):
       _step_2_park_in = True
    else:
        _step_2_park_out = False
        _counter_done += 1
        
        print("ZAVRSIO SAM KORAK 7 ", end="")
        t = time.perf_counter()
        print(_startTime, t)
        _startTime = t

def drive_forward_right_park_out(_time, _desiredAngle):
    pass   



