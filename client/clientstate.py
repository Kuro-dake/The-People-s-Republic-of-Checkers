from enum import Enum
"""
All the possible states of the client, used for communication with the server and also for managing the main game loop
"""


class ClientState(Enum):
    NEW = 0
    WAITING_FOR_SECOND_PLAYER = 1
    WAITING_FOR_TURN = 2
    PLAYER_TURN = 3

    QUIT = 4
