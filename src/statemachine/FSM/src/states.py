from enum import auto, Enum

class States(Enum):
    IDLE = auto(),
    FOLLOW_LINE = auto(),
    STOP = auto(),
    ERROR = auto()