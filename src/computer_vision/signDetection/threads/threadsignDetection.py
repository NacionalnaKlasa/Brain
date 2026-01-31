from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, serialCamera, signDetection)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from src.computer_vision.signDetection.threads.config import SignConfig

class threadsignDetection(ThreadWithStop):
    """This thread handles signDetection.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging

        self.config = SignConfig()
        print(self.config.Model.model_path)
        self.model = YOLO(self.config.Model.model_path)
        self.classes = self.config.Classes.classes
        self.conf_threshold = self.config.Model.conf_threshold

        self.FPS = self.config.FPS
        self.next = self.FPS

        time.sleep(5)

        self.subscribe()
        self.subscribe_senders()
        super(threadsignDetection, self).__init__()

    def subscribe_senders(self):
        self.signDetectionSender = messageHandlerSender(self.queuesList, signDetection)

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.serialCamera = messageHandlerSubscriber(self.queuesList, serialCamera, 'lastOnly', True)

    def state_change_handler(self):
        pass

    def thread_work(self):
        frame = self.serialCamera.receive()
        if frame is not None:
            if self.next <= 0:
                self.next = self.FPS
            else:
                self.next -= 1
                frame = self._strToFrame(frame)
                # DETECT
                detections = self.detect(frame)
                # DRAW
                frame = self.draw(frame, detections)
                # SEND
                #frame = cv2.resize(frame, (512, 270), interpolation=cv2.INTER_LINEAR)
                self.sendFrame(frame)

    def detect(self, frame):
        # Parametar classes=[11] govori modelu da te zanima SAMO stop sign
        """
        Parameter 'classes=[11]' tells model to look only for that object (in case of base model yolo26: 'stop sign')
        """
        # results = self.model(frame, imgsz=512, conf=self.conf_threshold, classes=list(self.classes.keys()), verbose=False)
        results = self.model(frame, imgsz=512, conf=self.conf_threshold, verbose=False)
        #results = self.model(frame, conf=self.conf_threshold, classes=list(self.classes.keys()), verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class_id": int(box.cls[0]),
                    "label": r.names[int(box.cls[0])], 
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].tolist()
                })
        return detections

    def draw(self, frame, detections):
        for det in detections:
            # Taking coords from dictionary returned from 'detect()'
            x1, y1, x2, y2 = map(int, det["bbox"])
            conf = det["confidence"]
            
            # Key: using 'label' which 'detect()' already returned from r.names
            label_text = f"{det['label']} {conf:.2f}"

            # Drawing rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Drawing background for text
            label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + label_size[0], y1), (0, 255, 0), -1)

            # Printing text
            cv2.putText(
                frame,
                label_text,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
            print(label_text)

        return frame

    def _strToFrame(self, frame):
        frame = base64.b64decode(frame)
        frame = np.frombuffer(frame, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame
    
    def sendFrame(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame = base64.b64encode(buffer).decode('utf-8')
        self.signDetectionSender.send(frame)