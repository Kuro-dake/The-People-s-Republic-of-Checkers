import pygame
from OfflineLoop import OfflineLoop

from Game import Game

CONSOLE_VERSION: bool = False

if CONSOLE_VERSION:
    loop = OfflineLoop()
    loop.main()
    exit()

Game().main()


# -------- Main Program Loop -----------



# Once we have exited the main program loop we can stop the game engine:
pygame.quit()