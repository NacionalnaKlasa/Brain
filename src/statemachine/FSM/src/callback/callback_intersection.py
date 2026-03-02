import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

def Enter_intersection(engine: engine):
    engine.setKlem(30)
    print("ENTER INTERSECTION")
    
def Execute_intersection(engine: engine):
    engine.setState(States.INTERSECTION_RIGHT)
    print("EXECUTE INTERSECTION")

    # GET DATA FROM LOCALIZATION OR SOMEWHERE
    
    # DATA SHOULD INCLUDE DIRECTIONS WHERE CAR SHOULD GO AT CURRENT INTERSTCTION