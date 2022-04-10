from __future__ import annotations

import time
from enum import  Enum
import Vector2
import pygame
from RuleObserver import RuleObserver
from Board import Board
from Database import Database
from Input import Input

from ClientState import ClientState

from ServerData import ServerData

import requests
import json

class Game(object):
    def __init__(self):
        pygame.init()

        self.bottom_side = None
        self.clock = pygame.time.Clock()
        self.rules: RuleObserver = RuleObserver()
        self.board: Board = Board(self.rules)
        self.input = Input(self.board, self.rules)
        self.db = Database()
        self.carry_on = True
        self.server_data = None
        self.state: ClientState = ClientState.NEW
    def main(self):
        # start by sending the random ID created in constructor to the server
        # and assigning the side from response to this client

        self.server_data = ServerData.get_server_data(ClientState.NEW)

        # if you can't enter the game, shut down
        if self.server_data.response_code == -1:
            print("Server returned code -1. Shutting down")
            exit()

        print(self.server_data)
        print(self.server_data.data)

        #self.bottom_side = True if response["bottom_side"] == 1 else False

        self.state = ClientState.WAITING_FOR_SECOND_PLAYER

        Vector2.Vector2.initialize()

        # The loop will carry on until the user exits the game (e.g. clicks the close button).

        # The clock will be used to control how fast the screen updates

        # repeatedly send queries into game state
        while self.carry_on:
            # --- Main event loop
            if self.state == ClientState.WAITING_FOR_SECOND_PLAYER:
                self.waiting_for_second_player_tick()
                time.sleep(2)
            elif self.state == ClientState.WAITING_FOR_TURN:
                # wait for 'your turn' server response, with drawn board
                time.sleep(1)
            elif self.state == ClientState.PLAYER_TURN:
                self.player_turn_tick()
            #self.player_turn_tick()

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




    def waiting_for_second_player_tick(self) -> bool:
        for event in pygame.event.get():  # User did something

            if event.type == pygame.QUIT:  # If user clicked close
                self.carry_on = False  # Flag that we are done so we can exit the while loop

        self.server_data = ServerData.get_server_data(ClientState.WAITING_FOR_SECOND_PLAYER)

        if "assign_bottom_side" in self.server_data.data.keys():
            self.bottom_side = True if self.server_data.data["bottom_side"] == 1 else False
            self.state = ClientState.WAITING_FOR_TURN
            return True

        print("Waiting...")

        self.board.screen.fill(Board.WHITE)
        label = self.board.font.render("Waiting for the second player", 1, Board.BLACK)
        self.board.screen.blit(label, [10, 10])
        pygame.display.flip()

        return False

    def player_turn_tick(self):
        for event in pygame.event.get():  # User did something

            if event.type == pygame.QUIT:  # If user clicked close
                self.carry_on = False  # Flag that we are done so we can exit the while loop
            else:
                self.input.handle_input_events(event)

        self.board.screen.fill(Board.WHITE)
        self.board.draw_board()
        pygame.display.flip()

        if not self.db.both_sides_have_pieces():
            print("game over")
            # db.new_game()
            carry_on = False

        # --- Limit to 60 frames per second
        self.clock.tick(60)


