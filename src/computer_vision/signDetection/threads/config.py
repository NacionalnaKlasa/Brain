from dataclasses import dataclass
from src.statemachine.FSM.src.states import OBJECT_CLASSES, States
from enum import Enum, auto

@dataclass(frozen=True)
class YOLOModel:
    # model_path: str = "/home/pi/Documents/Brain/src/computer_vision/signDetection/models/yolov8n_004/best.pt"
    model_path: str = "/home/pi/Documents/Brain/src/computer_vision/signDetection/models/yolo_test/best13Aprl.pt"
    # model_path: str = "/home/pi/Documents/Brain/src/computer_vision/signDetection/models/yolov8n-seg_best.pt"
    model_hef_path = "/home/pi/Documents/HEFmodels/bfmc_yolo_model_stari_p1.hef"
    conf_threshold: float = 0.4
    alpha = 0.2 # Tolerance for position of stop line when it is detected

@dataclass(frozen=True)
class SignClasses:
    classes = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        11: 'stop sign'
    }

class SignConfig:
    def __init__(self):
        self.Model = YOLOModel()
        self.Classes = SignClasses()

        self.FPS = 3
        
  
class Types(Enum):
    CAR = auto()
    SIGN = auto()
    STOP_LINE = auto()
    PEDESTRIAN = auto()
    TRAFFIC_LIGHT = auto()
    
    
OBJECT_TYPES = {
    Types.CAR : OBJECT_CLASSES.get(States.CAR),
    Types.SIGN : [OBJECT_CLASSES.get(States.STOP), 
            OBJECT_CLASSES.get(States.HIGHWAY_ENTRY), 
            OBJECT_CLASSES.get(States.HIGHWAY_EXIT), 
            OBJECT_CLASSES.get(States.PARKING),
            OBJECT_CLASSES.get(States.CROSSWALK),
            OBJECT_CLASSES.get(States.PRIORITY),
            OBJECT_CLASSES.get(States.ROUNDABOUT),
            OBJECT_CLASSES.get(States.ONE_WAY),
            OBJECT_CLASSES.get(States.NO_ENTRY)
            ],
    Types.PEDESTRIAN : OBJECT_CLASSES.get(States.PEDESTRIAN),
    Types.TRAFFIC_LIGHT : [
                     OBJECT_CLASSES.get(States.TRAFIC_LIGHT),
                     OBJECT_CLASSES.get(States.TRAFIC_LIGHT_GREEN),
                     OBJECT_CLASSES.get(States.TRAFIC_LIGHT_RED),
                     OBJECT_CLASSES.get(States.TRAFIC_LIGHT_RED_YELLOW),
                     OBJECT_CLASSES.get(States.TRAFIC_LIGHT_YELLOW)
                     ],
    Types.STOP_LINE : OBJECT_CLASSES.get(States.STOP_LINE)
}