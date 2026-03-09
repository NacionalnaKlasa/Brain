import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

def stateCallbackEnter_stopLine(engine: engine):
    # engine.setSpeed(0)
    # engine.setAngle(0)
    print("ENTER STOP LINE")
    
def stateCallback_stopLine(engine: engine):
    print("EXECUTE STOP LINE")
    engine.setState(States.INTERSECTION)