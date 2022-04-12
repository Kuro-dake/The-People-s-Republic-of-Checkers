import mysql.connector
from Server import config

from typing import Union, List
from common.square import Square
from common.vector import Vector2
from common.piece import Piece
from common.database import Database


#TODO: create a base Database class, make ServerData and this class inherit from it.
# Also rename this class to MysqlData

connection = mysql.connector.connect(host=Config.DB_HOST,
                                     database=Config.DATABASE,
                                     user=Config.USER,
                                     password=Config.PASSWORD)


class MysqlData(Database):
    """The class that manages the input to DB and DB to response operations"""

    _table_name = "Pieces"
    _deploy_queries = "CREATE TABLE {0} " \
                      "(id INT(2), x_pos INT(2), y_pos INT(2), side INT(1), state INT(1), PRIMARY KEY (id));".format(
        _table_name)

    board_size = 8

    def new_game(self):

        cursor = connection.cursor()
        if not MysqlData.__check_table_exists(cursor, self._table_name):
            print(self._deploy_queries)
            cursor.execute(self._deploy_queries)

        pieces: Piece[int] = []
        for i in range(0, self.board_size * 2):
            bottom_side: bool = i <= self.board_size - 1
            base = (i - self.board_size) if not bottom_side else i
            x = base + 1
            y = self.board_size - 1 if not bottom_side else 1
            y += 1 if i % 2 == 0 else 0

            pieces.append(Piece(Vector2(x, y), bottom_side, i, False))

        values = list(map(lambda p: p.insert_query, pieces))

        cursor.execute("DELETE FROM {0}".format(self._table_name))
        cursor.execute("INSERT INTO {0} VALUES ".format(self._table_name) + ",".join(values))
        connection.commit()

    def destroy_piece(self, piece: Piece):
        cursor = connection.cursor()
        query = "DELETE FROM {0} WHERE id={1}".format(self._table_name, piece.piece_id)
        print(query)
        cursor.execute(query)
        connection.commit()

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

        #print(list(map(lambda p: Square.vector2_to_position_query(p), positions)))

        return list(piece for piece in pieces if piece.position in positions)

    def get_all_pieces(self) -> List[Piece]:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {0}".format(self._table_name))
        return list(map(lambda dbr: Piece.create_from_db_object(dbr), cursor.fetchall()))

    # gets db objects of pieces for bottom or top side
    def __get_side_pieces_db_objects(self, bottom_side: bool):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {0} WHERE side={1}".format(self._table_name, 1 if bottom_side else 0))
        return cursor.fetchall()

    def get_side_pieces(self, bottom_side: bool):
        return list(map(lambda p: Piece.create_from_db_object(p), self.__get_side_pieces_db_objects(bottom_side)))

    def both_sides_have_pieces(self):
        return len(self.__get_side_pieces_db_objects(True)) > 0 and len(self.__get_side_pieces_db_objects(False))> 0

    def get_piece(self, piece_id: int) -> Piece:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {0} WHERE id={1}".format(self._table_name, piece_id))
        return Piece.create_from_db_object(cursor.fetchone())

    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:

        cursor = connection.cursor()

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
        connection.commit()

    def console_output_board(self) -> None:
        MysqlData._console_output_pieces(self.get_all_pieces())

    @staticmethod
    def __check_table_exists(dbcur, tablename):

        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            return True

        return False

