"""
An abstract base class that handles the basic Piece data management

Used for MysqlData class on server side
and ServerData class on client side
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Union, List
from common.square import Square
from common.vector import Vector2
from common.piece import Piece

class Database(ABC):

    board_size = None
    # the following abstract methods should be self-explanatory
    @abstractmethod
    def destroy_piece(self, piece: Piece):
        pass

    @abstractmethod
    def get_all_pieces(self) -> List[Piece]:
        pass

    @abstractmethod
    def get_piece(self, piece_id: int) -> Piece:
        pass

    @abstractmethod
    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:
        pass

    def get_piece_at(self, pos: Union[Vector2, str]):
        """

        @param pos: either a Vector2 object, or a position query (e.g. A2)
        @return: Piece on the given position (or None if not present)
        """
        # translate position query to vector
        if type(pos) is str:
            pos = Square.position_query_to_vector2(pos)

        return next((p for p in self.get_all_pieces() if p.position == pos), None)

    # gets the pieces between current position and target position
    def get_pieces_in_direction(self, current_position: Vector2, target_position: Vector2):

        direction: Vector2 = target_position - current_position

        if not direction.is_diagonal:
            raise Exception("direction dimensions have to be of same size")

        pieces: List[Piece] = self.get_all_pieces()

        positions: List[Vector2] = []

        # create a list of positions from 'current_position' to 'target_position'
        for i in range(0, int(direction.size.x)):
            pos = current_position + direction.direction * (i + 1)
            positions.append(pos)

        # return all pieces of which positions are in the list created in the previous block of code
        return list(piece for piece in pieces if piece.position in positions)

    # outputting the board into the console
    def console_output_board(self) -> None:
        Database.__console_output_pieces(self.get_all_pieces())

    # outputting the board into the console
    @staticmethod
    def __console_output_pieces(pieces):

        lines = []

        # prepare piece id's or squares line by line
        for y in range(1, 9):
            # board coordinate on left side
            line = "{0}|".format(y)
            # pieces
            for x in range(1, 9):
                piece: Piece = next((p for p in pieces if p.position == Vector2(x, y)), None)

                line += (hex(piece.piece_id).replace("0x", "") if piece is not None
                         else "█" if Square.is_playable(Vector2(x, y)) else " ") + "|"
            # board coordinate on right side
            line += "{0}".format(y)
            lines.append(line)

        # swap the list order
        lines = lines[::-1]

        # print the board coordinates and the lines
        print(" |A|B|C|D|E|F|G|H|")
        for line in lines:
            print(line)
        print(" |A|B|C|D|E|F|G|H|")

    @staticmethod
    # parse the provided coordinates
    def parse_coordinates(x_or_pos, y=None) -> (int, int):
        """

        @param x_or_pos: a vector, an x coordinate, or a position query (e.g. A2)
        @param y: y position if x_or_pos contains x position
        @return:
        """
        x = x_or_pos
        if y is None:
            if type(x_or_pos) is str:

                pos: Vector2 = Square.position_query_to_vector2(x)
                x = pos.x
                y = pos.y
            elif type(x_or_pos) is Vector2:

                x = x_or_pos.x
                y = x_or_pos.y
            else:
                raise Exception("Undefined x_or_pos {0} of type {1}".format(x_or_pos, type(x_or_pos)))

        return (x, y)
