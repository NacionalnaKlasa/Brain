from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

from .config import FORBIDEN_STATES
from src.statemachine.FSM.src.states import States, OBJECT_CLASSES

_desiredSpeed = 400

def stateCallbackEnter_entryHighway(engine: engine):
    global _desiredSpeed
    if engine.highway == 0:
        engine.setSpeed(_desiredSpeed)
    else:
        engine.setSpeed(200)
    engine.highway += 1

def stateCallback_highway(engine: engine):
    # engine.setLastSign("highway")
    params = {FORBIDEN_STATES: [States.HIGHWAY_ENTRY]}
    engine.setState(States.FOLLOW_LINE, params)