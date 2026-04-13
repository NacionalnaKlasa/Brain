from pyexpat import model

from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, serialCamera, signDetectionFrame, signDetection)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from src.computer_vision.signDetection.threads.config import SignConfig
from src.computer_vision.signDetection.threads.config import OBJECT_TYPES, Types

###########################
from src.computer_vision.signDetection.threads.hailo_inference import HailoYOLO
###########################

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
        #print(self.config.Model.model_path)
        self.conf_threshold = self.config.Model.conf_threshold
        self.model = YOLO(self.config.Model.model_path)
        #self.model = HailoYOLO(self.config.Model.model_hef_path, conf_threshold=self.conf_threshold)
        self.classes = self.config.Classes.classes
        self.alpha = self.config.Model.alpha

        self.FPS = self.config.FPS
        self.next = self.FPS

        time.sleep(5)

        self.subscribe()
        self.subscribe_senders()
        super(threadsignDetection, self).__init__()

    def subscribe_senders(self):
        self.signDetectionFrameSender = messageHandlerSender(self.queuesList, signDetectionFrame)
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

                for detection in detections:
                    if detection['label'] != "priority":
                        self.sendDetection(msg = f"{detection['label']} {detection['confidence']:.2f} {detection['distance']:.2} {detection['center']}")

    def detect(self, frame):
        # Parametar classes=[11] govori modelu da te zanima SAMO stop sign
        """
        Parameter 'classes=[11]' tells model to look only for that object (in case of base model yolo26: 'stop sign')
        """
        # results = self.model(frame, imgsz=512, conf=self.conf_threshold, classes=list(self.classes.keys()), verbose=False)
        results = self.model(frame, imgsz=512, conf=self.conf_threshold, verbose=False)
        #print(results)
        #results = self.model(frame, conf=self.conf_threshold, classes=list(self.classes.keys()), verbose=False)
       
        #FOCAL_LENGTH = (h_px × udaljenost) / realna_visina
        #FOCAL_LENGTH = (53 × 27) / 6 ≈ 243
        FOCAL_LENGTH = 243
        SIGN_REAL_HEIGHT = 6
        PEDESTRIAN_REAL_HEIGHT = 14
        CAR_REAL_HEIGHT = 12.7
        STOP_LINE_REAL_WIDTH = 41
        TRAFFIC_LIGHT_REAL_HEIGHT = 18
        #CONF_TH = 0.6
        MIN_HEIGHT_PX = 20
        FRAME_WIDTH = frame.shape[1]
        FRAME_WIDTH_CENTER = FRAME_WIDTH / 2

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                h_px = y2 - y1
                w_px = x2 - x1
                x_center = (x1 + x2) / 2
                # print("xyxy[0]:", box.xyxy[0])
                # print("conf[0]:", box.conf[0])
                # print("cls[0]:", box.cls[0])

                if h_px < MIN_HEIGHT_PX:
                    continue
                
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                # print(class_name)
                
                if class_name in OBJECT_TYPES.get(Types.SIGN):
                    distance = (SIGN_REAL_HEIGHT * FOCAL_LENGTH) / h_px
                elif class_name in OBJECT_TYPES.get(Types.PEDESTRIAN):
                    distance = (PEDESTRIAN_REAL_HEIGHT * FOCAL_LENGTH) / h_px
                elif class_name in OBJECT_TYPES.get(Types.CAR):
                    distance = (CAR_REAL_HEIGHT * FOCAL_LENGTH) / h_px
                elif class_name in OBJECT_TYPES.get(Types.TRAFFIC_LIGHT):
                    distance = (TRAFFIC_LIGHT_REAL_HEIGHT * FOCAL_LENGTH) / h_px
                elif class_name in OBJECT_TYPES.get(Types.STOP_LINE):
                    if abs(x_center - FRAME_WIDTH_CENTER) < self.alpha * FRAME_WIDTH:    
                        distance = (STOP_LINE_REAL_WIDTH * FOCAL_LENGTH) / w_px
                    else:
                        continue
                else:
                    distance = 0

                # print(f"Znak: {class_name}, Udaljenost: {distance:.2f} cm")
                # print(f"FRAME_WIDTH: {FRAME_WIDTH}, FRAME_WIDTH_CENTER: {FRAME_WIDTH_CENTER}")

                detections.append({
                    "class_id": int(box.cls[0]),
                    "label": r.names[int(box.cls[0])], 
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].tolist(),
                    "distance": f"{distance:.1f}",
                    "center": int(x_center)
                })
        return detections

    # def detect(self, frame):
    #     results = self.model(frame, classes=[0,1,2,3], imgsz=512, verbose=False,conf=0.25, simplify=True)
    #     detections = []
        
    #     for r in results:
    #         # Proveravamo da li model uopšte ima maske (za slučaj da učitaš običan model)
    #         masks = r.masks.data if r.masks is not None else [None] * len(r.boxes)
            
    #         for box, mask in zip(r.boxes, masks):
    #             det = {
    #                 "class_id": int(box.cls[0]),
    #                 "label": r.names[int(box.cls[0])], 
    #                 "confidence": float(box.conf[0]),
    #                 "bbox": box.xyxy[0].tolist(),
    #                 "mask": None
    #             }
                
    #             # Ako maska postoji, konvertujemo je u format koji OpenCV može da nacrta
    #             if mask is not None:
    #                 # Prebacujemo masku sa GPU-a na CPU, u numpy i skaliramo na veličinu originalnog frejma
    #                 m = mask.cpu().numpy()
    #                 m = cv2.resize(m, (frame.shape[1], frame.shape[0]))
    #                 det["mask"] = (m > 0.5) # Pravimo binarnu masku
                    
    #             detections.append(det)
                
    #     return detections

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
            # print(label_text)

        return frame

    def _strToFrame(self, frame):
        frame = base64.b64decode(frame)
        frame = np.frombuffer(frame, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame
    
    def sendFrame(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame = base64.b64encode(buffer).decode('utf-8')
        self.signDetectionFrameSender.send(frame)

    def sendDetection(self, msg):
        self.signDetectionSender.send(msg)