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
    States.IDLE:                    {CALLBACK_ENTER: stateCallbackEnter_idle,               CALLBACK_EXECUTE: stateCallback_idle},
    States.FOLLOW_LINE:             {CALLBACK_ENTER: stateCallbackEnter_followLine,         CALLBACK_EXECUTE: stateCallback_followLine},

    States.STOP:                    {CALLBACK_ENTER: stateCallbackEnter_stop,               CALLBACK_EXECUTE: stateCallback_stop},
    States.AFTER_SIGN:              {CALLBACK_ENTER: stateCallbackEnter_AfterSign,          CALLBACK_EXECUTE: stateCallback_AfterSign},

    States.HIGHWAY_ENTRY:           {CALLBACK_ENTER: stateCallbackEnter_entryHighway,       CALLBACK_EXECUTE: stateCallback_highway},
    States.HIGHWAY_EXIT:            {CALLBACK_ENTER: stateCallbackEnter_exitHighway,        CALLBACK_EXECUTE: stateCallback_exitHighway},

    States.ERROR:                   {CALLBACK_ENTER: stateCallbackEnter_error,              CALLBACK_EXECUTE: stateCallback_error},
    
    States.STOP_LINE:               {CALLBACK_ENTER: stateCallbackEnter_stopLine,           CALLBACK_EXECUTE: stateCallback_stopLine},
    
    States.INTERSECTION:            {CALLBACK_ENTER: Enter_intersection,                    CALLBACK_EXECUTE: Execute_intersection},
    States.INTERSECTION_LEFT:       {CALLBACK_ENTER: Enter_intersectionLeft,                CALLBACK_EXECUTE: Execute_intersectionLeft},
    States.INTERSECTION_RIGHT:      {CALLBACK_ENTER: Enter_intersectionRight,               CALLBACK_EXECUTE: Execute_intersectionRight},
    States.INTERSECTION_STRAIGHT:   {CALLBACK_ENTER: Enter_intersectionStraight,            CALLBACK_EXECUTE: Execute_intersectionStraight},

    States.PEDESTRIAN:              {CALLBACK_ENTER: stateCallbackEnter_pedestrian,         CALLBACK_EXECUTE: stateCallback_pedestrian},

    States.PARKING:                 {CALLBACK_ENTER: stateCallbackEnter_parking,            CALLBACK_EXECUTE: stateCallback_parking},
    
    States.TRAFIC_LIGHT:            {CALLBACK_ENTER: Enter_traficLight,                     CALLBACK_EXECUTE: Execute_traficLight},
    States.TRAFIC_LIGHT_RED:        {CALLBACK_ENTER: Enter_traficLight,                     CALLBACK_EXECUTE: Execute_traficLight},
    States.TRAFIC_LIGHT_GREEN:      {CALLBACK_ENTER: Enter_traficLight,                     CALLBACK_EXECUTE: Execute_traficLight},
    States.TRAFIC_LIGHT_YELLOW:     {CALLBACK_ENTER: Enter_traficLight,                     CALLBACK_EXECUTE: Execute_traficLight},
    States.TRAFIC_LIGHT_RED_YELLOW: {CALLBACK_ENTER: Enter_traficLight,                     CALLBACK_EXECUTE: Execute_traficLight},
}