from . import config
from src.statemachine.FSM.src.callback.common.follow_line import follow_line

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

from .config import FORBIDEN_STATES

_desiredSpeed = 200

def stateCallbackEnter_exitHighway(engine: engine):
    global _desiredSpeed
    engine.setSpeed(_desiredSpeed)

def stateCallback_exitHighway(engine: engine):
    engine.setLastSign("notHighway")
    params = {FORBIDEN_STATES: [States.HIGHWAY_EXIT, States.HIGHWAY_ENTRY]}
    engine.setState(States.FOLLOW_LINE, params)