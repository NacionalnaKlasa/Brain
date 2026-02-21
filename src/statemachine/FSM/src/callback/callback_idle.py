from . import config

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor

def stateCallbackEnter_idle(engine: engine):
    if engine.getCurrentKlem() != 0:
        engine.setKlem(0)


def stateCallback_idle(engine: engine):
    pass