"""
Handling the user mouse input during their turn
"""
import pygame
from common.piece import Piece

from client.board import Board

from common.rules import RuleObserver


class Input(object):

    def __init__(self, board: Board, rules: RuleObserver, game):
        self.board: Board = board
        self.game = game
        self.rules: RuleObserver = rules

    @property
    def db(self):
        return self.game.server_data

    def handle_input_events(self, event: pygame.event.Event) -> bool: # return value suggests if the turn is over

        if event.type == pygame.MOUSEBUTTONDOWN:

            x = event.pos[0]
            y = event.pos[1]
            # get piece at mouse position
            piece: Piece = self.board.get_piece_at_mouse_pos(x, y)

            # forfeit your turn with right mouse click, but only if you already skipped an opponent piece this turn
            if event.button == 3:
                self.board.select_piece(None)
                if self.rules.locked_piece is not None:
                    self.rules.end_turn()
                    self.game.end_turn_cancel_further_skips()

                return

            # if the player clicked on a piece, and it's the turn of the owner of the piece,
            # select it. We don't check if the piece belongs to the current player, since the
            # input (this method) is processed only during their turn
            if piece is not None and self.rules.locked_piece is None:
                if self.game.server_data.current_turn_bottom == piece.bottom_side:
                    self.board.select_piece(piece)

            # if we selected a piece before, we try to move it to the target square
            elif self.board.selected_piece is not None:
                # try to move the selected piece
                result = self.rules.move_piece(
                    self.board.selected_piece,
                    Board.translate_to_db_coordinates(self.board.get_square_position(x, y))
                )
                # if the move was successful
                if result == RuleObserver.Result.SUCCESS:
                    # RuleObserver.move_piece will have a piece locked if it skipped an opponent piece,
                    # and there are more available skips. The 'no locked piece' value is None
                    # either way we select the locked piece - either to reselect the piece we moved with
                    # or deselect it if it doesn't have more skips available
                    self.board.select_piece(self.rules.locked_piece)

                    # end turn if there was no locked piece
                    if self.rules.locked_piece is None:
                        return True

                # print the result into console, so we know why the piece didn't move if it didn't
                print(result)

        # continue the player turn loop
        return False



