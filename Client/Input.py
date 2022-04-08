import pygame
from Square import Square
import Piece

from Client.Board import Board
from Database import Database

class Input(object):

    def __init__(self, board: Board):
        self.board: Board = board
        self.db: Database = Database()

    def handle_input_events(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            x = event.pos[0]
            y = event.pos[1]
            piece: Piece = self.board.get_piece_at_mouse_pos(x, y)

            if event.button == 3:
                self.board.select_piece(None)
                return

            if piece is not None:
                self.board.select_piece(piece)
            elif self.board.selected_piece is not None:
                self.db.move_piece(
                    self.board.selected_piece, Board.translate_to_db_coordinates(Board.get_square_position(x, y))
                )
                #print(Square.vector2_to_position_query(Board.translate_to_db_coordinates(Board.get_square_position(x, y))))

            self.board.select_piece_at_mouse_pos(event.pos[0], event.pos[1])



