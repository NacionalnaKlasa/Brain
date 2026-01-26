from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, serialCamera, laneDetection)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import base64
from config import Config
from preprocessingFrame import PreprocessingFrame
from processingFrame import ProcessingFrame 
from postprocessingFrame import PostprocessingFrame

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

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.cameraReceive = messageHandlerSubscriber(self.queuesList, serialCamera, "lastOnly", True)
        self.cameraSender = messageHandlerSender(self.queuesList, laneDetection)

    def state_change_handler(self):
        pass

    def frame_receive(self):
        return self.cameraReceive.receive()

    def frame_send(self, frame):
        frame = base64.b64encode(frame)
        self.cameraSender.send(frame)

    def thread_work(self):
        frame = self.frame_receive()
        if frame is not None:
            if self.test < 10:
                self.test += 1
                print("Primio sam sliku")
        else:
            pass

        ##### Processing frame...
        
        # Preprocessing
        gamma = self.preprocessing.apply_gamma(frame)

        # Processing
        edges = self.processing.apply_canny(gamma)
        roi = self.processing.apply_roi(edges)
        lines = self.processing.apply_hough(roi)
        left_avg, right_avg = self.processing.average_lines(lines, frame.shape[1])

        # Postprocessing
        lane_center = self.postprocessing.calculate_lane_center(left_avg, right_avg, frame.shape[1])
        # steering = self.postprocessing.p_control(lane_center, frame.shape[1])

        self.frame_send(frame)

        # Vizualization
        # Not necessary for car
        vis_frame = self.processing.draw_lines(gamma, left_avg, right_avg)
        vis_frame = self.postprocessing.draw_lane_center(vis_frame, lane_center)

        self.frame_send(vis_frame)
