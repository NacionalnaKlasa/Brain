from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

def stateCallbackEnter_followLine(engine: engine):
    engine.sendMessage(Klem, "30")
    engine.sendMessage(SpeedMotor, "200")

def stateCallback_followLine(engine: engine):
    nextState = None

    currentSpeed = engine.getCurrentSpeed()
    if currentSpeed is not None:
        if currentSpeed != 200:
            # engine.sendMessage(SpeedMotor, "200")
            return nextState

    # FOLLOW LINE
    angle = engine.getAngleCV()
    if angle is not None:
        angle = str(int(angle))
        engine.sendMessage(SteerMotor, angle)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        signParts = sign.split()
        
        if signParts[0] == "stop":
            nextState = States.STOP

    return nextState