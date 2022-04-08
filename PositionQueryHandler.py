from typing import List, Any

from Database import Database
from Piece import Piece
from Square import Square, InvalidPositionQueryException
from Vector2 import Vector2
from PieceMover import PieceMover

class PositionQueryHandler(object):

    def __init__(self):
        self.db = Database()
        self.piece_mover = PieceMover()

    MESSAGES = {
        PieceMover.Result.SUCCESS: "Move successful",
        PieceMover.Result.NONE_PIECE: "There is no piece at position {0}",
        PieceMover.Result.SQUARE_OCCUPIED: "Target position {0} is already occupied",
        PieceMover.Result.WRONG_DIRECTION: "Piece at {0} can not move to {1} - wrong direction, or too far",
        PieceMover.Result.TOO_MANY_SKIPPED_PIECES: "More than one piece skipped"
    }

    def handle(self, move_query: str) -> str:

        db: Database = self.db

        if move_query == "exit":
            exit()
        if move_query == "newgame":
            db.new_game()
        move_query: str[int] = move_query.split("to")
        if len(move_query) != 2:
            return "Invalid movement query."

        additional_params = move_query[1].split("|")
        if len(additional_params) > 1:
            move_query[1] = additional_params[0]

        piece: Piece = None

        try:
            from_pos: Vector2 = Square.position_query_to_vector2(move_query[0])
            piece = db.get_piece_at(from_pos)

        except InvalidPositionQueryException:
            return "Invalid 'from' position query '{0}'".format(move_query[0])

        try:
            to_pos: Square = Square.position_query_to_vector2(move_query[1])
        except InvalidPositionQueryException:
            return "Invalid 'to' position query '{0}'".format(move_query[1])

        result = self.piece_mover.move_piece(piece, to_pos, "force" in additional_params)

        skipped: Piece = self.piece_mover.skipped_piece

        return ("Skipped {0}\n".format(skipped) if skipped is not None else "") + self.MESSAGES[result]
