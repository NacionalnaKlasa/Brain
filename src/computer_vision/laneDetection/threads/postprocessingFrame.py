import cv2
import math
import numpy as np

class PostprocessingFrame:
    def __init__(self, config):
        self.roi_y_top = config.ROI_Y.roi_top_y
        self.roi_y_bottom = config.ROI_Y.roi_bottom_y
        self.roi = config.ROI

        self.maxSteeringAngle = 250
        self.lastSteeringAngle = 0
        self.lane_width = 280
        self.alpha = 0.46
        self.b = 0.8
        
        self.y_offset = 0.6

        self.k = 1.2

        self.meanValues = []
        for j in range(4):
            self.meanValues.append(0)

    def calculate_lane_center(self, left_line, right_line):
        """Calculate lane center. If one line missing, assume average lane width"""
        if left_line is None and right_line is None:
            return None
        elif left_line is None:
            lane_width = self.lane_width
            return (right_line[0] + right_line[2]) // 2 - lane_width//2
        elif right_line is None:
            lane_width = self.lane_width
            return (left_line[0] + left_line[2]) // 2 + lane_width//2
        else:
            left_x = (left_line[0] + left_line[2]) // 2
            right_x = (right_line[0] + right_line[2]) // 2
            return (left_x + right_x) // 2
        
    def calculate_angle(self, lane_center, frame_width, frame_height):
        car_center = frame_width // 2
        lane_center -= car_center
        lane_center *= self.b
        lane_center += car_center
        error = lane_center - car_center

        y_offset = int(frame_height * self.y_offset)
        
        angle_radian = math.atan(error / y_offset)
        angle_degrees = math.degrees(angle_radian)

        return angle_degrees, car_center, y_offset

    def clamp_angle(self, angle, min_angle=None, max_angle=None):
        if min_angle == None:
            min_angle = -self.maxSteeringAngle
        
        if max_angle == None:
            max_angle = self.maxSteeringAngle
        return max(min(angle, max_angle), min_angle)

    def p_control(self, lane_center, frame_width, frame_height):
        """Simple proportional control steering signal [-1,1]"""
        if lane_center is None:
            return self.lastSteeringAngle, 0, 0

        raw_angle, car_center, y_offset = self.calculate_angle(lane_center, frame_width, frame_height)
        
        raw_angle *= 10
        raw_angle *= self.k
        
        raw_angle = self.clamp_angle(raw_angle)
        for j in range(len(self.meanValues) - 1):
            self.meanValues[j + 1] = self.meanValues[j]

        self.meanValues[0] = raw_angle
        raw_angle = sum(self.meanValues) / len(self.meanValues)

        new_angle = (self.alpha * raw_angle) + (1 - self.alpha) * self.lastSteeringAngle
        self.lastSteeringAngle = new_angle

        return max(min(new_angle, self.maxSteeringAngle), -self.maxSteeringAngle), car_center, y_offset
    
    # Not necessary for car
    def draw_lane_center(self, frame, lane_center, color=(0,0,255), thickness=2):
        """Draw vertical line at lane center"""
        if lane_center is None:
            return frame
        
        h = frame.shape[0]
        cv2.line(frame, (lane_center, int(h*self.roi_y_top)), (lane_center, int(h*self.roi_y_bottom)), color, thickness)
        return frame
    
    def draw_roi(self, frame, color=(0,255,255), thickness=2):
        """Draw ROI rectangle on frame"""
        h, w = frame.shape[:2]
        roi_top = int(h * self.roi_y_top)
        roi_bottom = int(h * self.roi_y_bottom)
        
        # Draw rectangle around ROI
        roi_points = np.array([
            [int(w * self.roi.roi_bottom_left[0]), roi_bottom],
            [int(w * self.roi.roi_bottom_right[0]), roi_bottom],
            [int(w * self.roi.roi_top_right[0]), roi_top],
            [int(w * self.roi.roi_top_left[0]), roi_top]
        ], dtype=np.int32)


        cv2.polylines(frame, [roi_points], isClosed=True, color=color, thickness=thickness)
        return frame

    def draw_angle(self, frame, steering):
        text = f"Steering: {steering:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.6
        color = (255, 255, 255)  # Green in BGR
        thickness = 1

        position = (20, 20)

        cv2.putText(frame, text, position, font, scale, color, thickness, cv2.LINE_AA)
        return frame

    def draw_debug(self, frame, car_center, y_offset):
        if frame is None:
            return frame

        # Get frame dimensions
        height, width = frame.shape[:2]

        # 1. Primary Circle (Current Center)
        # We use car_center_x as X, and y_offset as our fixed Y height
        center_point = (int(car_center), int(y_offset))
        cv2.circle(frame, center_point, 10, (0, 255, 0), -1) # Green filled circle

        # 2. Reference/Target Circle
        # Maybe you want to draw a circle in the absolute middle of the screen 
        # to see how far 'car_center_x' has drifted from the true center.
        true_center_x = width // 2
        true_center_point = (true_center_x, int(y_offset))
        cv2.circle(frame, true_center_point, 12, (0, 0, 255), 2) # Red outline

        # 3. Draw a horizontal line between them to visualize the error
        cv2.line(frame, center_point, true_center_point, (255, 255, 255), 2)

        return frame