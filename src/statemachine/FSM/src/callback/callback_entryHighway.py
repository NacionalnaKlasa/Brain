from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

_desiredSpeed = 350

def stateCallbackEnter_entryHighway(engine: engine):
    global _desiredSpeed
    engine.sendMessage(SpeedMotor, str(int(_desiredSpeed)))

def stateCallback_highway(engine: engine):
    global _desiredSpeed
    nextState = None

    currentSpeed = engine.getCurrentSpeed()
    if currentSpeed is not None:
        if currentSpeed != _desiredSpeed:
            return nextState

    # FOLLOW LINE
    follow_line(engine)
    # angle = engine.getAngleCV()
    # if angle is not None:
    #     angle = str(int(angle))
    #     engine.sendMessage(SteerMotor, angle)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        signParts = sign.split()
        print(sign)
        
        if signParts[0] == "stop":
            nextState = States.STOP

        if signParts[0] == "notHighway":
            nextState = States.EXIT_HIGHWAY

    return nextState