import pygame

from Database import Database

import Vector2

from OfflineLoop import OfflineLoop

from Client.Board import Board
from Client.Input import Input

CONSOLE_VERSION: bool = True

if CONSOLE_VERSION:
    loop = OfflineLoop()
    loop.main()
    exit()


Vector2.Vector2.initialize()
pygame.init()
board: Board = Board(100)

# The loop will carry on until the user exits the game (e.g. clicks the close button).
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
db = Database()
input = Input(board)

# -------- Main Program Loop -----------
while carryOn:
    # --- Main event loop
    for event in pygame.event.get():  # User did something

        if event.type == pygame.QUIT:  # If user clicked close
            carryOn = False  # Flag that we are done so we can exit the while loop
        else:
            input.handle_input_events(event)

        # --- Game logic should go here

        # --- Drawing code should go here
        # First, clear the screen to white.
    board.screen.fill(Board.WHITE)

    board.draw_board()




    # The you can draw different shapes and lines or add text to your background stage.
    #pygame.draw.rect(screen, RED, [55, 200, 100, 70], 0)

    #pygame.draw.ellipse(screen, BLACK, [20, 20, 250, 100], 2)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)


# Once we have exited the main program loop we can stop the game engine:
pygame.quit()