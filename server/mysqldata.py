"""The class that manages the r/w to Mysql DB + some simple operations on Piece objects"""
import mysql.connector
from server import config

from typing import Union, List
from common.square import Square
from common.vector import Vector2
from common.piece import Piece
from common.database import Database




class MysqlData(Database):

    # MySQL/MariaDB table name
    _table_name = "Pieces"
    # query for creating a simple DB structure
    _deploy_queries = "CREATE TABLE {0} " \
                      "(id INT(2), x_pos INT(2), y_pos INT(2), side INT(1), state INT(1), PRIMARY KEY (id));".format(
        _table_name)

    # board size in squares
    # the game will inevitably get stuck with board sizes over 8, and it's not really something worth fixing right now
    board_size = 8

    def __init__(self):
        self.connection = mysql.connector.connect(host=config.DB_HOST,
                                                  database=config.DATABASE,
                                                  user=config.USER,
                                                  password=config.PASSWORD)

    # get the database cursor object
    @property
    def db_cursor(self):
        return self.connection.db_cursor()

    # reset the db to a new game state
    def new_game(self):

        cursor = self.db_cursor

        # create a simple DB structure if it doesn't exist
        if not MysqlData.__check_if_table_exists(cursor, self._table_name):
            print(self._deploy_queries)
            cursor.execute(self._deploy_queries)

        # place the pieces to their starting position
        pieces: List[Piece] = []
        for i in range(0, self.board_size * 2):
            bottom_side: bool = i <= self.board_size - 1
            base = (i - self.board_size) if not bottom_side else i
            x = base + 1
            y = self.board_size - 1 if not bottom_side else 1
            y += 1 if i % 2 == 0 else 0

            pieces.append(Piece(Vector2(x, y), bottom_side, i, False))

        # list of insert queries for each individual Piece
        values = list(map(lambda p: p.insert_query, pieces))

        cursor.execute("DELETE FROM {0}".format(self._table_name))
        cursor.execute("INSERT INTO {0} VALUES ".format(self._table_name) + ",".join(values))
        self.connection.commit()

    # delete a piece from DB
    def destroy_piece(self, piece: Piece):
        cursor = self.db_cursor
        query = "DELETE FROM {0} WHERE id={1}".format(self._table_name, piece.piece_id)
        print(query)
        cursor.execute(query)
        self.connection.commit()

    # get a piece at specified position
    def get_piece_at(self, pos: Union[Vector2, str]):
        """

        @param pos: either a Vector2 object, or a position query (e.g. A2)
        @return: Piece on the given position (or None if not present)
        """
        if type(pos) is str:
            pos = Square.position_query_to_vector2(pos)

        return next((p for p in self.get_all_pieces() if p.position == pos), None)

    # get all pieces from DB
    def get_all_pieces(self) -> List[Piece]:
        cursor = self.db_cursor
        cursor.execute("SELECT * FROM {0}".format(self._table_name))
        return list(map(lambda dbr: Piece.create_from_db_object(dbr), cursor.fetchall()))

    # gets DB object representations of pieces for bottom or top side
    def __get_side_pieces_db_objects(self, bottom_side: bool):
        cursor = self.db_cursor
        cursor.execute("SELECT * FROM {0} WHERE side={1}".format(self._table_name, 1 if bottom_side else 0))
        return cursor.fetchall()

    # gets Piece objects for bottom or top side
    def get_side_pieces(self, bottom_side: bool):
        return list(map(lambda p: Piece.create_from_db_object(p), self.__get_side_pieces_db_objects(bottom_side)))

    # check if the game still floats
    def both_sides_have_pieces(self):
        return len(self.__get_side_pieces_db_objects(True)) > 0 and len(self.__get_side_pieces_db_objects(False))> 0

    # get a specific Piece by it's DB id
    def get_piece(self, piece_id: int) -> Piece:
        cursor = self.db_cursor
        cursor.execute("SELECT * FROM {0} WHERE id={1}".format(self._table_name, piece_id))
        return Piece.create_from_db_object(cursor.fetchone())

    # move a specific piece to a specific position. no rule checks are done on this level
    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:

        cursor = self.db_cursor

        pos = Database.parse_coordinates(x_or_pos, y)

        x = pos[0]
        y = pos[1]

        if type(piece) is Piece:
            piece.position = Vector2(x, y)
            piece_id: int = piece.piece_id

        query = "UPDATE {0} SET x_pos={1}, y_pos={2}, state={4} WHERE id={3}"\
            .format(self._table_name, x, y, piece_id, 1 if piece.is_king else 0)
        # print(query)
        cursor.execute(query)
        self.connection.commit()

    # "what the title says"
    @staticmethod
    def __check_if_table_exists(dbcur, tablename):

        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            return True

        return False

