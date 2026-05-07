from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (turnOnLED)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

from .src.controlLed import WS2812
from .src.config import LIGHT_Enum


class threadws2812(ThreadWithStop):
    """This thread handles ws2812.
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

        self.ws2812 = WS2812()

        super(threadws2812, self).__init__()

    def subscribe(self):
        self.ledReceive = messageHandlerSubscriber(self.queuesList, turnOnLED, "lastOnly", True)

    def state_change_handler(self):
        pass

    def _handle_message(self, msg: str):
        """Parse and apply a light control message.

        Expected format: "<LIGHT>_ON" or "<LIGHT>_OFF"
        where <LIGHT> is FRONT, REAR, LEFT, or RIGHT.
        """
        if not isinstance(msg, str):
            return
        msg = msg.strip().upper()
        mapping = {
            "FRONT": LIGHT_Enum.FRONT,
            "REAR":  LIGHT_Enum.REAR,
            "LEFT":  LIGHT_Enum.LEFT,
            "RIGHT": LIGHT_Enum.RIGHT,
        }
        for name, light in mapping.items():
            if msg == f"{name}_ON":
                self.ws2812.turnOn(light)
                return
            if msg == f"{name}_OFF":
                self.ws2812.turnOff(light)
                return

    def thread_work(self):
        msg = self.ledReceive.receive()
        if msg is not None:
            self._handle_message(msg)

        self.ws2812.tick()
