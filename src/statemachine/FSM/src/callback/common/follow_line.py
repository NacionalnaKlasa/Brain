from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem, SpeedMotor, SteerMotor

def follow_line(engine: engine):
    angle = engine.getCalculatedAngle()
    if angle is not None:
        engine.setAngle(angle)