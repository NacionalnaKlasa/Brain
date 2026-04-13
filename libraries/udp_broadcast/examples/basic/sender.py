"""
Osnovni primjer slanja podataka preko UDP-a.

Primjer korišćenja:
    sender = UDP_Sender()
    sender.send("Hello World!", DATA_TYPES.STRING)
    sender.send(42, DATA_TYPES.INTEGER)
    sender.send(3.14, DATA_TYPES.FLOAT)
    sender.send(True, DATA_TYPES.BOOLEAN)
"""

import sys
sys.path.insert(0, '/home/pi/Documents/Brain/libraries/udp_broadcast')

from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE

def main():
    sender = UDP_Sender(mode=BROADCAST_MODE.UNICAST, addresses=["10.14.127.250"], port=9999)
    
    # Primjeri slanja različitih tipova podataka
    while True:
        user_in = str(input())
        sender.send(user_in, DATA_TYPES.STRING)
        print(f"Poslana string poruka {user_in}")

if __name__ == "__main__":
    main()