from src.statemachine.FSM.src.states import States
from src.statemachine.FSM.src.callback import *
from src.statemachine.FSM.src.callback.config import *

transition_table = {
    States.IDLE:        [States.ERROR, States.FOLLOW_LINE],
    States.FOLLOW_LINE: [States.ERROR, States.IDLE, States.STOP],
    States.STOP:        [States.ERROR, States.IDLE, States.FOLLOW_LINE],
    States.ERROR:       [States.ERROR, States.IDLE]
}

callback_table = {
    States.IDLE:            {CALLBACK_ENTER: stateCallbackEnter_idle,                   CALLBACK_EXECUTE: stateCallback_idle},
    States.FOLLOW_LINE:     {CALLBACK_ENTER: stateCallbackEnter_followLine,             CALLBACK_EXECUTE: stateCallback_followLine},

    States.STOP:            {CALLBACK_ENTER: stateCallbackEnter_stop,                   CALLBACK_EXECUTE: stateCallback_stop},
    States.AFTER_STOP:      {CALLBACK_ENTER: stateCallbackEnter_followLineAfterStop,    CALLBACK_EXECUTE: stateCallback_followLineAfterStop},

    States.HIGHWAY:         {CALLBACK_ENTER: stateCallbackEnter_entryHighway,           CALLBACK_EXECUTE: stateCallback_highway},
    States.EXIT_HIGHWAY:    {CALLBACK_ENTER: stateCallbackEnter_exitHighway,            CALLBACK_EXECUTE: stateCallback_exitHighway},

    States.ERROR:           {CALLBACK_ENTER: stateCallbackEnter_error,                  CALLBACK_EXECUTE: stateCallback_error}
}