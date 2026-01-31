import cv2
import numpy as np
from typing import Tuple, List

class ProcessingFrame():
    def __init__(self, config):
        self.blur_kernel = config.Canny.blur_kernel
        self.canny_low = config.Canny.canny_low
        self.canny_high = config.Canny.canny_high
        self.roi = config.ROI
        self.hough_threshold = config.Hough.hough_threshold
        self.hough_min_line_length = config.Hough.hough_min_line_length
        self.hough_max_line_gap = config.Hough.hough_max_line_gap
        self.min_slope = config.Hough.min_slope
        self.max_slope = config.Hough.max_slope

        # Stop line parametri
        self.stop_min_length_ratio = config.StopLine.min_length_ratio
        self.stop_slope_threshold = config.StopLine.slope_threshold
        self.stop_min_segments = config.StopLine.min_segments
    
    def apply_canny(self, frame: np.ndarray) -> np.ndarray:
        """Convert to grayscale and apply Gaussian blur + Canny"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        kernel = self.blur_kernel
        if kernel % 2 == 0:
            kernel += 1
        blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        return edges
    
    def apply_roi(self, edges: np.ndarray) -> np.ndarray:
        """Apply trapezoid ROI mask"""
        h, w = edges.shape
        pts = []
        for point in self.roi:
            pts.append((np.int32(w * point[0]), np.int32(h * point[1])))
        pts = np.array(pts, dtype=np.int32)
        pts = pts.reshape((-1,1,2))
        
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, [pts], 255)
        return cv2.bitwise_and(edges, mask)
    
    def apply_hough(self, edges: np.ndarray) -> List[Tuple[int,int,int,int]]:
        """Detect lines using Hough Transform and filter by slope"""
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        lane_lines = []
        stop_lines = []
        
        if lines is not None:
            for x1, y1, x2, y2 in lines[:,0]:
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                
                # Horizontalne linije (zaustavne) - koristi konfigurabilan parametar
                if abs(slope) < self.stop_slope_threshold:
                    stop_lines.append((x1, y1, x2, y2))
                # Vertikalne linije (trake)
                elif self.min_slope < abs(slope) < self.max_slope:
                    lane_lines.append((x1, y1, x2, y2))
        
        return lane_lines, stop_lines
    
    def line_average(self, group):
        if not group:
            return None
        x_coords = []
        y_coords = []
        for x1,y1,x2,y2 in group:
            x_coords += [x1,x2]
            y_coords += [y1,y2]
        poly = np.polyfit(y_coords, x_coords, 1)  # x = m*y + b
        y1_out = min(y_coords)
        y2_out = max(y_coords)
        x1_out = int(poly[0]*y1_out + poly[1])
        x2_out = int(poly[0]*y2_out + poly[1])
        return (x1_out, y1_out, x2_out, y2_out)

    
    def average_lines(self, lines: List[Tuple[int,int,int,int]]) -> Tuple[Tuple[int,int,int,int], Tuple[int,int,int,int]]:
        """Separate left/right lines and average them"""
        left_lines = []
        right_lines = []
        for x1, y1, x2, y2 in lines:
            slope = (y2 - y1)/(x2 - x1)
            if slope < 0:
                left_lines.append((x1,y1,x2,y2))
            else:
                right_lines.append((x1,y1,x2,y2))

        left_avg = self.line_average(left_lines)
        right_avg = self.line_average(right_lines)
        return left_avg, right_avg
    
    def fit_stop_line(self, stop_lines: List[Tuple[int,int,int,int]], frame_width: int) -> Tuple[int,int,int,int]:
        """
        Filtrira i fituje zaustavnu liniju koristeći konfiguracione parametre.
        """
        if not stop_lines:
            return None
        
        # KORAK 1: Filtriranje
        min_length = frame_width * self.stop_min_length_ratio
        filtered_lines = []
        
        for x1, y1, x2, y2 in stop_lines:
            length = abs(x2 - x1)
            if length >= min_length:
                filtered_lines.append((x1, y1, x2, y2))
        
        if not filtered_lines:
            return None        
        
        if len(filtered_lines) == 1:
            return filtered_lines[0]
        elif len(filtered_lines) > 1:
            return self.line_average(filtered_lines)
        else:
            return None

    # Not necessary for car
    def draw_lines(self, frame: np.ndarray, left_line, right_line, stop_line, color=(0,255,0), color_stop=(255,0,0), thickness=3) -> np.ndarray:
        """Draw left and right lines on frame"""
        line_img = frame.copy()
        if left_line is not None:
            cv2.line(line_img, (left_line[0], left_line[1]), (left_line[2], left_line[3]), color, thickness)
        if right_line is not None:
            cv2.line(line_img, (right_line[0], right_line[1]), (right_line[2], right_line[3]), color, thickness)
        if stop_line is not None:
            cv2.line(line_img, (stop_line[0], stop_line[1]), (stop_line[2], stop_line[3]), color_stop, thickness)
        return line_img