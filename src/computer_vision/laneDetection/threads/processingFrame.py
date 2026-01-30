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
        pts = np.array([[
            (int(w * self.roi.roi_bottom_left[0]), int(h * self.roi.roi_bottom_left[1])),
            (int(w * self.roi.roi_bottom_right[0]), int(h * self.roi.roi_bottom_right[1])),
            (int(w * self.roi.roi_top_right[0]), int(h * self.roi.roi_top_right[1])),
            (int(w * self.roi.roi_top_left[0]), int(h * self.roi.roi_top_left[1]))
        ]], dtype=np.int32)
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, pts, 255)
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
        filtered = []
        if lines is not None:
            for x1, y1, x2, y2 in lines[:,0]:
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                if self.min_slope < abs(slope) < self.max_slope:
                    filtered.append((x1, y1, x2, y2))
        return filtered

    # NEW ALGORITHM FOR DETECTING LINES
    def apply_hough_all_lines(self, edges: np.ndarray) -> List[Tuple[int,int,int,int]]:
        """Detect lines using Hough Transform and filter by slope"""
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        filtered_horizontal = []
        filtered_vertical = []
        if lines is not None:
            for x1, y1, x2, y2 in lines[:,0]:
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                
                dx = x2 - x1
                dy = y2 - y1

                angle = np.degrees(np.arctan2(dy, dx))

                if 0.7 < abs(slope) < 3:
                    filtered_vertical.append((x1, y1, x2, y2))
                if abs(angle) < 30:
                    filtered_horizontal.append((x1, y1, x2, y2))

        return filtered_vertical, filtered_horizontal
    
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

        def line_average(group):
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

        left_avg = line_average(left_lines)
        right_avg = line_average(right_lines)
        return left_avg, right_avg

    # NEW ALGORITH FOR STOP LINE DETECTION
    def average_lines_with_stop(self, vertical_lines: List[Tuple[int,int,int,int]], horizontal_lines: List[Tuple[int,int,int,int]]) -> Tuple[Tuple[int,int,int,int], Tuple[int,int,int,int], Tuple[int,int,int,int]]:
        """Separate left/right lines and average them"""
        left_lines = []
        right_lines = []
        for x1, y1, x2, y2 in vertical_lines:
            slope = (y2 - y1)/(x2 - x1)
            if slope < 0:
                left_lines.append((x1,y1,x2,y2))
            else:
                right_lines.append((x1,y1,x2,y2))

        def line_average(group):
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

        def line_average_stop(group):
            if not group:
                return None
            ys = []
            xs_right = []
            xs_left = []

            for x1, y1, x2, y2 in group:
                ys.append((y1 + y2) / 2)
                xs_left.append(min(x1, x2))
                xs_right.append(max(x1,x1))

            if len(ys) == 0:
                return None

            y_avg = int(np.mean(ys)) - 100
            x_left = int(np.mean(xs_left))
            x_right = int(np.mean(xs_right))

            return (x_left, y_avg, x_right + 200, y_avg)

        left_avg = line_average(left_lines)
        right_avg = line_average(right_lines)
        stop_avg = line_average_stop(horizontal_lines)
        return left_avg, right_avg, stop_avg

    # New algorithm for stop lane detection Kole
    def detect_horizontal_stop_line(self, lines: list[tuple[int, int, int, int]], img_height: int, min_length: int = 100, max_angle: float = 15.0) -> tuple[int, int, int, int] | None:
        """
        Detect STOP line (horizontal) from Hough lines.
        Vertical lane detection is NOT affected.
        """

        candidates = []

        for x1, y1, x2, y2 in lines:
            dx = x2 - x1
            dy = y2 - y1

            if dx == 0:
                continue

            angle = abs(np.degrees(np.arctan2(dy, dx)))
            length = np.hypot(dx, dy)

            if (
                angle < max_angle and              # horizontal
                length > min_length and             # long enough
                max(y1, y2) > img_height * 0.55     # below horizon
            ):
                candidates.append((x1, y1, x2, y2))

        if not candidates:
            return None

        # Pick closest to car (lowest in image)
        return max(candidates, key=lambda l: max(l[1], l[3]))


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