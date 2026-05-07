import time

from . import config

from src.statemachine.FSM.src.states import States

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

navigation = [States.INTERSECTION_STRAIGHT, States.INTERSECTION_RIGHT, States.INTERSECTION_RIGHT, States.INTERSECTION_STRAIGHT, States.INTERSECTION_RIGHT, States.INTERSECTION_RIGHT]
# navigation = [States.INTERSECTION_RIGHT, States.INTERSECTION_RIGHT]
counterModuo = len(navigation)

counter = 0

def Enter_intersection(engine: engine):
    engine.setKlem(30)
    print("ENTER INTERSECTION")
    
def Execute_intersection(engine: engine):
    global counterModuo
    #engine.setState(States.INTERSECTION_RIGHT)
    nextState = navigation[engine.counter % counterModuo]
    engine.counter += 1
    counter = engine.counter
    
    if engine.counter == 4:
        engine.highway = 0
    
    engine.setState(nextState)
    print("EXECUTE INTERSECTION", engine.counter)

    # GET DATA FROM LOCALIZATION OR SOMEWHERE
    
    # DATA SHOULD INCLUDE DIRECTIONS WHERE CAR SHOULD GO AT CURRENT INTERSTCTION