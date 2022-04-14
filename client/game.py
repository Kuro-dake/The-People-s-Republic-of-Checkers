"""
Contains the main loop that manages communication with server, and forwarding the game to the input when it's
player's turn
"""
from __future__ import annotations

from ctypes import windll

from common import vector
import pygame
from common.rules import RuleObserver
from client.board import Board
from client.input import Input

import client.config

from client.clientstate import ClientState

from client.serverdata import ServerData


class Game(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("initializing People's republic of checkers")
        self.bottom_side = None
        self.clock = pygame.time.Clock()
        # the time of the last server update, for delaying server updates
        self.last_server_update = 0
        self.rules: RuleObserver = RuleObserver()
        self.board: Board = None
        self.input = Input(self.board, self.rules, self)

        # the main loop 'carries on' while true
        self.carry_on = True

        # the "database" of the client, contains all the data from server regarding player turn, piece positions, etc.
        self.server_data: ServerData = None

        self.state: ClientState = ClientState.NEW

        # the id of the game on the server. used to keep track of validity of client data
        self.server_id = None

    # updates the server data and stores them for this and dependent classes to use
    def update_server_data(self, force: bool = False, data: dict = {}) -> bool:
        """

        @param force: Update even if the timeout hasn't finished running
        @param data: additional data to send to the server
        @return: True if updated else False
        """
        # make an attempt every 1000 milliseconds
        if pygame.time.get_ticks() - self.last_server_update > 1000 or self.last_server_update == 0 or force:

            # update only if we got any data from server. keep the old data otherwise
            server_response = ServerData.get_server_data(self, data)
            if server_response.response_code == -1:
                server_response = None
            self.server_data = server_response if server_response is not None else self.server_data

            # keep the track of last update
            self.last_server_update = pygame.time.get_ticks()

            return True

        return False

    # the main gameplay loop
    def main(self):

        vector.Vector2.initialize()

        # repeatedly send queries into game state
        while self.carry_on:

            # reset game if the game's server id is different from our stored server id
            if self.server_data is not None and self.server_id != self.server_data.server_id:
                self.reset_game()

            # handle clicking 'close'. dump all the other events if it's not player's turn since
            # there's an event loop in Game.player_turn_tick, and pygame stacks events every tick
            # in a stack until it's handled/popped
            for event in pygame.event.get(None if self.state != ClientState.PLAYER_TURN else pygame.QUIT):
                if event.type == pygame.QUIT:
                    self.state = ClientState.QUIT
                    # let the server know we closed the game
                    self.update_server_data(force=True)
                    # break the loop
                    self.carry_on = False
                    continue

            # waiting for the server to assign us a side
            if self.state == ClientState.NEW:
                if self.new_game_tick():
                    self.state = ClientState.WAITING_FOR_SECOND_PLAYER

            # waiting until server tells us it found a second player
            elif self.state == ClientState.WAITING_FOR_SECOND_PLAYER:
                if self.waiting_for_second_player_tick():
                    self.state = ClientState.WAITING_FOR_TURN

            # wait for 'your turn' server response, with drawn board
            elif self.state == ClientState.WAITING_FOR_TURN:
                if self.waiting_for_turn_tick():
                    self.state = ClientState.PLAYER_TURN

            # play your turn, after your move, send request to the server with move data
            elif self.state == ClientState.PLAYER_TURN:
                if self.player_turn_tick():
                    self.state = ClientState.WAITING_FOR_TURN

            # quitting the game
            elif self.state == ClientState.QUIT:
                print("Quitting the game")
                self.carry_on = False
                continue
            # undefined state
            else:
                print("Undefined state {0} in game loop. Exitting...".format(self.state))
                self.carry_on = False
                continue

            # pygame frame delay
            self.clock.tick(60)

    # wait for the server to assign the client a side
    def new_game_tick(self) -> bool:
        """

        @return: True if ready to move to next ClientState
        """
        self.update_server_data()

        if self.server_data is not None:

            if "assign_bottom_side" not in self.server_data.data.keys():
                print("Didn't get a side assigned. Will try again.")
                return False

            self.bottom_side = True if self.server_data.data["assign_bottom_side"] == 1 else False
            self.server_id = self.server_data.server_id

            pygame.display.set_caption("{0}: People's republic of checkers".format("Red" if self.bottom_side else "Green"))

            self.board = Board(self.rules, self)
            self.input.board = self.board

            print("server id {0}".format(self.server_id))

            if client.config.DEBUG:
                self.position_window()

            return True

        return False

    # wait until server tells us that a second player has connected into the game
    def waiting_for_second_player_tick(self) -> bool:
        """

        @return: True if ready to move to next ClientState
        """
        ret: bool = False

        if self.update_server_data():

            if self.server_data.game_start:
                ret = True
            else:
                print("Waiting for second player...")

            self.board.screen.fill(Board.WHITE)
            label = self.board.font.render("Waiting for the second player to connect", 1, Board.BLACK)
            self.board.screen.blit(label, [10, 10])
            pygame.display.flip()

        return ret

    # wait until the server tells us it's our turn
    def waiting_for_turn_tick(self) -> bool:
        """

        @return: True if ready to move to next ClientState
        """
        ret: bool = False

        if self.update_server_data():

            if self.server_data.current_turn_bottom is not None and self.server_data.current_turn_bottom == self.bottom_side:
                print("Your turn starts.")
                ret = True
            else:
                print("Waiting for opponent to finish their turn.")

        self.board.draw_board()
        pygame.display.flip()

        return ret

    # board control loop
    def player_turn_tick(self) -> bool:
        """

        @return: True if ready to move to next ClientState
        """
        turn_over: bool = False

        for event in pygame.event.get():  # User did something
            if self.input.handle_input_events(event):
                turn_over = True

        self.board.draw_board()
        pygame.display.flip()

        return turn_over

    # ...
    def reset_game(self):
        self.server_data = None
        self.state = ClientState.NEW

    # let the server know that you're forfeiting your option to chain skip opponent's pieces
    def end_turn_cancel_further_skips(self):
        print("Forfeiting further skips, ending turn")
        self.update_server_data(True, {"force_end_turn": 1})
        self.state = ClientState.WAITING_FOR_TURN

    # position the window for the dev purposes (when having two client instances running, it's nice to have
    # the windows next to each other, and with the same piece side on the same position)
    def position_window(self):
        position = (self.board.board_size + 1) * 100 if self.bottom_side else 10, 0

        SWP_NOMOVE = 0x0002
        SWP_NOOWNERZORDER = 0x0200
        SWP_NOSIZE = 0x0001

        hwnd = pygame.display.get_wm_info()["window"]
        windll.user32.SetWindowPos(hwnd, 0, position[0], position[1], 0, 0, SWP_NOSIZE | SWP_NOOWNERZORDER)


