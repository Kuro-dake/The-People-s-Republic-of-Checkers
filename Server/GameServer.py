import random
import pickle
from DatabaseProvider import DatabaseProvider
from Client.ClientState import ClientState
from Piece import Piece
from Database import Database
from PositionQueryHandler import PositionQueryHandler
from RuleObserver import RuleObserver
import time
from enum import Enum

class GameServer(object):


    def __init__(self):
        # id: bottom_side pairs defining the player client ids and their sides
        self.players = {}
        self.game_started: bool = False
        self.current_turn_bottom = random.randint(0, 2) == 1
        self.move_query_handler = PositionQueryHandler(RuleObserver())
        self.game_id = None
        self.new_game()
        self.game_ended = False

    def new_game(self):
        self.players = {}
        self.game_started: bool = False
        self.current_turn_bottom = random.randint(0, 2) == 1
        self.game_ended = True
        self.game_id = time.time_ns() + random.randint(-10000, 10000)

    @property
    def rules(self) -> RuleObserver:
        return self.move_query_handler.rules

    @property
    def db(self) -> Database:
        return DatabaseProvider.get_database()

    def player_exists(self, player_id: str):
        return player_id in self.players.keys()

    def get_player_side(self, player_id: str):
        if self.player_exists(player_id):
            return self.players[player_id]
        elif len(self.players) == 0:
            self.players[player_id] = random.randint(0, 2) == 1
        elif len(self.players) == 1:
            self.players[player_id] = not list(self.players.values())[0]
        elif len(self.players) > 2:
            print(self.players)
            raise CorruptPlayerDataException("Creating a third player.")

        else:
            raise CorruptPlayerDataException("Looking for non-existing player")

        return self.players[player_id]

    def handle_request(self, parameters: dict):

        self.game_ended = False

        #print("received params {0}".format(parameters))
        client_state = ClientState[str(parameters["client_state"].replace("ClientState.", ""))]

        ret = {"response_code": 0, "board_size": self.db.board_size, "server_id" : self.game_id}

        client_id = parameters["client_id"]

        #print("client id {0} state {2} existing {1}".format(client_id, self.players, client_state))

        if (not self.player_exists(client_id)) and client_state != ClientState.NEW:
            print("Weird data. Restarting game")
            self.new_game()

        client_side_bottom = self.get_player_side(client_id) if client_state != ClientState.NEW else None

        if client_state == ClientState.NEW:
            try:
                client_side_bottom = self.get_player_side(client_id)
                ret["assign_bottom_side"] = 1 if client_side_bottom else 0
                print("Assigned player {0} to {1}".format(parameters["client_id"], "bottom" if client_side_bottom else "top"))
                # self.current_turn_bottom = client_side_bottom
                # self.get_player_side(0) # dev to create a second empty player
            except CorruptPlayerDataException:
                ret["error_message"] = "Tried to create a third player. Wiping the game."

                print("Tried to create a third player. Wiping the game.")
                self.new_game()

        elif "force_end_turn" in parameters.keys() and client_side_bottom == self.current_turn_bottom \
                and self.rules.locked_piece is not None:
            self.current_turn_bottom = not self.current_turn_bottom
            self.rules.lock_piece(None)

        elif client_state == ClientState.WAITING_FOR_SECOND_PLAYER:
            if len(self.players) == 2:
                ret["game_start"] = 1
                self.db.new_game()
                self.game_started = True
                print("Two players connected. Starting the game.")
            elif len(self.players) == 1:
                ret["game_start"] = 0
                print("One player connected. Waiting for player two.")
            elif len(self.players) == 0:
                ret["response_code"] = 1
                ret["error_message"] = "Waiting for second player while player pool is empty."
                print("An unexpected state: Waiting for second player while player pool is empty. Resetting server.")
                self.new_game()

        elif client_state == ClientState.QUIT:
            print("A player has disconnected. Ending game.")
            self.new_game()

        if self.game_started:

            #print("The game is running")

            if "move_query" in parameters.keys():
                if client_side_bottom != self.current_turn_bottom:
                    raise Exception("Trying to move a piece out of player's turn")
                move_query: str = parameters["move_query"]
                piece_pos = move_query.split("to")[0]
                piece = self.db.get_piece_at(piece_pos)
                if piece.bottom_side != client_side_bottom:
                    raise Exception("Trying to move a piece that doesn't belong to the player")
                print(self.move_query_handler.handle(move_query))
                if not self.db.both_sides_have_pieces():
                    self.new_game()
                elif self.rules.locked_piece is None:
                    self.current_turn_bottom = not self.current_turn_bottom
                    print("{0} turn starting".format("bottom" if self.current_turn_bottom else "top"))

            pieces = self.db.get_all_pieces()
            pieces_dict: dict = {}
            piece: Piece
            for piece in pieces:
                pieces_dict[piece.piece_id] = [piece.position.x, piece.position.y, piece.bottom_side, piece.is_king]

            ret["pieces"] = pieces_dict

            ret["current_turn_bottom"] = 1 if self.current_turn_bottom else 0

        return ret


class CorruptPlayerDataException(Exception):
    pass


