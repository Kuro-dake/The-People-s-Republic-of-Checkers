"""Tools for legitimizing Vector2 positions on the board"""
from common.vector import Vector2
import common.dbprovider


class Square(object):

    # check if the square is a black square (white squares are never playable in checkers)
    @staticmethod
    def is_playable(position: Vector2):
        return (position.x + position.y) % 2 != 0

    # is the square an advance position for a given piece
    @staticmethod
    def is_square_forward(orig_position: Vector2, target_position: Vector2, bottom_side: bool):
        return bottom_side == (orig_position.y < target_position.y)

    # translate a position query (e.g. A2) to a Vector2
    @staticmethod
    def position_query_to_vector2(pos: str) -> Vector2:
        pos = Vector2.from_position_query(pos)
        board_size = common.dbprovider.DBProvider.get().board_size
        if pos.x < 1 or pos.x > board_size or pos.y < 1 or pos.y > board_size:
            raise InvalidPositionQueryException("Invalid position query")

        return pos

    # translate a Vector2 to a position query (e.g. A2)
    @staticmethod
    def vector2_to_position_query(pos: Vector2):
        return "{0}{1}".format(chr(int(pos.x)+64), int(pos.y))

# thrown when a non-position query string is provided to the Square.position_query_to_vector2 method
class InvalidPositionQueryException(Exception):
    pass
