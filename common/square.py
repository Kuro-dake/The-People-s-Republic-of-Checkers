from __future__ import annotations

from common.vector import Vector2

import common.database

class Square(object):
    """Tools for legitimizing Vector2 positions"""

    @staticmethod
    def is_playable(position: Vector2):
        return (position.x + position.y) % 2 != 0

    @staticmethod
    def is_square_forward(orig_position: Vector2, target_position: Vector2, bottom_side: bool):
        return bottom_side == (orig_position.y < target_position.y)

    @staticmethod
    def position_query_to_vector2(pos: str) -> Vector2:
        pos = Vector2.from_position_query(pos)
        board_size = common.database.Database.get().board_size
        if pos.x < 1 or pos.x > board_size or pos.y < 1 or pos.y > board_size:
            raise InvalidPositionQueryException("Invalid position query")

        return pos

    @staticmethod
    def vector2_to_position_query(pos: Vector2):
        return "{0}{1}".format(chr(int(pos.x)+64), int(pos.y))

class InvalidPositionQueryException(Exception):
    pass
