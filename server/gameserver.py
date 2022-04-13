"""Server side gameplay handling logic"""
from common.piece import Piece
from common.rules import RuleObserver

from server.mysqldata import MysqlData
from server.movequeryhandler import MoveQueryHandler
from client.clientstate import ClientState

import random
import time


class GameServer(object):

    def __init__(self):
        # id -> player side(top or bottom) pairs defining the player client ids and their sides
        self.players = {}

        self.game_started: bool = False

        # which player's turn is it
        self.current_turn_bottom = random.randint(0, 2) == 1

        self.move_query_handler = MoveQueryHandler(RuleObserver())

        # the id of the current game for client to keep track if another game hasn't started on the server
        self.game_id = None

        # start a new game
        self.new_game()

        self.db = MysqlData()

    # reset game values to new game state
    def new_game(self):
        self.players = {}
        self.game_started: bool = False
        self.current_turn_bottom = random.randint(0, 2) == 1

        self.game_id = time.time_ns() + random.randint(-10000, 10000)
        self.rules.lock_piece(None)

    # use a move query handler rules object since it contains skipped piece and locked piece
    @property
    def rules(self) -> RuleObserver:
        return self.move_query_handler.rules

    # does a player with provided id exist in the current game
    def player_exists(self, player_id: str):
        return player_id in self.players.keys()

    # does player with id control top or bottom side pieces.
    # if player does not exist, assign a side to it.
    # if there are already two players in the game, start a new one since there's no other way worth implementing
    # of taking care of this case
    def get_player_side(self, player_id: str):
        # if player exists return their side
        if self.player_exists(player_id):
            return self.players[player_id]
        # if there are no players yet, assign the player a random side
        elif len(self.players) == 0:
            self.players[player_id] = random.randint(0, 2) == 1
        # if there is one player ready for game already, assign the new player an opposing side
        elif len(self.players) == 1:
            self.players[player_id] = not list(self.players.values())[0]
        # if there are more than two players, throw an exception
        elif len(self.players) > 2:
            print(self.players)
            raise CorruptPlayerDataException("Creating a third player.")
        # if we got this far, it means that we are looking for a player that doesn't exist in this game anymore,
        # so we throw an exception
        else:
            raise CorruptPlayerDataException("Looking for non-existing player")

        # we return the assigned player side
        return self.players[player_id]

    # handle a request from the client
    def handle_request(self, parameters: dict):

        client_state = ClientState[str(parameters["client_state"].replace("ClientState.", ""))]

        # the object containing values that will be returned to the client
        ret = {"response_code": 0, "board_size": self.db.board_size, "server_id" : self.game_id}

        client_id = parameters["client_id"]

        # if the client that is trying to get a response doesn't have a side assigned, and it's not
        # starting a new game, wipe the game and start a new one
        # handling a state where there are three clients running is not worthwhile in this case
        if (not self.player_exists(client_id)) and client_state != ClientState.NEW:
            print("Corrupt game state. Restarting game.")
            self.new_game()

        # get the client's player side. we handle the logic for a client starting a new game in next block
        # with exception handling and sending the assigned side to the client,
        # so we don't call GameServer.get_player_side in this place
        client_side_bottom = self.get_player_side(client_id) if client_state != ClientState.NEW else None

        if client_state == ClientState.NEW:
            try:
                # assigning a side to a new player with exception handling
                client_side_bottom = self.get_player_side(client_id)
                ret["assign_bottom_side"] = 1 if client_side_bottom else 0
                print("Assigned player {0} to {1}".format(parameters["client_id"], "bottom" if client_side_bottom else "top"))
                # uncomment the next two lines if you need to dev/debug game start and first turn on single client
                # self.current_turn_bottom = client_side_bottom
                # self.get_player_side(0) # dev to create a second empty player
            except CorruptPlayerDataException:
                ret["error_message"] = "Tried to create a third player. Wiping the game."

                print("Tried to create a third player. Wiping the game.")
                self.new_game()

        # end turn if player clicked right mouse button in the client to forfeit their next move/end their turn
        # but only after skipping a piece.
        elif "force_end_turn" in parameters.keys() and client_side_bottom == self.current_turn_bottom \
                and self.rules.locked_piece is not None:
            self.current_turn_bottom = not self.current_turn_bottom
            self.rules.lock_piece(None)

        # handle the client pinging while waiting for second player to connect
        elif client_state == ClientState.WAITING_FOR_SECOND_PLAYER:
            # if there are two players connected at this point, we start the game
            if len(self.players) == 2:
                ret["game_start"] = 1
                self.db.new_game()
                self.game_started = True
                print("Two players connected. Starting the game.")
            # if there is only the current player connected, we let the client know that it has to keep waiting
            elif len(self.players) == 1:
                ret["game_start"] = 0
                print("One player connected. Waiting for player two.")
            # an unexpected state that restarts the game and shouldn't be happening ever
            elif len(self.players) == 0:
                ret["response_code"] = 1
                ret["error_message"] = "Waiting for second player while player pool is empty."
                print("An unexpected state: Waiting for second player while player pool is empty. Resetting server.")
                self.new_game()

        # restart the game if the client signalled that it is closing
        elif client_state == ClientState.QUIT:
            print("A player has disconnected. Ending game.")
            self.new_game()

        # if the game is running
        if self.game_started:

            # if there was a move query provided
            if "move_query" in parameters.keys():
                # we check if it's client's turn, and wipe the current game if it's not since
                # this shouldn't be happening ever, and denotes weird things happening on client sides
                if client_side_bottom != self.current_turn_bottom:
                    print("Trying to move a piece out of player's turn. Wiping the game.")
                    self.new_game()
                    return {}

                # parse the move query and get the 'from' piece
                move_query: str = parameters["move_query"]
                piece_pos = move_query.split("to")[0]
                piece = self.db.get_piece_at(piece_pos)
                # we check if the piece exists, and wipe the current game if it's not,
                # same as with checking current turn
                if piece is None:
                    print("Received a move query that wants to move a non existing piece. Wiping the game.")
                    self.new_game()
                    return {}

                # same for the case of the query from the client trying to move a piece that does not belong to it
                if piece.bottom_side != client_side_bottom:
                    print("Trying to move a piece that doesn't belong to the player")
                    self.new_game()
                    return {}

                # handle the move query and print the result message to server console
                print(self.move_query_handler.handle(move_query))

                # if there are no more pieces on one of the sides, the game is over, so we start a new one
                if not self.db.both_sides_have_pieces():
                    self.new_game()
                # we switch the player turn at the end of the move if there's no subsequent possible skip move
                elif self.rules.locked_piece is None:
                    self.current_turn_bottom = not self.current_turn_bottom
                    print("{0} turn starting".format("bottom" if self.current_turn_bottom else "top"))

            # get all pieces from DB so we can send the current state of the board to client for syncing
            pieces = self.db.get_all_pieces()
            pieces_dict: dict = {}
            piece: Piece
            for piece in pieces:
                pieces_dict[piece.piece_id] = [piece.position.x, piece.position.y, piece.bottom_side, piece.is_king]

            ret["pieces"] = pieces_dict

            # tell the client whose turn it is
            ret["current_turn_bottom"] = 1 if self.current_turn_bottom else 0

        return ret


# an exception that gets thrown in GameServer.get_player_side if there's an unexpected state
class CorruptPlayerDataException(Exception):
    pass


