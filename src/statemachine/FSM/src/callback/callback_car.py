import time
from src.statemachine.FSM.src.engine import engine
from .common.follow_line import follow_line
from src.statemachine.FSM.src.states import States, OBJECT_CLASSES

__desiredSpeed = 200
__startTime : float = 0

_agnle_change_road_track_left = -250
_angle_change_road_track_right = 250

_time_changing_road_track_left : float = 1.8
_time_changing_road_track_right : float = 1.8

_time_passing_car : float = 4

safe_to_overtake = False

_counter_done : int = 0

CHANGE_TO_LEFT = 0
PASS = 1
CHANGE_TO_RIGHT = 2

#_right_side_region = 0.75

# U slucaju preticanja potrebno je dodati da auto u koraku passing veichle ubrzava "dok ne prodje" vozilo u potpunosti
# (moguce samo) na auto putu, s tim sto ce nam biti potrebna info sa nekog desnog bocnog i zadnjeg ultrazvucog/tof senzora
# da li smo se dovoljno udaljili da bismo mogli bezbedno da se vratimo u svoju traku, pretpostavljam da je difoltna traka desna,
# s toga se u nju i vracamo.

def Enter_car(engine:engine):
    global __startTime, safe_to_overtake, __desiredSpeed, _counter_done

    __startTime = time.perf_counter()

    safe_to_overtake = False
    _counter_done = 0
    
    engine.setSpeed(__desiredSpeed)


def Execute_car(engine:engine):
    global safe_to_overtake, _counter_done
        

    # is_safe_to_overtake(engine)
    # if safe_to_overtake:
    if _counter_done == CHANGE_TO_LEFT:
        change_road_track_to_left(engine)
    elif _counter_done == PASS:
        pass_vehicle(engine)
    elif _counter_done == CHANGE_TO_RIGHT:
        change_road_track_to_right(engine)


def is_safe_to_overtake(engine:engine):
    global safe_to_overtake
    # ovde se proverava informacija iz modela ili lokalizacije/liste prethodno vidjenih znakova,
    # da li detektuje isprekidanu i na osnovu toga postavlja fleg safe_to_overtake na odgovarajucu vrednost 
    pass


def change_road_track_to_left(engine:engine):
    global _going_around_car, _agnle_change_road_track_left, __startTime, _time_changing_road_track_left, _counter_done

    if time.perf_counter() - __startTime < _time_changing_road_track_left:
        print(f"promenio u levo, brojac {_counter_done}")
        engine.setAngle(_agnle_change_road_track_left)
    else:
        _counter_done += 1


def pass_vehicle(engine:engine):
    global __startTime, _time_passing_car, _time_changing_road_track_left, _counter_done

    if time.perf_counter() - __startTime < _time_passing_car + _time_changing_road_track_left:
        print("prosao auto")
        follow_line(engine)
    else:
        _counter_done += 1


def change_road_track_to_right(engine:engine):
    global __startTime, _time_changing_road_track_left, _time_changing_road_track_right, _time_passing_car, _angle_change_road_track_right
    if time.perf_counter() - __startTime < _time_changing_road_track_right + _time_passing_car + _time_changing_road_track_left:
        engine.setAngle(_angle_change_road_track_right)
    else:
        print("promenio u desno")
        engine.setState(States.FOLLOW_LINE)


