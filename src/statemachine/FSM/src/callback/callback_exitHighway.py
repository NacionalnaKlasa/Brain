from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

_desiredSpeed = 200

def stateCallbackEnter_exitHighway(engine: engine):
    global _desiredSpeed
    engine.sendMessage(SpeedMotor, str(int(_desiredSpeed)))

def stateCallback_exitHighway(engine: engine):
    global _desiredSpeed
    nextState = None

    currentSpeed = engine.getCurrentSpeed()
    if currentSpeed is not None:
        if currentSpeed == _desiredSpeed:
            nextState = States.FOLLOW_LINE

    return nextState