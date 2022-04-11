from __future__ import annotations
from ctypes import windll, Structure, wintypes, pointer
import os

import time
from enum import  Enum
import Vector2
import pygame
from RuleObserver import RuleObserver
from Client.Board import Board
from Database import Database
from Client.Input import Input

from Client.ClientState import ClientState

from Client.ServerData import ServerData

from Piece import Piece

import requests
import json

class Game(object):
    def __init__(self):
        pygame.init()

        self.bottom_side = None
        self.clock = pygame.time.Clock()
        self.last_server_update = 0
        self.rules: RuleObserver = RuleObserver()
        self.board: Board = None
        self.input = Input(self.board, self.rules, self)

        self.carry_on = True
        self.server_data: ServerData = None
        self.state: ClientState = ClientState.NEW

    def update_server_data(self, force: bool = False) -> bool:
        if pygame.time.get_ticks() - self.last_server_update > 1000 or self.last_server_update == 0 or force:
            self.server_data = ServerData.get_server_data(self)

            if self.server_data.game_ended:
                print("The game has ended on the server side. Quitting...")
                pygame.quit()
                exit()

            self.last_server_update = pygame.time.get_ticks()
            return True
        return False

    def main(self):
        # start by sending the random ID created in constructor to the server
        # and assigning the side from response to this client

        self.update_server_data()
        self.bottom_side = True if self.server_data.data["assign_bottom_side"] == 1 else False

        pygame.display.set_caption("{0}: People's republic of checkers".format("Red" if self.bottom_side else "Green"))

        self.state = ClientState.WAITING_FOR_SECOND_PLAYER

        self.board = Board(self.rules, self)

        position = (self.board.board_size + 1) * 100 if self.bottom_side else 10, 0

        SWP_NOMOVE = 0x0002
        SWP_NOOWNERZORDER = 0x0200
        SWP_NOSIZE = 0x0001

        hwnd = pygame.display.get_wm_info()["window"]
        windll.user32.SetWindowPos(hwnd, 0, position[0], position[1], 0, 0, SWP_NOSIZE | SWP_NOOWNERZORDER)

        self.input.board = self.board
        #self.bottom_side = True if response["bottom_side"] == 1 else False



        Vector2.Vector2.initialize()

        # The loop will carry on until the user exits the game (e.g. clicks the close button).

        # The clock will be used to control how fast the screen updates

        should_update_server_data = True

        # repeatedly send queries into game state
        while self.carry_on:
            # --- Main event loop
            for event in pygame.event.get(pygame.QUIT):
                if event.type == pygame.QUIT:  # If user clicked close
                    self.state = ClientState.QUIT
                    self.update_server_data(force=True)
                    self.carry_on = False  # Flag that we are done so we can exit the while loop

            if self.state == ClientState.WAITING_FOR_SECOND_PLAYER:
                if self.waiting_for_second_player_tick():
                    self.state = ClientState.WAITING_FOR_TURN

            # wait for 'your turn' server response, with drawn board
            elif self.state == ClientState.WAITING_FOR_TURN:
                if self.waiting_for_turn_tick():
                    self.state = ClientState.PLAYER_TURN

            elif self.state == ClientState.PLAYER_TURN:
                if self.player_turn_tick():
                    self.state = ClientState.WAITING_FOR_TURN

            self.clock.tick(60)

        # the query contains info about if the game is ready
        # when the game is ready, it will send the first response. response types representing client phases:
        # waiting for other player to connect
        # a) waiting for other player turn to end
        # your turn
        # game over

        # if game is ready, draw the board
        # wait until it's your turn
        # after your move, send request to the server with move data
        # if the server sends you TURN_OVER response, go back to a)


    def end_turn_cancel_further_skips(self):
        print("Forfeiting further skips, ending turn")
        self.state = ClientState.WAITING_FOR_TURN
        self.update_server_data(True)

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

        self.board.screen.fill(Board.WHITE)
        self.board.draw_board()
        pygame.display.flip()

        if not self.server_data.both_sides_have_pieces():
            print("game over")
            # db.new_game()
            self.carry_on = False

        return turn_over


