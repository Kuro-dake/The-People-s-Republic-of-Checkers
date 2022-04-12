import common.database
from client.game import Game

import pygame

game = Game()

common.database.Database.init(game)
game.main()

pygame.quit()
