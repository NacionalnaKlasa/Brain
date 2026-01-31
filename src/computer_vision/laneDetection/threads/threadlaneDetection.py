from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (serialCamera, laneDetection, CalculatedAngle)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import base64
import numpy as np
import cv2
from src.computer_vision.laneDetection.threads.config import Config
from src.computer_vision.laneDetection.threads.preprocessingFrame import PreprocessingFrame
from src.computer_vision.laneDetection.threads.processingFrame import ProcessingFrame 
from src.computer_vision.laneDetection.threads.postprocessingFrame import PostprocessingFrame

class threadlaneDetection(ThreadWithStop):
    """This thread handles laneDetection.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging

        self.test = 0
        time.sleep(5)

        self.config = Config()
        self.preprocessing = PreprocessingFrame(self.config)
        self.processing = ProcessingFrame(self.config)
        self.postprocessing = PostprocessingFrame(self.config)

        self.subscribe()
        super(threadlaneDetection, self).__init__()

    def subscribe_senders(self):
        self.cameraSender = messageHandlerSender(self.queuesList, laneDetection)
        self.steeringSender = messageHandlerSender(self.queuesList, CalculatedAngle)

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.cameraReceive = messageHandlerSubscriber(self.queuesList, serialCamera, "lastOnly", True)

    def state_change_handler(self):
        pass

    def _strToFrame(self, frame):
        frame = base64.b64decode(frame)
        frame = np.frombuffer(frame, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame
    
    def _frameToStr(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')

    def receievFrame(self):
        return self.cameraReceive.receive()

    def sendFrame(self, frame):
        frame = self._frameToStr(frame)
        self.cameraSender.send(frame)

    def sendSteering(self, steering):
        self.steeringSender.send(steering)

    def thread_work(self):
        frame = self.receievFrame()
        if frame is None:
            return
        frame = self._strToFrame(frame)
        if frame is None:
            print("Error while decoding image !")
            return
        
        # Preprocessing
        gamma = self.preprocessing.apply_gamma(frame)

        # Processing
        edges = self.processing.apply_canny(gamma)
        roi = self.processing.apply_roi(edges)

        lines, stop_lines = self.processing.apply_hough(roi)

        left_avg, right_avg = self.processing.average_lines(lines)
        stop_line = self.processing.fit_stop_line(stop_lines, frame.shape[1])

        # Postprocessing
        # Calculating error and angle to send for servo motors
        lane_center = self.postprocessing.calculate_lane_center(left_avg, right_avg)
        steering, car_center, y_offset = self.postprocessing.p_control(lane_center, frame.shape[1], frame.shape[0])
      
        # # Vizualization
        # # Not necessary for car
        vis_frame = self.postprocessing.draw_lines(gamma, left_avg, right_avg, None)
        vis_frame = self.postprocessing.draw_stop(vis_frame, stop_lines)
        #vis_frame = self.postprocessing.draw_stop(vis_frame, filtered_lines)
        vis_frame = self.postprocessing.draw_stop(vis_frame, [stop_line], color = (0, 0, 255))
        vis_frame = self.postprocessing.draw_lane_center(vis_frame, lane_center)
        vis_frame = self.postprocessing.draw_roi(vis_frame)
        vis_frame = self.postprocessing.draw_angle(vis_frame, steering)
        vis_frame = self.postprocessing.draw_debug(vis_frame, car_center, y_offset)

        self.sendFrame(vis_frame)

        ####### VERY IMPORTANT TO SEND
        self.sendSteering(steering)
        ####### VERY IMPORTANT TO SEND