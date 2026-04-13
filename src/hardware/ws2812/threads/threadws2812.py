from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (turnOnLED)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import board
import neopixel
import time

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

        self.pixel_pin = board.D18        # GPIO 18
        self.num_pixels = 60           # Broj tvojih dioda
        self.ORDER = neopixel.GRB

        self.pixels = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=0.2, auto_write=False, pixel_order=self.ORDER
        )

        super(threadws2812, self).__init__()

    def subscribe(self):
        self.ledReceive = messageHandlerSubscriber(self.queuesList, turnOnLED, "lastOnly", True)

    def state_change_handler(self):
        pass

    def simple_color_fill(self):
    # Crvena boja
        self.pixels.fill((255, 0, 0))
        self.pixels.show()
        time.sleep(1)

        # Zelena boja
        self.pixels.fill((0, 255, 0))
        self.pixels.show()
        time.sleep(1)

        # Zelena boja
        self.pixels.fill((0, 0, 255))
        self.pixels.show()
        time.sleep(1)

        # Zelena boja
        self.pixels.fill((255, 255, 255))
        self.pixels.show()
        time.sleep(1)

        # Zelena boja
        self.pixels.fill((0, 0, 0))
        self.pixels.show()  
        time.sleep(1)

    def turnOn(self):
        #self.pixels.fill((0, 255, 0))
        self.pixels[50] = (255, 255, 255)
        self.pixels[46] = (255, 255, 255)
        self.pixels[47] = (255, 255, 255)
        self.pixels[48] = (255, 255, 255)
        self.pixels[49] = (255, 255, 255)
        self.pixels[51] = (255, 255, 255)
        self.pixels[52] = (255, 255, 255)
        self.pixels[53] = (255, 255, 255)


        self.pixels.show()

    def thread_work(self):
        recv : str = self.ledReceive.receive()
        if recv is not None:
            if recv == "ON":
                pass

        self.turnOn()

