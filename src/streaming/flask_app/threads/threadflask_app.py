from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (mainCamera, serialCamera)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.utils.messages.messageHandlerSender import messageHandlerSender

import time
import base64
import numpy as np
import cv2
from flask import Flask, render_template, Response
import psutil
import threading
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, template_folder=template_dir)
lastFrameRawData = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    response = Response(getFrame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def getFrame():
    global lastFrameRawData

    frame_bytes = None
    while True:
        if frame_bytes == lastFrameRawData:
            time.sleep(1/60)
            continue

        frame_bytes = lastFrameRawData
        
        if frame_bytes == None:
            continue

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes  + b'\r\n')
            
def flask_app(port=4201):
    kill_process_on_port(port=port)
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False) 

def kill_process_on_port(port=4201):
    """Proverava da li je port zauzet i ubija proces koji ga drži."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Prolazimo kroz sve konekcije procesa
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Port {port} je zauzet od strane procesa {proc.info['name']} (PID: {proc.info['pid']}).")
                    print("Ubijam proces...")
                    proc.terminate() # Prvo probamo fino
                    proc.wait(timeout=3) # Čekamo da umre
                    print("Proces uspešno ugašen.")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


class threadflask_app(ThreadWithStop):
    """This thread handles flask_app.
    Args:
        queueList (dictionary of multiprocessing.queues.Queue): Dictionary of queues where the ID is the type of messages.
        logging (logging object): Made for debugging.
        debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    def __init__(self, queueList, logging, debugging=False):
        time.sleep(5)

        self.queuesList = queueList
        self.logging = logging
        self.debugging = debugging
        self.subscribe()

        print("--- DEBUGG FLASK PATHS ---")
        print(f"Root path: {app.root_path}")
        print(f"Template folder (relative): {app.template_folder}")
        print(f"Template folder (absolute): {os.path.join(app.root_path, app.template_folder)}")
        print("--------------------------")

        self.test = 0
        self.port = 4901
        self._init_flask()
        print("Flask app thread is running...")
        super(threadflask_app, self).__init__()

    def _init_flask(self):
        self.flask_thread = threading.Thread(target=flask_app, args=(self.port,))
        self.flask_thread.start()

    def subscribe(self):
        """Subscribes to the messages you are interested in"""
        self.CameraReceive = messageHandlerSubscriber(self.queuesList, serialCamera, 'lastOnly', True)

    def state_change_handler(self):
        pass

    def stop(self):
        print("Stopping flask app...")
        self.flask_thread.stop()
        kill_process_on_port(port=self.port)
        super(threadflask_app, self).stop()

    def thread_work(self):
        global lastFrameRawData

        if self.test == 0:
            print("Flask app THREAD WORK")
            self.test += 1

        rec = self.CameraReceive.receive()
        if rec is not None:
            lastFrameRawData = base64.b64decode(rec)