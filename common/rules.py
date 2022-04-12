from __future__ import annotations
from common.piece import Piece
from common.vector import Vector2
from common.possiblemove import PossibleMove

import common.dbprovider

from enum import Enum
from typing import List


# Logic regarding the checkers rules
class RuleObserver(object):

    _instantiated: bool = False

    def __init__(self):
        if self._instantiated:
            raise Exception("Creating a second instance of RuleObserver. Unless you seriously changed"
                            " the logic, you are asking for a bad time.")
        self._instantiated = True
        # you need to create a database provider and inject it into all the places that use database
        # or just create a static method that will provide either Database or ServerData object
        self.skipped_piece: Piece = None

        # for locking the selectable piece after destroying opponent piece until end of turn
        self._locked_piece: Piece = None

    @staticmethod
    def db():
        return common.dbprovider.DBProvider.get()

    def end_turn(self):
        self._locked_piece = None

    @staticmethod
    def is_board_position(position: Vector2):
        return 0 < position.x <= RuleObserver.db().board_size and 0 < position.y <= RuleObserver.db().board_size

    def get_possible_moves(self, piece: Piece) -> List[PossibleMove]:

        directions = [Vector2(1, 1), Vector2(1, -1), Vector2(-1, 1), Vector2(-1, -1)]

        add_directions = []
        for i in range(2, self.db().board_size if piece.is_king else 3):
            for direction in directions:
                add_directions.append(direction * i)

        for added_direction in add_directions:
            directions.append(added_direction)

        moves = []
        for direction in directions:
            target_position = piece.position + direction
            if RuleObserver.is_board_position(target_position) and self.can_piece_move_to(piece, target_position):
                moves.append(PossibleMove(piece, piece.position + direction, self.skipped_piece is not None))

        return moves

    def can_piece_move_to(self, piece: Piece, to_pos: Vector2) -> bool:
        return self.determine_movability(piece, to_pos) == RuleObserver.Result.SUCCESS

    def determine_movability(self, piece: Piece, to_pos: Vector2) -> RuleObserver.Result:

        self.skipped_piece = None
        if piece is None:
            return self.Result.NONE_PIECE

        is_king: bool = piece.is_king

        diff: Vector2 = piece.position - to_pos
        if not diff.is_diagonal:
            return self.Result.NOT_DIAGONAL

        pieces_in_direction: List[Piece] = self.db().get_pieces_in_direction(piece.position, to_pos)

        if self.db().get_piece_at(to_pos) is not None:
            return self.Result.SQUARE_OCCUPIED

        if not is_king:
            if not piece.can_move_to_man_constraints(to_pos, pieces_in_direction, piece.bottom_side):
                return self.Result.WRONG_DIRECTION

        if len(pieces_in_direction) > 1:
            return self.Result.TOO_MANY_SKIPPED_PIECES

        piece_to_skip = pieces_in_direction[0] if len(pieces_in_direction) == 1 else None

        if piece_to_skip is None and self.locked_piece is not None:
            return self.Result.MUST_SKIP_WITH_LOCKED_PIECE

        if piece_to_skip is not None:
            if piece_to_skip.bottom_side == piece.bottom_side:
                return self.Result.SKIPPING_ALLIED_PIECE
            self.skipped_piece = piece_to_skip

        return self.Result.SUCCESS

    @property
    def locked_piece(self):
        return self._locked_piece

    def lock_piece(self, piece: Piece):
        self._locked_piece = piece


    def move_piece(self, piece: Piece, to_pos: Vector2):

        self.skipped_piece = None
        result = self.determine_movability(piece, to_pos)

        if result == self.Result.SUCCESS:
            if to_pos.y == self.db().board_size and piece.bottom_side \
                    or to_pos.y == 1 and not piece.bottom_side:
                piece.is_king = True
            self.db().move_piece(piece, to_pos)

            if self.skipped_piece is not None:
                self.db().destroy_piece(self.skipped_piece)
                self._locked_piece = piece

                possible_moves = self.get_possible_moves(piece)
                pm: PossibleMove
                if len(list(pm for pm in possible_moves if pm.skips)) == 0:
                    self.end_turn()


            else:
                print("none skipped, ending turn")
                self.end_turn()

        return result

    class Result(Enum):
        SUCCESS = 0
        NONE_PIECE = 1
        SQUARE_OCCUPIED = 2
        WRONG_DIRECTION = 3
        TOO_MANY_SKIPPED_PIECES = 4
        NOT_DIAGONAL = 5
        SKIPPING_ALLIED_PIECE = 6
        MUST_SKIP_WITH_LOCKED_PIECE = 7
