from enum import Enum

class ClientState(Enum):
    NEW = 0
    WAITING_FOR_SECOND_PLAYER = 1
    WAITING_FOR_TURN = 2
    PLAYER_TURN = 3
