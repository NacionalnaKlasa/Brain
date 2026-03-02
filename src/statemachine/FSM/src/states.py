from enum import auto, Enum

class States(Enum):
    IDLE = auto()
    FOLLOW_LINE = auto()

    STOP = auto(),
    AFTER_SIGN = auto()

    ERROR = auto()
    
    STOP_LINE = auto()
    
    PARKING = auto()
    PRIORITY = auto()
    CROSSWALK = auto()
    HIGHWAY_ENTRY = auto()
    HIGHWAY_EXIT = auto()
    ROUNDABOUT = auto()
    ONE_WAY = auto()
    NO_ENTRY = auto()
    
    INTERSECTION = auto()
    INTERSECTION_LEFT = auto()
    INTERSECTION_RIGHT = auto()
    INTERSECTION_STRAIGHT = auto()

    PEDESTRIAN = auto()
    TRAFIC_LIGHT = auto()
    TRAFIC_LIGHT_GREEN = auto()
    TRAFIC_LIGHT_YELLOW = auto()
    TRAFIC_LIGHT_RED = auto()
    TRAFIC_LIGHT_RED_YELLOW = auto()
    
    CAR = auto()
    PARKING_SPOT = auto()
    
OBJECT_CLASSES = {
    States.STOP: "stop",
    States.PARKING: "parking",
    States.PRIORITY: "priority",
    States.CROSSWALK: "crosswalk",
    States.HIGHWAY_ENTRY: "highwayEntry",
    States.HIGHWAY_EXIT: "highwayExit",
    States.ROUNDABOUT: "roundabout",
    States.ONE_WAY: "oneWay",
    States.NO_ENTRY: "noEntry",

    States.PEDESTRIAN: "pedestrian",
    States.INTERSECTION: "intersection",
    States.TRAFIC_LIGHT: "light",
    States.TRAFIC_LIGHT_GREEN: "lightGreen",
    States.TRAFIC_LIGHT_YELLOW: "lightYellow",
    States.TRAFIC_LIGHT_RED: "lightRed",
    States.TRAFIC_LIGHT_RED_YELLOW: "lightRedYellos",
    States.STOP_LINE: "stopLine",
    States.CAR: "car",

    States.PARKING_SPOT: "parkingSpot"
}