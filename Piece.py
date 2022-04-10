from __future__ import annotations
from Square import Square
from Vector2 import Vector2
import Database

import math

class Piece(object):
    """A pawn object that stores its position and state"""

    def __init__(self, pos: Vector2, bottom_side: bool, piece_id: int, state: bool):
        # position on board
        self.position: Vector2 = pos
        # piece starts on the bottom of the board.
        self.bottom_side = bottom_side
        self.piece_id = piece_id
        # man or king
        self.is_king = state

    # create a piece filled with a record from the DB
    @staticmethod
    def create_from_db_object(dbr):
        return Piece(Vector2(dbr[1], dbr[2]), dbr[3] == 1, dbr[0], dbr[4] == 1)

    # figure out if we can move the piece to the specified position
    # we check for forward only movement, and if the position we are moving to
    # is empty
    def can_move_to_man_constraints(self, target_position: Vector2, pieces_in_direction: Piece[int], piece_side: bool):

        diff = self.position - target_position
        if not diff.is_diagonal:
            return False
        # print("isf {0}".format(Square.is_square_forward(self.position, target_position, self.bottom_side)))
        # print("len {0}".format((diff.size.x == 1 or diff.size.x == 2 and len(pieces_in_direction) == 1)))

        piece_to_skip: Piece = None

        if len(pieces_in_direction) == 1:
            piece_to_skip = pieces_in_direction[0]

        skipping = diff.size.x == 2 and piece_to_skip is not None and piece_to_skip.bottom_side != piece_side

        if skipping:
            return True

        ret: bool = Square.is_square_forward(self.position, target_position, self.bottom_side)
        ret &= diff.size.x == 1


        # print("ret {0}".format(ret))
        return ret




    # move by a specified vector
    def move_by(self, by: Vector2):
        self.position += by

    # get the partial query string for database values
    @property
    def insert_query(self):
        return "({0},{1},{2},{3},{4})" \
            .format(self.piece_id
                    , self.position.x
                    , self.position.y
                    , 1 if self.bottom_side else 0
                    , 1 if self.is_king else 0)

    def __repr__(self):
        return "Piece(#{0}:{1}: side {2})".format(self.piece_id, Square.vector2_to_position_query(self.position), self.bottom_side)

    def __eq__(self, other: Piece):
        if other is None:
            return self is None

        if type(other) is not Piece:
            raise Exception("Comparing Piece with '{0}' is not supported".format(type(other)))

        return self.piece_id == other.piece_id
