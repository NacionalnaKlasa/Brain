from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, SpeedMotor, SteerMotor)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

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
        pass

    def state_change_handler(self):
        pass

    def thread_work(self):
        if self.lastHearbeat < self.heartbeat:
            self.lastHearbeat += 1
        else:
            self.lastHearbeat = 0
            
            print("omg")
            rec = self.speedReceiver.receive()
            if rec is not None:
                self.lastSpeed = int(rec)
                print("speed ", self.lastSpeed)
                
            rec = self.angleReceiver.receive()
            if rec is not None:
                self.lastAngle = int(rec)
            
            # if self.autoConnected:
            #     print("hahaha")
            #     tcpClient(self.auto, self.lastSpeed, self.lastAngle)

            status = self.server.update(speed=self.lastSpeed, steer=self.lastAngle)
            if status:
                print(f"Speed: {status['speed']:>5} | Steer: {status['steer']:>5.2f}")

        
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
        

