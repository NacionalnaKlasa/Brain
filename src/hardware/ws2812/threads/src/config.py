from enum import Enum, auto

SIGNAL_LIGHT_FRONT_RIGHT_ID = [34, 35, 36, 37, 38]
SIGNAL_LIGHT_FRONT_LEFT_ID = [51, 50, 49, 48, 47]


SIGNAL_LIGHT_REAR_RIGHT_ID = [12, 13, 14, 15]
SIGNAL_LIGHT_REAR_LEFT_ID = [5, 4, 3, 2]

LIGHT_FRONT_ID = [39, 40, 41, 42, 43, 44, 45, 46]
LIGHT_REAR_ID = [6, 7, 8, 9, 10, 11]

class LIGHT_Enum(Enum):
	FRONT = auto()
	REAR  = auto()

	LEFT  = auto()
	RIGHT = auto()

	NONE = auto()
