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
        self.last_server_update = 0
        self.rules: RuleObserver = RuleObserver()
        self.board: Board = None
        self.input = Input(self.board, self.rules, self)

        self.carry_on = True
        self.server_data: ServerData = None
        self.state: ClientState = ClientState.NEW

        self.server_id = None

        self.waiting_for_server = False

    def update_server_data(self, force: bool = False, data: dict = {}) -> bool:
        if pygame.time.get_ticks() - self.last_server_update > 1000 or self.last_server_update == 0 or force:
            server_response = ServerData.get_server_data(self, data)
            #if server_response is None:
            #    return False
            self.server_data = server_response if server_response is not None else self.server_data

            self.last_server_update = pygame.time.get_ticks()
            return True
        return False

    def main(self):

        #self.bottom_side = True if response["bottom_side"] == 1 else False

        vector.Vector2.initialize()

        # repeatedly send queries into game state
        while self.carry_on:

            if self.server_data is not None and self.server_id != self.server_data.server_id:
                self.reset_game()

            # --- Main event loop
            for event in pygame.event.get(pygame.QUIT):
                if event.type == pygame.QUIT:  # If user clicked close
                    self.state = ClientState.QUIT
                    self.update_server_data(force=True)
                    self.carry_on = False  # Flag that we are done so we can exit the while loop
                    break

            # if server chokes, wait for the connection to restore
            if self.waiting_for_server:
                self.update_server_data()

            elif self.state == ClientState.NEW:
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
            else:
                print("Undefined state {0} in game loop. Exitting...".format(self.state))
                self.carry_on = False
                continue

            self.clock.tick(60)

    def new_game_tick(self) -> bool:
        # start by sending the random ID created in constructor to the server
        # and assigning the side from response to this client

        self.update_server_data()

        if self.server_data is not None:

            self.bottom_side = True if self.server_data.data["assign_bottom_side"] == 1 else False
            self.server_id = self.server_data.server_id

            pygame.display.set_caption("{0}: People's republic of checkers".format("Red" if self.bottom_side else "Green"))

            self.board = Board(self.rules, self)
            self.input.board = self.board

            print("server id {0}".format(self.server_id))

            if client.Config.CLIENT_DEBUG:
                self.position_window()

            return True

        return False

    def waiting_for_second_player_tick(self) -> bool:

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

    def waiting_for_turn_tick(self) -> bool:

        ret: bool = False

        if self.update_server_data():

            if self.server_data.current_turn_bottom is not None and self.server_data.current_turn_bottom == self.bottom_side:
                print("Your turn starts.")
                ret = True
            else:
                print("Waiting for opponent to finish his turn.")

        self.board.draw_board()
        pygame.display.flip()

        return ret

    def player_turn_tick(self) -> bool:

        turn_over: bool = False

        for event in pygame.event.get():  # User did something
            if self.input.handle_input_events(event):
                turn_over = True

        self.board.draw_board()
        pygame.display.flip()

        return turn_over

    def reset_game(self):
        self.server_data = None
        self.state = ClientState.NEW

    def end_turn_cancel_further_skips(self):
        print("Forfeiting further skips, ending turn")
        self.update_server_data(True, {"force_end_turn": 1})
        self.state = ClientState.WAITING_FOR_TURN

    def position_window(self):
        position = (self.board.board_size + 1) * 100 if self.bottom_side else 10, 0

        SWP_NOMOVE = 0x0002
        SWP_NOOWNERZORDER = 0x0200
        SWP_NOSIZE = 0x0001

        hwnd = pygame.display.get_wm_info()["window"]
        windll.user32.SetWindowPos(hwnd, 0, position[0], position[1], 0, 0, SWP_NOSIZE | SWP_NOOWNERZORDER)


