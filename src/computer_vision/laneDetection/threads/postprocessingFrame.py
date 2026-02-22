import cv2
import math
import numpy as np

class PostprocessingFrame:
    def __init__(self, config):
        self.roi = config.ROI
        self.roi_y_top = max(p[1] for p in self.roi)
        self.roi_y_bottom = min(p[1] for p in self.roi)

        self.maxSteeringAngle = 250.0
        self.lastSteeringAngle = 0.0
        self.lane_width = 280
        self.alpha = 0.63
        self.b = 0.8
        
        
        self.y_offset = 0.54

        self.kp : float = 1.0
        self.ki : float = 0.01
        self.k_aw : float = 0.01
        self.integral : float = 0


        self.meanValues = []
        for _ in range(5):
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
        # __________________________
        #                           |                            
        # lane_center -= car_center |
        # lane_center *= self.b     => Ovo ovde je suvisno, komentarise Kole, mada treba opet zajedno proveriti. 
        # lane_center += car_center |   Bukvalno ove 3 linije rade isto sto 53. i 54. rade same. Optimizacija koda :)
        # __________________________|
        error = lane_center - car_center
        error *= self.b
        y_offset = int(frame_height * self.y_offset)
        
        angle_radian = math.atan(error / y_offset)
        angle_degrees = math.degrees(angle_radian)
        #print(f"Izracunat ugao u stepenima : {angle_degrees}")
        error = angle_degrees * 10
        #print(f"Izracunat ugao u stepenima nakon skaliranja sa 10 : {error}")

        return error, car_center, y_offset

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

        error, car_center, y_offset = self.calculate_angle(lane_center, frame_width, frame_height)
        
        error *= self.kp

        error = self.clamp_angle(error)
        #error = max(min(error, self.maxSteeringAngle), -self.maxSteeringAngle)  Pretpostavljam da je brze ovako nego da pozivamo f-ju, Kole.
        #print(f"Izracunat ugao u stepenima nakon skaliranja sa 10 i klampinga: {error}")
        for j in range(len(self.meanValues) - 1):
            self.meanValues[j + 1] = self.meanValues[j]

        self.meanValues[0] = error
        error = sum(self.meanValues) / len(self.meanValues)
        #print(f"Izracunat ugao u stepenima nakon skaliranja sa 10 i klampinga i usrednjavanja: {error}")

        new_angle = (self.alpha * error) + (1 - self.alpha) * self.lastSteeringAngle
        self.lastSteeringAngle = new_angle

        return max(min(new_angle, self.maxSteeringAngle), -self.maxSteeringAngle), car_center, y_offset
    
    def pi_control(self, lane_center, frame_width, frame_height):

        if lane_center is None:
            return self.lastSteeringAngle, 0, 0

        error, car_center, y_offset = self.calculate_angle(lane_center, frame_width, frame_height)
        print(f"Greska : {error}")
        
        p_control = self.kp * error
        print(f"P upravljanje: {p_control}")
        print(f"I upravljanje: {self.integral}")

        u = p_control + self.integral
        print(f"Izracunato upravljanje: {u}")
        
        u_sat = max(min(u, self.maxSteeringAngle),-self.maxSteeringAngle)

        # Usrednjavanje koje zavisi od staze da dodatno ublazi sizofreniju kod reference
        # for j in range(len(self.meanValues) - 1):
        #     self.meanValues[j + 1] = self.meanValues[j]

        # self.meanValues[0] = error
        # error = sum(self.meanValues) / len(self.meanValues)
       
        print(f"Parametri I dejstva: {self.ki}, {error}, {self.k_aw}, {u_sat - u}")

        self.integral += (self.ki * error + self.k_aw * (u_sat - u))
        print(f"Moguce upravljanje: {u_sat}")
        print("---------------------------------------------------")

        return u_sat, car_center, y_offset


    
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
        
        # Draw rectangle around ROI
        pts = []
        for point in self.roi:
            pts.append((np.int32(w * point[0]), np.int32(h * point[1])))
        pts = np.array(pts, dtype=np.int32)
        pts = pts.reshape((-1,1,2))


        cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
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
    
    def draw_stop(self, frame, stop_lanes, color = (255, 0, 0)):
        if stop_lanes is None:
            return frame
        for stop in stop_lanes:
            if stop is not None:
                x1, y1, x2, y2 = stop
                cv2.line(frame, (int(x1),int(y1)), (int(x2),int(y2)), color, 4)
            
        return frame