from Database import Database
from Piece import Piece
from Vector2 import Vector2
from enum import Enum
from typing import List


# Logic regarding the checkers rules
class RuleObserver(object):

    def __init__(self):
        self.db = Database()
        self.skipped_piece: Piece = None


    def move_piece(self, piece: Piece, to_pos: Vector2, force_back_move: bool=False):
        self.skipped_piece = None
        if piece is None:
            return self.Result.NONE_PIECE

        pieces_in_direction: List[Piece] = self.db.get_pieces_in_direction(piece.position, to_pos)

        if self.db.get_piece_at(to_pos) is not None:
            return self.Result.SQUARE_OCCUPIED

        if not force_back_move:
            if not piece.can_move_to(to_pos, pieces_in_direction):
                self.Result.WRONG_DIRECTION

        if len(pieces_in_direction) > 1:
            return self.Result.TOO_MANY_SKIPPED_PIECES

        self.db.move_piece(piece, to_pos)

        result = self.Result.SUCCESS

        if len(pieces_in_direction) == 1:
            self.skipped_piece = pieces_in_direction[0]

        return result

    class Result(Enum):
        SUCCESS = 0
        NONE_PIECE = 1
        SQUARE_OCCUPIED = 2
        WRONG_DIRECTION = 3
        TOO_MANY_SKIPPED_PIECES = 4
