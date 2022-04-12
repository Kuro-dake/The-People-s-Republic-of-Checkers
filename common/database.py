from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Union, List
from common.square import Square
from common.vector import Vector2
from common.piece import Piece
import client.game


class Database(ABC):

    _inst: Database = None
    _game: client.game.Game = None
    _initialized = False

    @staticmethod
    def init(arg: Union[Database, client.game.Game]):
        if Database._initialized:
            raise Exception("Trying to reinitialize Database. This shouldn't be necessary.")
        if type(arg) is Database:
            Database._inst = arg
        elif type(arg) is client.game.Game:
            Database._game = arg
        else:
            raise Exception("Trying to initialize Database with '{0}'".format(arg))

        Database._initialized = True

    @staticmethod
    def get() -> Database:
        if not Database._initialized:
            raise Exception("Database was not initialized")
        if Database._inst is not None:
            return Database._inst
        if Database._game is not None:
            return Database._game.server_data
        else:
            raise Exception("No database was set.")

    board_size = None

    @abstractmethod
    def destroy_piece(self, piece: Piece):
        pass

    def get_piece_at(self, pos: Union[Vector2, str]):
        if type(pos) is str:
            pos = Square.position_query_to_vector2(pos)

        return next((p for p in self.get_all_pieces() if p.position == pos), None)

    def get_pieces_in_direction(self, position: Vector2, direction: Vector2, max_distance: int = -1):

        direction: Vector2 = direction - position

        if not direction.is_diagonal:
            raise Exception("direction dimensions have to be of same size")

        pieces: Piece[int] = self.get_all_pieces()

        positions: Vector2[int] = []

        for i in range(0, int(direction.size.x)):
            pos = position + direction.direction * (i + 1)

            positions.append(pos)

        return list(piece for piece in pieces if piece.position in positions)

    @abstractmethod
    def get_all_pieces(self) -> List[Piece]:
        pass

    @abstractmethod
    def get_piece(self, piece_id: int) -> Piece:
        pass

    @abstractmethod
    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:
        pass

    @staticmethod
    def _console_output_pieces(pieces):

        lines = []

        for y in range(1, 9):
            line = "{0}|".format(y)
            for x in range(1, 9):
                piece: Piece = next((p for p in pieces if p.position == Vector2(x, y)), None)

                line += (hex(piece.piece_id).replace("0x", "") if piece is not None
                         else "█" if Square.is_playable(Vector2(x, y)) else " ") + "|"
            line += "{0}".format(y)
            lines.append(line)

        lines = lines[::-1]

        print(" |A|B|C|D|E|F|G|H|")
        for line in lines:
            print(line)
        print(" |A|B|C|D|E|F|G|H|")

    @staticmethod
    def parse_coordinates(x_or_pos, y=None) -> (int, int):
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
