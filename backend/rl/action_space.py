from enum import IntEnum
from typing import Dict, Any

class RLAction(IntEnum):
    CONTINUE_CURRENT_ROUTE = 0
    REPLAN = 1
    TAKE_ALTERNATE_ROUTE = 2
    BACKTRACK = 3
    APPROACH_TARGET = 4
    WAIT_AND_REASSESS = 5

ACTION_NAMES: Dict[int, str] = {
    0: "CONTINUE_CURRENT_ROUTE",
    1: "REPLAN",
    2: "TAKE_ALTERNATE_ROUTE",
    3: "BACKTRACK",
    4: "APPROACH_TARGET",
    5: "WAIT_AND_REASSESS"
}
