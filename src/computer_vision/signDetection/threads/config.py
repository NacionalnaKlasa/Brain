from dataclasses import dataclass

@dataclass(frozen=True)
class YOLOModel:
    model_path: str = "/home/pi/Documents/Brain/src/computer_vision/signDetection/models/yolov8n_002/best.pt"
    # model_path: str = "/home/pi/Documents/Brain/src/computer_vision/signDetection/models/yolov8n-seg_best.pt"
    conf_threshold: float = 0.4

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
