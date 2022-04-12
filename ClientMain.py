import common.dbprovider
from client.game import Game

import pygame

game = Game()

common.dbprovider.DBProvider.init(game)
game.main()

pygame.quit()
