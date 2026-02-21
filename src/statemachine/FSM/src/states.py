from enum import auto, Enum

class States(Enum):
    IDLE = auto(),
    FOLLOW_LINE = auto(),

    STOP = auto(),
    AFTER_SIGN = auto(),

    HIGHWAY = auto()
    EXIT_HIGHWAY = auto()

    ERROR = auto()