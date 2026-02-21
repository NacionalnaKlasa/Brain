from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

_desiredSpeed = 350

def stateCallbackEnter_entryHighway(engine: engine):
    global _desiredSpeed
    engine.setSpeed(_desiredSpeed)

def stateCallback_highway(engine: engine):
    engine.setLastSign("highway")
    engine.setState(States.AFTER_SIGN)