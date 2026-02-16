from . import config

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor

def stateCallbackEnter_followLine(engine: engine):
    print("OMG STATE FOLLOW LINE")
    engine.sendMessage(Klem, "30")
    engine.sendMessage(SpeedMotor, "200")

def stateCallback_followLine(engine):
    pass