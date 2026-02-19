from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

_desiredSpeed = 200

def stateCallbackEnter_followLine(engine: engine):
    global _desiredSpeed
    if engine.getCurrentKlem() != 30:
        engine.sendMessage(Klem, "30")
    engine.sendMessage(SpeedMotor, str(_desiredSpeed))

def stateCallback_followLine(engine: engine):
    global _desiredSpeed
    nextState = None

    currentSpeed = engine.getCurrentSpeed()
    if currentSpeed is not None:
        if currentSpeed != _desiredSpeed:
            return nextState

    # FOLLOW LINE
    follow_line(engine)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        signParts = sign.split()
        if signParts[0] == "stop" and float(signParts[2]) < 39.0:
            nextState = States.STOP

        if signParts[0] == "highway":
            nextState = States.HIGHWAY

    return nextState

def stateCallbackEnter_followLineAfterStop(engine: engine):
    global _afterStop
    global _desiredSpeed

    _afterStop = 0
    if engine.getCurrentKlem() != 30:
        engine.sendMessage(Klem, "30")
    engine.sendMessage(SpeedMotor, str(_desiredSpeed))

def stateCallback_followLineAfterStop(engine: engine):
    global _afterStop
    global _desiredSpeed
    nextState = None

    currentSpeed = engine.getCurrentSpeed()
    if currentSpeed is not None:
        if currentSpeed != _desiredSpeed:
            return nextState

    # FOLLOW LINE
    follow_line(engine)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        signParts = sign.split()
        
        if signParts[0] == "stop":
            _afterStop = 0
    else:
        _afterStop += 1

    if _afterStop > 1000:
        nextState = States.FOLLOW_LINE
        
    return nextState