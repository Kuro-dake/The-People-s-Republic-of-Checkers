"""
The main Client script to run/compile

installed dependencies:
 pygame
 requests

(might have forgotten something, please let me know if you have to install any python module to make this thing
 executable)
"""
import common.dbprovider
from client.game import Game

import pygame

game = Game()
common.dbprovider.DBProvider.init(game, True)
game.main()

pygame.quit()
