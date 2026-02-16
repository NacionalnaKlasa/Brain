from src.statemachine.FSM.src.states import States
from src.statemachine.FSM.src.callback import *

transition_table = {
    States.IDLE:        [States.ERROR, States.FOLLOW_LINE],
    States.FOLLOW_LINE: [States.ERROR, States.IDLE, States.STOP],
    States.STOP:        [States.ERROR, States.IDLE, States.FOLLOW_LINE],
    States.ERROR:       [States.ERROR, States.IDLE]
}

callback_table = {
    States.IDLE:        {"enter": stateCallbackEnter_idle, "execute": stateCallback_idle},
    States.FOLLOW_LINE: {"enter": stateCallbackEnter_followLine, "execute": stateCallback_followLine},
    States.STOP:        {"enter": stateCallbackEnter_stop, "execute": stateCallback_stop},
    States.ERROR:       {"enter": stateCallbackEnter_error, "execute": stateCallback_error}
}