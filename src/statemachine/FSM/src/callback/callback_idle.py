from . import config

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor

def stateCallbackEnter_idle(engine: engine):
    engine.sendMessage(Klem, "0")
    print("OMG RADI ENTER U IDLE")

def stateCallback_idle(engine):
    pass