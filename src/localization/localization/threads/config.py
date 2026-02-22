import socket
import json
import time

class Localization:
    def __init__(self):

        self.CAR_PORT = 5005
        self.PC_IP = "192.168.50.102"
        self.PC_PORT = 5006

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.CAR_PORT))
        
        print("Listening for UDP messages...")             

    #     # UDP sockets
    #     self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     self.sock_recv.bind(("0.0.0.0", self.CAR_PORT))
    #     self.sock_recv.setblocking(False)

    #     self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     #self.sock_send.bind(("0.0.0.0", self.PC_PORT))

    # def send_to_pc(self, data):
    #     """Send car state to PC for visualization."""
    #     try:
    #         msg = json.dumps(data).encode()
    #         self.sock_send.sendto(msg, (self.PC_IP, self.PC_PORT))
    #     except:
    #         print("Nije poslata")
    #         pass

    # def receive_from_pc(self):
    #     """Non-blocking receive commands from PC."""
    #     try:
    #         data, _ = self.sock_recv.recvfrom(4096)
    #         return json.loads(data.decode())
    #     except:
    #         print("Nije primljena")
    #         return None





