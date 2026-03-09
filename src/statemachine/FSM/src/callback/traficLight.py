import time
from . import config

from src.statemachine.FSM.src.states import States, OBJECT_CLASSES
from src.computer_vision.signDetection.threads.config import Types, OBJECT_TYPES

from src.statemachine.FSM.src.engine import engine
from src.utils.messages.allMessages import Klem

from .config import FORBIDEN_STATES

_switchTime = 0
_lastTimeSeen = 0

_switchTimeTimeout = 1e9
_lastTimeSeenTimeout = 3e9

_switchCounter = 0
_switchCounterMin = 5

_lightParam = "light"
_lastLight = OBJECT_CLASSES[States.TRAFIC_LIGHT]

_hearbeat = 500
_lastHearbeat = 0

nextState = None

def Enter_traficLight(engine: engine):
    global _switchTime, _lastTimeSeen
    global _lightParam, _lastLight
    global _switchCounter
    global _lastHearbeat
    
    print("ENTER TRAFFIC LIGHT")
    
    light = engine.getStateParameters(_lightParam)
    if light is not None:
        print(light)
        _lastLight = light
        
    _switchTime = _lastTimeSeen = time.monotonic_ns()
    
    _switchCounter = 0
    _lastHearbeat = 0
    
def Execute_traficLight(engine: engine):
    global _switchTime, _lastTimeSeen, _switchTimeTimeout, _lastTimeSeenTimeout
    global _switchCounter, _switchCounterMin
    global _lastLight, nextState
    
    # Ako ne vidim semafor vise od 3 sekunde -> doslo je do greske -> vrati se na FOLLOW_LINE
    if time.monotonic_ns() - _lastTimeSeen > _lastTimeSeenTimeout:
        print("VRATI SE U FOLLOW LINE")
        engine.setState(States.FOLLOW_LINE)
    
    # Ako trenutni znak nije semafor nema sta da obradjujem -> return
    #   -> u suprotnom azuriraj lastTimeSeen
    sign = engine.getSign()
    if sign is not None:
        sign = sign.split()
        
        if sign[0] in OBJECT_TYPES[Types.TRAFFIC_LIGHT]:
            # print("znak je semafor :)")
            _lastTimeSeen = time.monotonic_ns()
            
            # Ako je prethodni znak isti kao trenutni azuriraj switchTime
            if _lastLight == sign[0]:
                # print("reset timer")
                _switchTime = _lastTimeSeen
                
            # Ako prethodni znak nije isti kao trenutni i ako je proslo vise od jedne sekunde i ako sam minimum 4 puta video taj isti novi znak
            #   -> Prebaci da je prethodni znak ustvari trenutni
            else:
                # print("razlicit znak", end="\r")
                if time.monotonic_ns() - _switchTime > _switchTimeTimeout and _switchCounter > _switchCounterMin:
                    
                    _lastLight = sign[0]
                    
                    _switchTime = time.monotonic_ns()
                    _switchCounter = 0
                    
                else:
                    _switchCounter += 1
        
        elif sign[0] == OBJECT_CLASSES[States.STOP_LINE]:
            nextState = States.STOP_LINE
    
    # U zavisnosti koji je prethodni znak izvrsavaj neku od sledecih funkcija
    
    if _lastLight == OBJECT_CLASSES[States.TRAFIC_LIGHT_GREEN]:
        _greenLight(engine)
        
    elif    _lastLight == OBJECT_CLASSES[States.TRAFIC_LIGHT_RED] or \
            _lastLight == OBJECT_CLASSES[States.TRAFIC_LIGHT_RED_YELLOW]:        
        _redLight(engine)
        
    elif    _lastLight == OBJECT_CLASSES[States.TRAFIC_LIGHT_YELLOW]:
        _yellowLight(engine)
        
    elif    _lastLight == OBJECT_CLASSES[States.TRAFIC_LIGHT]:
        _noLight(engine)
    
def _greenLight(engine: engine):
    global _hearbeat, _lastHearbeat, nextState
        
    if _lastHearbeat > _hearbeat:
        print("Hej, GREEN light")
    else:
        _lastHearbeat += 1
    
    params = {FORBIDEN_STATES: [States.TRAFIC_LIGHT, States.TRAFIC_LIGHT_RED, States.TRAFIC_LIGHT_GREEN, States.TRAFIC_LIGHT_RED_YELLOW, States.TRAFIC_LIGHT_YELLOW]}
    # if nextState:
    #     engine.setState(nextState, params)
    # else:
    engine.setState(States.FOLLOW_LINE, params)
    
    ### HEJJJJ OVDE URADI STA TREBA
    """
    U sustini ovde iznas gde je podesena brzina na 200 treba da me prebacis u sledece stanje
    koje ce na primer da detektuje samo STOP_LINE i kada detektuje ide u stanje STOP_LINE
    odakle on automatski prelazi u raskrsnicu i ide desno
    
    Ja bih za ovu potrebu napravio ili dodatno stanje ili jos bolja je sledeca situacija...
    
    U ovom stanju dok je zeleno svetlo postavi brzinu na 200 i ukljuci follow line,
    u isto vreme engine.getSign() proveravaj da li je dobijeni znak STOP_LINE, proveri udaljenost i 
    ako je udaljenost to i to samo predji u intersection. Mislim da je ovo najjednostavnije resenje 
    
    Znaci GREEN_LIGHT -> brzina 200 + follow_line() + getSign() -> predji u STOP_LINE
    Ako nije green light brzina je automatski 0 samo ne smes da pratis liniju (bilo bi lepo kad ne bi dobijao znak)
    
    PS. ja sam gore proveravao da li je znak SEMAFOR pa ako mozes iskoristi. Ako ne ponovo samo pozovi getSign() bilo gde u kodu
    """

def _noLight(engine: engine):
    """
    Ne bi trebalo nikad da se desi al nek postoji slucaj
    """
    global _hearbeat, _lastHearbeat
    
    if _lastHearbeat > _hearbeat:
        print("Hej, NO LIGHT light")
    else:
        _lastHearbeat += 1
        
    engine.setSpeed(0)
    
def _redLight(engine: engine):
    global _hearbeat, _lastHearbeat
    
    if _lastHearbeat > _hearbeat:
        print("Hej, RED light")
    else:
        _lastHearbeat += 1
    
    engine.setSpeed(0)
    
def _redYellowLight(engine: engine):
    global _hearbeat, _lastHearbeat
    
    # if _lastHearbeat > _hearbeat:
    #     print("Hej, RED YELLOW light", end="\r")
    # else:
    #     _lastHearbeat += 1
        
    _redLight(engine)
    
def _yellowLight(engine: engine):
    global _hearbeat, _lastHearbeat
    
    if _lastHearbeat > _hearbeat:
        print("Hej, YELLOW light")
    else:
        _lastHearbeat += 1
        
    engine.setSpeed(0)