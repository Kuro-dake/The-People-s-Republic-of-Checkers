"""A simple class that translates a movement query (e.g.A2toB3) into a RulesObserver action"""

import common.dbprovider
from server.mysqldata import MysqlData
from common.piece import Piece
from common.square import Square, InvalidPositionQueryException
from common.vector import Vector2
from common.rules import RuleObserver

class MoveQueryHandler(object):

    def __init__(self, rules: RuleObserver):
        self.rules = rules

    MESSAGES = {
        RuleObserver.Result.SUCCESS: "Move successful",
        RuleObserver.Result.NONE_PIECE: "There is no piece at position {0}",
        RuleObserver.Result.SQUARE_OCCUPIED: "Target position {0} is already occupied",
        RuleObserver.Result.MOVING_BACK_OR_TOO_FAR: "Piece at {0} can not move to {1} - wrong direction, or too far",
        RuleObserver.Result.TOO_MANY_SKIPPED_PIECES: "More than one piece skipped",
        RuleObserver.Result.NOT_DIAGONAL: "You haven't even tried to move diagonally. What's wrong with you fool?"
    }

    @property
    def db(self):
        return common.dbprovider.DBProvider.get()

    # translates a movement query (e.g.A2toB3) into a RulesObserver action
    def handle(self, move_query: str) -> str:

        db: MysqlData = self.db

        move_query: str[int] = move_query.split("to")
        if len(move_query) != 2:
            return "Invalid movement query."

        # we can allow additional parameters in the move query for dev purposes
        # additional_params = move_query[1].split("|")
        # if len(additional_params) > 1:
        #    move_query[1] = additional_params[0]

        piece: Piece = None
        # try to parse the 'from' position
        try:
            from_pos: Vector2 = Square.position_query_to_vector2(move_query[0])
            print("from {1} {0}".format( from_pos, move_query[0]))
            piece = db.get_piece_at(from_pos)

        except InvalidPositionQueryException:
            return "Invalid 'from' position query '{0}'".format(move_query[0])

        # try to parse the 'to' position
        try:
            to_pos: Square = Square.position_query_to_vector2(move_query[1])
            print("to {1} {0}".format( to_pos, move_query[1]))
        except InvalidPositionQueryException:
            return "Invalid 'to' position query '{0}'".format(move_query[1])

        # move the piece with all the executability checks
        result = self.rules.move_piece(piece, to_pos)

        # return the move result message. include data about the skipped piece if any
        skipped: Piece = self.rules.skipped_piece

        return ("Skipped {0}\n".format(skipped) if skipped is not None else "") + self.MESSAGES[result]
