from common.square import Square
from common.vector import Vector2
from common.piece import Piece
from common.rules import RuleObserver

import common.database

import pygame
import numpy
from pygame import Color


class Board(object):

    SQUARE_SIZE = 100

    def __init__(self, rules: RuleObserver, game):

        self.game = game
        self._selected_piece = None
        self.screen \
            = pygame.display.set_mode((
            self.board_size * Board.SQUARE_SIZE + Board.COORDS_PADDING * 2
            , self.board_size * Board.SQUARE_SIZE + Board.COORDS_PADDING * 2))
        self.font = pygame.font.SysFont("monospace", 25)
        self.rules = rules

        pygame.font.init()

    @property
    def board_size(self):
        return self.db().board_size

    @staticmethod
    def db():
        return common.database.Database.get()

    def draw_board(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])

        mouse_square = self.get_square_position(mouse_pos.x, mouse_pos.y)

        possible_moves = []
        self.screen.fill(Board.WHITE)
        if self.selected_piece is not None:
            possible_moves = self.rules.get_possible_moves(self.selected_piece)

        color = Board.RED if self.game.server_data.current_turn_bottom else Board.GREEN

        pygame.draw.rect(self.screen, color, [Board.COORDS_PADDING * .4, Board.COORDS_PADDING * .4,
                            Board.COORDS_PADDING *.25, Board.COORDS_PADDING * .25], 0)

        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                pos: Vector2 = Vector2(x, y)
                color = Board.BLACK
                if mouse_square == pos:
                    color = Board.BLUE
                if not Square.is_playable(pos):
                    color = Board.WHITE
                if self.translate_to_db_coordinates(pos) in map(lambda pm: pm.position, possible_moves):
                    color = Board.YELLOW

                screen_pos = Board.get_square_screen_position(x, y, self.board_size)

                pygame.draw.rect(self.screen
                                 , color
                                 , [screen_pos[0], screen_pos[1],
                                    Board.SQUARE_SIZE, Board.SQUARE_SIZE], 0)

        piece: Piece

        for piece in self.db().get_all_pieces():
            self.draw_piece(piece)

        self.draw_coords()

    PIECE_HEIGHT = 20

    def draw_piece(self, piece: Piece):

        color_range = Board.RED_PIECE if piece.bottom_side else Board.GREEN_PIECE

        if piece == self.selected_piece:
            color_range = Board.YELLOW_PIECE

        draw_position_core = self.piece_coordinates(piece.position)

        start_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] + Board.PIECE_HEIGHT * .5)
        end_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - Board.PIECE_HEIGHT * .5)

        start_color = color_range[0]

        end_color = color_range[1]

        step = .25

        is_king = piece.is_king

        for t in numpy.arange(0, 1, step):
            pos = start_pos.lerp(end_pos, t)
            coords = [pos.x, pos.y, draw_position_core[2], draw_position_core[3]]
            pygame.draw.ellipse(self.screen, start_color.lerp(end_color, t), coords, 0)

        if is_king:

            start_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - Board.PIECE_HEIGHT * .4)
            end_pos = pygame.Vector2(draw_position_core[0], draw_position_core[1] - Board.PIECE_HEIGHT * 1.4)

            for t in numpy.arange(0, 1, step):
                pos = start_pos.lerp(end_pos, t)
                coords = [pos.x, pos.y, draw_position_core[2], draw_position_core[3]]
                pygame.draw.ellipse(self.screen, start_color.lerp(end_color, t), coords, 0)

        start_pos = end_pos
        end_pos = start_pos + pygame.Vector2(draw_position_core[2] * .45, draw_position_core[3] * .45)

        for t in numpy.arange(0, 1, step):
            pos = start_pos.lerp(end_pos, t)
            w: float = Board.lerp(draw_position_core[2], draw_position_core[2] * .1, t)
            h: float = Board.lerp(draw_position_core[3], draw_position_core[3] * .1, t)

            coords = [pos.x, pos.y, w, h]
            pygame.draw.ellipse(self.screen, end_color.lerp(start_color, t * .3), coords, 0)

    @staticmethod
    def lerp(a, b, t):
        return (a * (1.0 - t)) + (b * t);

    def piece_coordinates(self, position: Vector2):
        width = 80
        height = 50
        pos = Board.get_square_screen_position(position.x - 1, position.y - 1, self.board_size)
        return [pos[0] + (Board.SQUARE_SIZE - width) / 2
            , pos[1] + (Board.SQUARE_SIZE - height) / 2
            , width
            , height]

    @staticmethod
    def get_square_position(mouse_x: int, mouse_y: int):
        x: int = int((mouse_x - Board.COORDS_PADDING) / Board.SQUARE_SIZE)
        y: int = Board.db().board_size - int((mouse_y - Board.COORDS_PADDING) / Board.SQUARE_SIZE) - 1
        return Vector2(x, y)

    @staticmethod
    def translate_to_db_coordinates(pos: Vector2)-> Vector2:
        return pos + Vector2(1, 1)

    @staticmethod
    def get_square_screen_position(x: int, y: int, board_size: int):
        return (Board.COORDS_PADDING + x * Board.SQUARE_SIZE,
                Board.COORDS_PADDING + board_size * Board.SQUARE_SIZE - (y + 1) * Board.SQUARE_SIZE)

    def get_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        return self.db().get_piece_at(self.translate_to_db_coordinates(self.get_square_position(mouse_x, mouse_y)))

    def select_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        self.select_piece(self.get_piece_at_mouse_pos(mouse_x, mouse_y))

    def select_piece(self, piece: Piece):
        self._selected_piece = piece

    @property
    def selected_piece(self):
        return self._selected_piece

    def draw_coords(self):
        for x in range(1, 9):
            label = self.font.render("{0}".format(chr(x+64)), 1, Board.BLACK)
            self.screen.blit(label, self.get_coord_position(x, True, False))
            self.screen.blit(label, self.get_coord_position(x, True, True))

        for y in range(1, 9):
            label = self.font.render("{0}".format(y), 1, Board.BLACK)
            self.screen.blit(label, self.get_coord_position(9-y, False, False))
            self.screen.blit(label, self.get_coord_position(9-y, False, True))


    def get_coord_position(self, dimension: int, x_dimension: bool, side: bool):
        main_dimension = (dimension - .5) * Board.SQUARE_SIZE + Board.COORDS_PADDING - Board.COORDS_FONT_SIZE * .5
        side_dimension = (Board.COORDS_PADDING - Board.COORDS_FONT_SIZE) * (-.2 if side else .4) + ((self.board_size + .5) * Board.SQUARE_SIZE if side else 0)
        x = main_dimension if x_dimension else side_dimension
        y = side_dimension if x_dimension else main_dimension
        return (x, y)

    BLACK = Color(0,0,0)
    WHITE = Color(255,255,255)

    RED_PIECE = (Color(197, 28, 26), Color(230, 137, 117))
    GREEN_PIECE = (Color(37, 158, 42), Color(137, 230, 117))
    YELLOW_PIECE = (Color(158, 150, 37), Color(217, 206, 52))

    RED = Color(255,0,0)
    GREEN = Color(0,255,0)
    BLUE = Color(0,0,255)
    YELLOW = Color(255,255,0)

    COORDS_PADDING = 40
    COORDS_FONT_SIZE = 25
