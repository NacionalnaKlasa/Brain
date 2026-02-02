from dataclasses import dataclass
from typing import Tuple

############# Parameters for Preprocessing ##############
# Using dataclass for immutable configuration
@dataclass(frozen=True) 
class Gamma:
    gamma: float = 1
    lut: None | list = None 
#########################################################

############### Parameters for Processing ###############
@dataclass(frozen=True)
class Canny:
    blur_kernel: int = 5
    canny_low: int = 50
    canny_high: int = 150

ROI = [
    (0, 0.95),
    (0.27, 0.95),
    (0.35, 0.76),
    (0.64, 0.76),
    (0.73, 0.95),
    (1, 0.95),
    (0.65, 0.4),
    (0.35, 0.4)
]

#########################################################

############# Parameters for Postprocessing #############
@dataclass(frozen=True)
class Hough:
    hough_threshold: int = 50
    hough_min_line_length: int = 40
    hough_max_line_gap: int = 50
    min_slope: float = 0.3
    max_slope: float = 3.0

@dataclass(frozen=True)
class StopLine:
    min_length_ratio: float = 0.15     # Min dužina linije (30% širine ekrana)
    slope_threshold: float = 0.4       # Max nagib za horizontalnu liniju
    min_segments: int = 1              # Min broj segmenata za validnu stop liniju

#########################################################

class Config:
    def __init__(self):
        self.Gamma = Gamma()
        self.Canny = Canny()
        self.ROI = ROI
        self.Hough = Hough()
        self.StopLine = StopLine()
