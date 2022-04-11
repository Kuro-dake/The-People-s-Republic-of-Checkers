from __future__ import annotations

from Database import Database

import random
import time

import requests
from Client.ClientState import ClientState
from typing import Union
import json
import Client.ServerCredentials

from Square import Square

from Piece import Piece
from Vector2 import Vector2


class ServerData(Database):

    URL = "http://{0}:{1}".format(Client.ServerCredentials.HOST, Client.ServerCredentials.PORT)
    CLIENT_ID = time.time_ns() + random.randint(-10000, 10000)

    @staticmethod
    def get_server_data(game, data: dict = {}) -> ServerData:
        send = {"client_id" : ServerData.CLIENT_ID, "client_state" : str(game.state)}
        for key in data.keys():
            send[key] = data[key]
        response = requests.post(ServerData.URL, send)

        return ServerData(response.json(), game)

    def new_game(self):
        raise Exception("ServerData new_game method has no function and shouldn't be called")

    def __init__(self, response_data: dict, game):
        self.data = response_data

        #self.response_code = response_data["response_code"]

        if response_data["response_code"] != 0:
            raise Exception("Server returned a non zero response code.")

        self.game = game

        self.game_start = self._data_value("game_start", 0) == 1

        self.pieces_data: dict = self._data_value("pieces", None)

        self.pieces = []
        if self.pieces_data is not None:
            for key in self.pieces_data.keys():
                data = self.pieces_data[key]
                self.pieces.append(Piece(Vector2(data[0], data[1]), data[2], key, data[3]))

        self.board_size = self._data_value("board_size", None)

        self.current_turn_bottom: bool = self._data_value("current_turn_bottom", None)

        self.game_ended: bool = self._data_value("game_ended", 0) == 1

    def _data_value(self, key: str, default):
        return self.data[key] if key in self.data.keys() else default

    def get_all_pieces(self):
        return self.pieces

    def get_piece(self, piece_id: int) -> Piece:
        piece: Piece
        return next(piece for piece in self.get_all_pieces() if piece.piece_id == piece)

    def destroy_piece(self, piece: Piece):
        self.pieces.remove(piece)

    def move_piece(self, piece: Union[int, Piece], x_or_pos, y=None) -> bool:

        pos = self.parse_coordinates(x_or_pos, y)

        x = pos[0]
        y = pos[1]

        if type(piece) is not Piece:
            piece = self.get_piece(piece)

        move_query = "{0}to{1}".format(Square.vector2_to_position_query(piece.position), Square.vector2_to_position_query(Vector2(x, y)))

        piece.position = Vector2(x, y)

        self.get_server_data(self.game, {"move_query": move_query})

