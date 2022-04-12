from __future__ import annotations
import random
import time
import requests
import client.config

from typing import Union

import sys
from pathlib import Path

sys.path.append(str(Path('.').absolute().parent))

from common.database import Database
from common.square import Square
from common.piece import Piece
from common.vector import Vector2


class ServerData(Database):

    URL = "http://{0}:{1}".format(client.Config.HOST, client.Config.PORT)
    CLIENT_ID = time.time_ns() + random.randint(-10000, 10000)

    @staticmethod
    def get_server_data(game, data: dict = {}) -> ServerData:
        send = {"client_id" : ServerData.CLIENT_ID, "client_state" : str(game.state), "server_id" : game.server_id}
        game.waiting_for_server = True
        for key in data.keys():
            send[key] = data[key]

        try:
            response = requests.post(ServerData.URL, send)
        except requests.exceptions.ConnectionError:
            print("Server returned no value. Will try again.")
            return None

        game.waiting_for_server = False
        #try:
        return ServerData(response.json(), game)
        #except requests.exceptions.JSONDecodeError:
        #    print("There was an error parsing the server response. Will try again.")
        #    return None

    def __init__(self, response_data: dict, game):
        self.data = response_data

        #self.response_code = response_data["response_code"]

        if response_data["response_code"] != 0:
            raise Exception("Server returned a non zero response code.")

        self.game = game

        self.game_start = self.__data_value("game_start", 0) == 1

        self.pieces_data: dict = self.__data_value("pieces", None)

        self.pieces = []
        if self.pieces_data is not None:
            for key in self.pieces_data.keys():
                data = self.pieces_data[key]
                self.pieces.append(Piece(Vector2(data[0], data[1]), data[2], key, data[3]))

        self.board_size = self.__data_value("board_size", None)

        self.current_turn_bottom: bool = self.__data_value("current_turn_bottom", None)

        self.game_ended: bool = self.__data_value("game_ended", 0) == 1

        self.server_id = self.data["server_id"]

    def __data_value(self, key: str, default):
        return self.data[key] if key in self.data.keys() else default

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

        move_query = "{0}to{1}".format(Square.vector2_to_position_query(piece.position), Square.vector2_to_position_query(Vector2(x, y)))

        self.get_server_data(self.game, {"move_query": move_query})


