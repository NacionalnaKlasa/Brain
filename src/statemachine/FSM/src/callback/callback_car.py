import time
from src.statemachine.FSM.src.engine import engine
from .common.follow_line import follow_line
from src.statemachine.FSM.src.states import States, OBJECT_CLASSES

__desiredSpeed = 200
__startTime : float = 0

_agnle_change_road_track_left = -200
_angle_change_road_track_right = 200

_time_changing_road_track_left : float = 2
_time_changing_road_track_right : float = 2

_time_passing_car : float = 6

safe_to_overtake = False

#_right_side_region = 0.75

# U slucaju preticanja potrebno je dodati da auto u koraku passing veichle ubrzava "dok ne prodje" vozilo u potpunosti
# (moguce samo) na auto putu, s tim sto ce nam biti potrebna info sa nekog desnog bocnog i zadnjeg ultrazvucog/tof senzora
# da li smo se dovoljno udaljili da bismo mogli bezbedno da se vratimo u svoju traku, pretpostavljam da je difoltna traka desna,
# s toga se u nju i vracamo.

def Enter_car(engine:engine):
    global __startTime, safe_to_overtake, __desiredSpeed

    __startTime = time.perf_counter()
    safe_to_overtake = False

    engine.setSpeed(__desiredSpeed)


def Execute_car(engine:engine):
    global safe_to_overtake

    is_safe_to_overtake(engine)
    if safe_to_overtake:
        change_road_track_to_left(engine)
        pass_vehicle(engine)
        change_road_track_to_right(engine)


def is_safe_to_overtake(engine:engine):
    global safe_to_overtake
    # ovde se proverava informacija iz modela ili lokalizacije/liste prethodno vidjenih znakova,
    # da li detektuje isprekidanu i na osnovu toga postavlja fleg safe_to_overtake na odgovarajucu vrednost 
    pass


def change_road_track_to_left(engine:engine):
    global _going_around_car, _agnle_change_road_track_left, __startTime, _time_changing_road_track_left

    if time.perf_counter() - __startTime < _time_changing_road_track_left:
        engine.setAngle(_agnle_change_road_track_left)


def pass_vehicle(engine:engine):
    global __startTime, _time_passing_car, _time_changing_road_track_left

    if time.perf_counter() - __startTime < _time_passing_car + _time_changing_road_track_left:
        follow_line()


def change_road_track_to_right(engine:engine):
    global __startTime, _time_changing_road_track_left, _time_changing_road_track_right, _time_passing_car, _angle_change_road_track_right
    if time.perf_counter() - __startTime < _time_changing_road_track_right + _time_passing_car + _time_changing_road_track_left:
        engine.setAngle(_angle_change_road_track_right)
    else:
        engine.setState(States.FOLLOW_LINE)


