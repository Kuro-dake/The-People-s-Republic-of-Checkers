import unittest
import sys
import os

sys.path.append(os.getcwd() + '/..')

import pygame
from OfflineLoop import OfflineLoop
from DatabaseProvider import DatabaseProvider
from Client.Game import Game

CONSOLE_VERSION: bool = False

if CONSOLE_VERSION:
    loop = OfflineLoop()
    loop.main()
    exit()

game = Game()

DatabaseProvider.game = game

game.main()


# -------- Main Program Loop -----------



# Once we have exited the main program loop we can stop the game engine:
pygame.quit()