"""
All the logic regarding the applied checkers rules
"""
from __future__ import annotations
from common.piece import Piece
from common.vector import Vector2
from common.possiblemove import PossibleMove

import common.dbprovider

from enum import Enum
from typing import List


class RuleObserver(object):

    _instantiated: bool = False

    def __init__(self):
        if self._instantiated:
            raise Exception("Creating a second instance of RuleObserver. Unless you seriously changed"
                            " the logic, you are asking for a bad time.")
        self._instantiated = True

        # we need to store the piece that was recently skipped
        self.skipped_piece: Piece = None

        # for locking the selectable piece after destroying opponent piece until end of turn
        self._locked_piece: Piece = None

    @staticmethod
    def db():
        return common.dbprovider.DBProvider.get()

    # the only thing that we need to do at the end of turn is remove the lock on the locked piece if any
    def end_turn(self):
        self._locked_piece = None

    # check if the position is in the constraints of the board size
    @staticmethod
    def is_board_position(position: Vector2):
        return 0 < position.x <= RuleObserver.db().board_size and 0 < position.y <= RuleObserver.db().board_size

    # get all the possible moves for a given piece
    def get_possible_moves(self, piece: Piece) -> List[PossibleMove]:

        # four size 1 directions in which a piece can move
        directions = [Vector2(1, 1), Vector2(1, -1), Vector2(-1, 1), Vector2(-1, -1)]

        add_directions = []
        for i in range(2, self.db().board_size if piece.is_king else 3):
            for direction in directions:
                add_directions.append(direction * i)

        # add directions up to 2 squares away only if the piece is man, add directions all the way to the side of the
        # board if the piece is king
        for added_direction in add_directions:
            directions.append(added_direction)


        moves = []
        for direction in directions:
            target_position = piece.position + direction
            # check if the position is on the board
            # check if the piece can move to a position
            if RuleObserver.is_board_position(target_position) and self.can_piece_move_to(piece, target_position):
                moves.append(PossibleMove(piece, piece.position + direction, self.skipped_piece is not None))

        return moves

    # translate the determine_movability result into a bool
    def can_piece_move_to(self, piece: Piece, to_pos: Vector2) -> bool:
        return self.determine_movability(piece, to_pos) == RuleObserver.Result.SUCCESS

    # check if the piece can move to target position, and if it can't, return the reason why
    def determine_movability(self, piece: Piece, to_pos: Vector2) -> RuleObserver.Result:

        self.skipped_piece = None
        # no piece was provided
        if piece is None:
            return self.Result.NONE_PIECE

        is_king: bool = piece.is_king

        # trying to move non-diagonally
        diff: Vector2 = piece.position - to_pos
        if not diff.is_diagonal:
            return self.Result.NOT_DIAGONAL

        # get all the pieces between piece and target position
        pieces_in_direction: List[Piece] = self.db().get_pieces_in_direction(piece.position, to_pos)

        # trying to move to an occupied square
        if self.db().get_piece_at(to_pos) is not None:
            return self.Result.SQUARE_OCCUPIED

        # apply man constraints if the piece is not king
        if not is_king:
            if not piece.can_move_to_man_constraints(to_pos, pieces_in_direction, piece.bottom_side):
                return self.Result.MOVING_BACK_OR_TOO_FAR

        # trying to skip more than one piece in one move
        if len(pieces_in_direction) > 1:
            return self.Result.TOO_MANY_SKIPPED_PIECES

        # the piece that will be skipped
        piece_to_skip = pieces_in_direction[0] if len(pieces_in_direction) == 1 else None

        # continuing the turn after skipping/destroying the first piece
        # we must make sure the player is only allowed to execute skip moves that turn
        if piece_to_skip is None and self.locked_piece is not None:
            return self.Result.MUST_SKIP_WITH_LOCKED_PIECE

        # skipping/destroying player's own pieces is not allowed
        if piece_to_skip is not None:
            if piece_to_skip.bottom_side == piece.bottom_side:
                return self.Result.SKIPPING_ALLIED_PIECE
            self.skipped_piece = piece_to_skip

        # "no reason to not execute this move"
        return self.Result.SUCCESS

    # getter for a protected property
    @property
    def locked_piece(self):
        return self._locked_piece

    # setter for a protected property
    def lock_piece(self, piece: Piece):
        self._locked_piece = piece

    # check movability and execute the move if possible
    def move_piece(self, piece: Piece, to_pos: Vector2):

        self.skipped_piece = None
        # this method sets self.skipped_piece
        can_move_result = self.determine_movability(piece, to_pos)

        if can_move_result == self.Result.SUCCESS:
            # make the piece into a king if it reached the opposite side of the board
            if to_pos.y == self.db().board_size and piece.bottom_side \
                    or to_pos.y == 1 and not piece.bottom_side:
                piece.is_king = True

            # move the piece to target position. 'piece.is_king = True' is flushed into database with this
            self.db().move_piece(piece, to_pos)

            # if we skipped a piece
            if self.skipped_piece is not None:
                self.db().destroy_piece(self.skipped_piece)
                # we lock the piece which we moved with so we can continue our turn
                self.lock_piece(piece)

                # check if there are any moves with skips available to the player with the current piece
                # and end turn if not
                possible_moves = self.get_possible_moves(piece)
                pm: PossibleMove
                if len(list(pm for pm in possible_moves if pm.skips)) == 0:
                    print("No more pieces to skip, ending turn")
                    self.end_turn()
                else:
                    print("skipped a piece, turn continues")

            # if player didn't skip any pieces their turn ends
            else:
                print("none skipped, ending turn")
                self.end_turn()

        # return the result of the move
        return can_move_result

    class Result(Enum):
        SUCCESS = 0
        # tried to move with None as piece argument
        NONE_PIECE = 1
        SQUARE_OCCUPIED = 2
        MOVING_BACK_OR_TOO_FAR = 3
        TOO_MANY_SKIPPED_PIECES = 4
        NOT_DIAGONAL = 5
        SKIPPING_ALLIED_PIECE = 6
        MUST_SKIP_WITH_LOCKED_PIECE = 7
