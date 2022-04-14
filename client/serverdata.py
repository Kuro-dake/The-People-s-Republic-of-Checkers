"""
The method that handles server communication, and stores the server data

Basically the client equivalent of MysqlData class - a data 'storage' and manipulation
"""

from __future__ import annotations
import random
import time
import requests
import client.config
from typing import Union

from common.database import Database
from common.square import Square
from common.piece import Piece
from common.vector import Vector2


# derived from Database class - same class MysqlData is derived from
class ServerData(Database):

    URL = "http://{0}:{1}".format(client.config.HOST, client.config.PORT)
    # used to identify the client to the server.
    CLIENT_ID = time.time_ns() + random.randint(-10000, 10000)

    # send a request and return the instance of this class with the data from server
    @staticmethod
    def get_server_data(game, data: dict = {}) -> ServerData:

        send = {"client_id" : ServerData.CLIENT_ID, "client_state" : str(game.state), "server_id" : game.server_id}

        # append the extra data to the request
        for key in data.keys():
            send[key] = data[key]

        try:
            response = requests.post(ServerData.URL, send)
        except requests.exceptions.ConnectionError:
            print("server returned no value. Will try again.")
            return None

        # the game crashes with invalid json response. once again not worth investing more time into handling this error
        # try:
        return ServerData(response.json(), game)
        # except requests.exceptions.JSONDecodeError:
        #    print("There was an error parsing the server response. Will try again.")
        #    return None

    def __init__(self, response_data: dict, game):
        """

        @param response_data: Raw data from response
        @param game: the main instance of the Game class
        """
        # raw decoded json
        self.data = response_data

        self.response_code = self.__data_value("response_code", -1)

        self.game = game

        # 'game has started' flag from server
        self.game_start = self.__data_value("game_start", 0) == 1

        # the state of the board as it is currently recorded on the server
        self.pieces_data: dict = self.__data_value("pieces", None)

        # create Piece instances representing the raw data from server
        self.pieces = []
        if self.pieces_data is not None:
            for key in self.pieces_data.keys():
                data = self.pieces_data[key]
                self.pieces.append(Piece(Vector2(data[0], data[1]), data[2], key, data[3]))

        # use a board size according to server setting
        self.board_size = self.__data_value("board_size", None)

        # which side's turn it is
        self.current_turn_bottom: bool = self.__data_value("current_turn_bottom", None)

        # the server's game id, used for syncing the games
        self.server_id = self.data["server_id"]

    # a shortcut to fill ServerData variable
    def __data_value(self, key: str, default):
        return self.data[key] if key in self.data.keys() else default

    # following methods should be self-explanatory
    def get_all_pieces(self):
        return self.pieces

    def get_piece(self, piece_id: int) -> Piece:
        piece: Piece
        return next(piece for piece in self.get_all_pieces() if piece.piece_id == piece)

    def destroy_piece(self, piece: Piece):
        self.pieces.remove(piece)

    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:

        pos = Database.parse_coordinates(x_or_pos, y)

        x = pos[0]
        y = pos[1]

        if type(piece) is not Piece:
            piece = self.get_piece(piece)

        # create a movement query (e.g. A2toB3) and send it to the server
        move_query = "{0}to{1}".format(Square.vector2_to_position_query(piece.position), Square.vector2_to_position_query(Vector2(x, y)))

        self.get_server_data(self.game, {"move_query": move_query})

        # update local piece data since we don't update server data until player turn is finished
        piece.position = Vector2(x, y)



