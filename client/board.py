"""
This class handles the drawing and game screen input to data structure conversion
"""
from common.square import Square
from common.vector import Vector2
from common.piece import Piece
from common.rules import RuleObserver

import common.dbprovider

import pygame
import numpy
from pygame import Color


class Board(object):

    def __init__(self, rules: RuleObserver, game):

        self.game = game
        # stores the piece that player has selected on screen
        self._selected_piece: Piece = None

        # calculate the screen padding for board coordinates and font size from the square size
        self.padding = Board.SQUARE_SIZE * .4
        self.font_size = Board.SQUARE_SIZE * .25

        # init display according to board size
        self.screen \
            = pygame.display.set_mode((
                self.board_size * Board.SQUARE_SIZE + self.padding * 2
                , self.board_size * Board.SQUARE_SIZE + self.padding * 2))

        # init the single font we will use throughout the entire game
        self.font = pygame.font.SysFont("monospace", 25)
        self.rules = rules

        pygame.font.init()

    @property
    # the size of the board in squares
    def board_size(self):
        return self.db().board_size

    @staticmethod
    def db():
        return common.dbprovider.DBProvider.get()

    # draws the board
    def draw_board(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])

        # the board position of the square which the mouse is currently over (for highlighting)
        mouse_square = self.get_square_position(mouse_pos.x, mouse_pos.y)

        possible_moves = []
        # draw white background
        self.screen.fill(Board.WHITE)

        # get possible moves from current state of the board
        if self.selected_piece is not None:
            possible_moves = self.rules.get_possible_moves(self.selected_piece)

        # the color for current turn indicator
        color = Board.RED if self.game.server_data.current_turn_bottom else Board.GREEN

        # draw the current turn indicator in the top left corner
        pygame.draw.rect(self.screen, color, [self.padding * .4, self.padding * .4,
                                self.padding * .25, self.padding * .25], 0)

        # draw the board square by square
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                pos: Vector2 = Vector2(x, y)

                # default color is black
                color = Board.BLACK
                # highlight the square the mouse is over
                if mouse_square == pos:
                    color = Board.BLUE
                # unplayable squares are white (pieces can only move diagonally, so it correlates with color)
                if not Square.is_playable(pos):
                    color = Board.WHITE
                # set highlight color if the square is amongst possible moves
                if self.translate_to_db_coordinates(pos) in map(lambda pm: pm.position, possible_moves):
                    color = Board.YELLOW

                # find a screen square position for drawing
                screen_pos = self.get_square_screen_position(x, y, self.board_size)

                # draw
                pygame.draw.rect(self.screen
                                 , color
                                 , [screen_pos[0], screen_pos[1],
                                    Board.SQUARE_SIZE, Board.SQUARE_SIZE], 0)

        piece: Piece
        # draw all the pieces
        for piece in self.db().get_all_pieces():
            self.draw_piece(piece)
        # draw the coordinates (e.g. 1-8, A-H for 8x8 board)
        self.__draw_coords()

    # draw a piece
    def draw_piece(self, piece: Piece):

        # the screen piece height
        piece_height = Board.SQUARE_SIZE * .2

        # get a color range for current piece side (top or bottom)
        color_range = Board.RED_PIECE if piece.bottom_side else Board.GREEN_PIECE

        # highlight the selected piece
        if piece == self.selected_piece:
            color_range = Board.YELLOW_PIECE

        # the center position for the various ellipses that will create the gradient of the final piece drawn
        draw_position_core = self.piece_coordinates(piece.position)

        # we will draw ellipses from start_pos to end_pos, one after another, creating gradient
        start_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] + piece_height * .5)
        end_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - piece_height * .5)

        # the same goes for the colors
        start_color = color_range[0]
        end_color = color_range[1]

        # how many ellipses will we draw per piece
        steps = 4
        step = .1 / steps

        # ...
        is_king = piece.is_king

        # we use linear interpolation to draw ellipses of gradient colors with 't' parameter in 0,1 range.
        for t in numpy.arange(0, 1, step):
            pos = start_pos.lerp(end_pos, t)
            coords = [pos.x, pos.y, draw_position_core[2], draw_position_core[3]]
            pygame.draw.ellipse(self.screen, start_color.lerp(end_color, t), coords, 0)

        # if the piece is king, we draw another piece on top of the first one
        if is_king:

            start_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - piece_height * .4)
            end_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - piece_height * 1.4)

            for t in numpy.arange(0, 1, step):
                pos = start_pos.lerp(end_pos, t)
                coords = [pos.x, pos.y, draw_position_core[2], draw_position_core[3]]
                pygame.draw.ellipse(self.screen, start_color.lerp(end_color, t), coords, 0)

        # we finish drawing the piece with ellipses of modified gradient on top of the piece to make it prettier
        start_pos = end_pos
        end_pos = start_pos + pygame.Vector2(draw_position_core[2] * .45, draw_position_core[3] * .45)

        for t in numpy.arange(0, 1, step):
            pos = start_pos.lerp(end_pos, t)
            w: float = Board.lerp(draw_position_core[2], draw_position_core[2] * .1, t)
            h: float = Board.lerp(draw_position_core[3], draw_position_core[3] * .1, t)

            coords = [pos.x, pos.y, w, h]
            pygame.draw.ellipse(self.screen, end_color.lerp(start_color, t * .3), coords, 0)

    # linear interpolation for a number
    @staticmethod
    def lerp(a, b, t):
        return (a * (1.0 - t)) + (b * t);

    # screen coordinates for a piece on 'position' from DB
    def piece_coordinates(self, position: Vector2):
        width = Board.SQUARE_SIZE * .8
        height = Board.SQUARE_SIZE * .5
        pos = self.get_square_screen_position(position.x - 1, position.y - 1, self.board_size)
        return [pos[0] + (Board.SQUARE_SIZE - width) / 2
            , pos[1] + (Board.SQUARE_SIZE - height) / 2
            , width
            , height]

    # screen coordinates for a square on 'position' from DB
    def get_square_position(self, mouse_x: int, mouse_y: int):
        x: int = int((mouse_x - self.padding) / Board.SQUARE_SIZE)
        y: int = Board.db().board_size - int((mouse_y - self.padding) / Board.SQUARE_SIZE) - 1
        return Vector2(x, y)

    # the database saves positions starting from 1,1 so we need to compensate for that
    @staticmethod
    def translate_to_db_coordinates(pos: Vector2)-> Vector2:
        return pos + Vector2(1, 1)

    # a formula for square screen position
    def get_square_screen_position(self, x: int, y: int, board_size: int):
        return (self.padding + x * Board.SQUARE_SIZE,
                self.padding + board_size * Board.SQUARE_SIZE - (y + 1) * Board.SQUARE_SIZE)

    # a shortcut for getting piece at mouse position
    def get_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        return self.db().get_piece_at(self.translate_to_db_coordinates(self.get_square_position(mouse_x, mouse_y)))

    # a shortcut for selecting piece at mouse position
    def select_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        self.select_piece(self.get_piece_at_mouse_pos(mouse_x, mouse_y))

    # ...
    def select_piece(self, piece: Piece):
        self._selected_piece = piece

    # a getter for protected property
    @property
    def selected_piece(self):
        return self._selected_piece

    # draw the board coordinates at board sides (e.g. 1-8 A-H for 8x8 board)
    def __draw_coords(self):
        for x in range(1, 9):
            label = self.font.render("{0}".format(chr(x+64)), 1, Board.BLACK)
            self.screen.blit(label, self.__get_coord_position(x, True, False))
            self.screen.blit(label, self.__get_coord_position(x, True, True))

        for y in range(1, 9):
            label = self.font.render("{0}".format(y), 1, Board.BLACK)
            self.screen.blit(label, self.__get_coord_position(9 - y, False, False))
            self.screen.blit(label, self.__get_coord_position(9 - y, False, True))

    # get coordinate position
    def __get_coord_position(self, dimension: int, x_dimension: bool, side: bool):

        padding = self.padding
        font_size = self.font_size

        main_dimension = (dimension - .5) * Board.SQUARE_SIZE + padding - font_size * .5
        side_dimension = (padding - font_size) * (-.2 if side else .4) + ((self.board_size + .5) * Board.SQUARE_SIZE if side else 0)
        x = main_dimension if x_dimension else side_dimension
        y = side_dimension if x_dimension else main_dimension
        return (x, y)

    # definitions for colors and color ranges

    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)

    RED = Color(255,0,0)
    GREEN = Color(0,255,0)
    BLUE = Color(0,0,255)
    YELLOW = Color(255,255,0)

    RED_PIECE = (Color(197, 28, 26), Color(230, 137, 117))
    GREEN_PIECE = (Color(37, 158, 42), Color(137, 230, 117))
    YELLOW_PIECE = (Color(158, 150, 37), Color(217, 206, 52))

    # the size of one board position on screen in pixels. Most of the other display values derive from it
    SQUARE_SIZE = 100
