from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, SpeedMotor, SteerMotor, signDetection, laneDetection)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender
from src.statemachine.FSM.src.states import OBJECT_CLASSES, States
from src.statemachine.FSM.src.callback.callback_intersection import navigation, counter, counterModuo

# from src.localization.localization.threads.config import Localization
import json

from src.localization.localization.threads.src.localizationModul import localizationRPi
from .config import *

class threadlocalization(ThreadWithStop):
    """This thread handles localization.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging
        self.subscribe()
        super(threadlocalization, self).__init__()

        self.udp = Localization()
        
        self.lastSpeed = 0
        self.lastAngle = 0

        self.server = localizationRPi(SERVER_IP, SERVER_PORT)
        while not self.server.start():
            print("Waiting on initMSG...", end="\r")
            time.sleep(0.1)

        self.heartbeat = 40
        self.lastHearbeat = 0

    
    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.speedReceiver = messageHandlerSubscriber(self.queuesList, SpeedMotor, "lastOnly", True)
        self.angleReceiver = messageHandlerSubscriber(self.queuesList, SteerMotor, "lastOnly", True)
        self.signReceiver = messageHandlerSubscriber(self.queuesList, signDetection, "lastOnly", True)
        self.laneReceiver = messageHandlerSubscriber(self.queuesList, laneDetection, "lastOnly", True)

        pass

    def state_change_handler(self):
        pass

    def thread_work(self):
        if self.lastHearbeat < self.heartbeat:
            self.lastHearbeat += 1
        else:
            self.lastHearbeat = 0
            currentSpeed = None
            currentAngle = None
            
            # print("omg")
            lane_rec = self.laneReceiver.receive()
            if lane_rec:
                self.server.send_lane_snap()
                print("[RPI-Kamera] Auto između linija → šaljem lane snap!")

            rec = self.speedReceiver.receive()
            if rec is not None:
                # self.lastSpeed = int(rec)
                currentSpeed = int(rec)
                print("speed ", self.lastSpeed)
                
            rec = self.angleReceiver.receive()
            if rec is not None:
                # self.lastAngle = int(rec)
                currentAngle = int(rec)
            
            # if self.autoConnected:
            #     print("hahaha")
            #     tcpClient(self.auto, self.lastSpeed, self.lastAngle)

            if (currentSpeed != self.lastSpeed and currentSpeed is not None) or (currentAngle != self.lastAngle and currentAngle is not None):
                if currentSpeed is not None:
                    self.lastSpeed = currentSpeed
                if currentAngle is not None:
                    self.lastAngle = currentAngle
                status = self.server.update(speed=self.lastSpeed, steer=self.lastAngle)
                if status:
                    print(f"Speed: {status['speed']:>5} | Steer: {status['steer']:>5.2f}")
            
        
            nextState = navigation[counter % counterModuo]
            if nextState == States.INTERSECTION_STRAIGHT:
                self.server.send_nav_command("STRAIGHT")
            elif nextState == States.INTERSECTION_RIGHT:
                self.server.send_nav_command("RIGHT")
            elif nextState == States.INTERSECTION_LEFT:
                self.server.send_nav_command("LEFT")
            
            
            sign_rec = self.signReceiver.receive()
            if sign_rec is not None:
                # Pretpostavimo da queue pošalje "crosswalk", "stop_line", ili "parking_sign"
                detected_type = str(sign_rec).split()[0]  
                
                # Mapiramo kameru na ona tačna imena koja računar iz CHECKPOINTS_MAP očekuje
                if detected_type == OBJECT_CLASSES[States.STOP_LINE]:
                    self.server.send_checkpoint(OBJECT_CLASSES[States.STOP_LINE])  # Naravno, zavisnood toga gde ste, morate poslati pravu stranu
                    print(f"[RPI-Kamera] Prepoznat {detected_type}, obaveštavam PC Server!")
                elif detected_type == OBJECT_CLASSES[States.CROSSWALK]:
                    self.server.send_checkpoint(OBJECT_CLASSES[States.CROSSWALK])
                    print(f"[RPI-Kamera] Prepoznat {detected_type}, obaveštavam PC Server!")
                elif detected_type == OBJECT_CLASSES[States.PARKING]:
                    self.server.send_checkpoint(OBJECT_CLASSES[States.PARKING])
                    print(f"[RPI-Kamera] Prepoznat {detected_type}, obaveštavam PC Server!")
                
                



        
        # Primam podatak
        # data_recieved, addr = self.udp.sock.recvfrom(1024)
        # print(f"Received from {addr}: {data_recieved.decode()}")

        # # Dekodiram podatak i pripremam ga za slanje nazad na PC
        # data_to_sent = f"From Car {data_recieved.decode()}"

        # # Saljem podatak -- ovo izgleda ne radi, ili dobro ne primam na PC-u
        # msg = json.dumps(data_to_sent).encode()
        # self.udp.sock.sendto(msg, (self.udp.PC_IP, self.udp.PC_PORT))
        
        # data, addr = self.udp.receive_from_pc()
        # print(f"Received from {addr}: {data.decode()}")
        # msg = {f"speed":"{i}", "angle":"{j}"}
        # self.udp.send_to_pc(msg)


#         # U importima dodaj laneDetection
# from src.utils.messages.allMessages import (mainCamera, SpeedMotor, SteerMotor, signDetection, laneDetection)

# # U subscribe() metodi dodaj:
# self.laneReceiver = messageHandlerSubscriber(self.queuesList, laneDetection, "lastOnly", True)

# # U thread_work() bloku (unutar heartbeat if-a), posle sign_rec bloka dodaj:
# lane_rec = self.laneReceiver.receive()
# if lane_rec:
#     self.server.send_lane_snap()
#     print("[RPI-Kamera] Auto između linija → šaljem lane snap!")

        

