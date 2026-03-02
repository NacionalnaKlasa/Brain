from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States, OBJECT_CLASSES

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

def stateCallbackEnter_followLine(engine: engine):
    engine.setKlem(30)
    if engine.getSpeed() == 0:
        engine.setSpeed(200)

def stateCallback_followLine(engine: engine):     
    # FOLLOW LINE
    follow_line(engine)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        signParts = sign.split()
        print(sign)
        if float(signParts[2]) < 39:
            if signParts[0] == OBJECT_CLASSES[States.STOP]:
                engine.setState(States.STOP)

            if signParts[0] == OBJECT_CLASSES[States.HIGHWAY_ENTRY]:
                print("HIGHWAY")
                engine.setState(States.HIGHWAY_ENTRY)
                
            if signParts[0] == OBJECT_CLASSES[States.HIGHWAY_EXIT]:
                print("OMG EXIT")
                engine.setState(States.HIGHWAY_EXIT)
                
        # if signParts[0] == OBJECT_CLASSES[States.STOP_LINE]:
        #     print("STOP LINE")
        #     engine.setState(States.STOP_LINE)