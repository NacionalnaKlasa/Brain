import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

from src.statemachine.FSM.src.callback.common.follow_line import follow_line

_withoutSign = 0

def stateCallbackEnter_AfterSign(engine: engine):
    global _withoutSign
    if engine.getCurrentKlem() != 30:
        engine.setKlem(30)
    if engine.getSpeed() == 0:
        engine.setSpeed(200)
    _withoutSign = 0

def stateCallback_AfterSign(engine: engine):
    global _withoutSign
    
    # FOLLOW LINE
    follow_line(engine)

    # TRANSFER TO ANOTHER STATE
    sign = engine.getSign()
    if sign is not None:
        lastSign = engine.getLastSign()
        
        signParts = sign.split()
        lastSignParts = lastSign.split()
        
        if signParts[0] == lastSignParts[0]:
            _withoutSign = 0
    else:
        _withoutSign += 1

    if _withoutSign > 1000:
        engine.setState(States.FOLLOW_LINE)