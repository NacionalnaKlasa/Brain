from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States, OBJECT_CLASSES
from src.computer_vision.signDetection.threads.config import Types, OBJECT_TYPES

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

from .config import FORBIDEN_STATES


def stateCallbackEnter_followLine(engine: engine):
    print("ENTER FOLLOWLINE")
    engine.setKlem(30)
    if engine.getSpeed() == 0:
        engine.setSpeed(200)

def stateCallback_followLine(engine: engine):     
    # FOLLOW LINE
    follow_line(engine)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()

    forbiden_states_enum = engine.getStateParameters(FORBIDEN_STATES)
    forbiden_states = []
    if forbiden_states_enum:
        for state in forbiden_states_enum:
            forbiden_states.append(OBJECT_CLASSES[state])

    if sign is not None:
        signParts = sign.split()
        if signParts[0] in OBJECT_TYPES[Types.TRAFFIC_LIGHT]:
            print(signParts)
        # print(sign)
        if float(signParts[2]) < 39:
            if signParts[0] == OBJECT_CLASSES[States.STOP] and signParts[0] not in forbiden_states:
                engine.setState(States.STOP)

            if signParts[0] == OBJECT_CLASSES[States.HIGHWAY_ENTRY] and signParts[0] not in forbiden_states:
                print("HIGHWAY")
                engine.setState(States.HIGHWAY_ENTRY)
                
            if signParts[0] == OBJECT_CLASSES[States.HIGHWAY_EXIT] and signParts[0] not in forbiden_states:
                print("OMG EXIT")
                print(forbiden_states)
                engine.setState(States.HIGHWAY_EXIT)
                
        if signParts[0] == OBJECT_CLASSES[States.STOP_LINE] and signParts[0] not in forbiden_states and float(signParts[2]) < 36:
            print("STOP LINE")
            engine.setState(States.STOP_LINE)

        if signParts[0] == OBJECT_CLASSES[States.PEDESTRIAN] and float(signParts[2]) < 66 and signParts[0] not in forbiden_states:
            print("PEDESTRIAN")
            params = {"start_position": int(signParts[3])}
            engine.setState(States.PEDESTRIAN, params)

        if signParts[0] == OBJECT_CLASSES[States.PARKING] and float(signParts[2]) < 27 and signParts[0] not in forbiden_states:
            print("PARKING")
            engine.setState(States.PARKING)
            
        if signParts[0] in OBJECT_TYPES[Types.TRAFFIC_LIGHT] and float(signParts[2]) < 60 and signParts[0] not in forbiden_states:
            params = {"light": signParts[0]}
            engine.setState(States.TRAFIC_LIGHT, params)

        if signParts[0] == OBJECT_CLASSES[States.ROUNDABOUT] and float(signParts[2]) < 27 and signParts[0] not in forbiden_states:
            print("ROUNDABOUT")
            engine.setState(States.ROUNDABOUT)

        if signParts[0] == OBJECT_CLASSES[States.CAR] and float(signParts[2]) < 27 and signParts[0] not in forbiden_states:
            print("CAR")
            engine.setState(States.CAR)
        