from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

from src.localization.localization.threads.config import Localization
import json

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

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        pass

    def state_change_handler(self):
        pass

    def thread_work(self):
        # Primam podatak
        data_recieved, addr = self.udp.sock.recvfrom(1024)
        print(f"Received from {addr}: {data_recieved.decode()}")

        # Dekodiram podatak i pripremam ga za slanje nazad na PC
        data_to_sent = f"From Car {data_recieved.decode()}"

        # Saljem podatak -- ovo izgleda ne radi, ili dobro ne primam na PC-u
        msg = json.dumps(data_to_sent).encode()
        self.udp.sock.sendto(msg, (self.udp.PC_IP, self.udp.PC_PORT))
        
        # data, addr = self.udp.receive_from_pc()
        # print(f"Received from {addr}: {data.decode()}")
        # msg = {f"speed":"{i}", "angle":"{j}"}
        # self.udp.send_to_pc(msg)
        

