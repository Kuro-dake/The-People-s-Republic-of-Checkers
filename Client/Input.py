import pygame
from Square import Square
import Piece

from Client.Board import Board

from Database import Database
from RuleObserver import RuleObserver


class Input(object):

    def __init__(self, board: Board, rules: RuleObserver, game):
        self.board: Board = board
        self.game = game
        self.rules: RuleObserver = rules

    @property
    def db(self):
        return self.game.server_data

    def handle_input_events(self, event: pygame.event.Event) -> bool: # return value suggests if the turn is over
        if event.type == pygame.KEYDOWN:
            print(event)
        #if event.type == pygame.KEYDOWN:
         #   if event.key == 27:
          #      exit()
            #if event.key == 110:
            #    self.db.new_game()

        if event.type == pygame.MOUSEBUTTONDOWN:

            x = event.pos[0]
            y = event.pos[1]
            piece: Piece = self.board.get_piece_at_mouse_pos(x, y)

            if event.button == 3:
                self.board.select_piece(None)
                if self.rules.locked_piece is not None:
                    self.rules.end_turn()
                    self.game.end_turn_cancel_further_skips()

                return

            if piece is not None and self.rules.locked_piece is None:
                if self.game.server_data.current_turn_bottom == piece.bottom_side:
                    self.board.select_piece(piece)

            elif self.board.selected_piece is not None:
                result = self.rules.move_piece(
                    self.board.selected_piece,
                    Board.translate_to_db_coordinates(Board.get_square_position(x, y))
                )
                if result == RuleObserver.Result.SUCCESS:
                    # bool = possible moves contain skip

                    # add a condition that checks if the current piece has any more skips possible
                    # also make sure the player doesn't select any other piece this turn
                    # and that she will only execute other skip moves
                    self.board.select_piece(self.rules.locked_piece)
                    if self.rules.locked_piece is None:
                        return True

                print(result)

        return False



