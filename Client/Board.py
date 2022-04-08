from Database import  Database
from Square import Square
from Vector2 import Vector2
from Piece import Piece
import pygame

class Board(object):

    square_size = 100

    def __init__(self, square_size):
        self.board_size = Database.board_size
        self.db = Database()
        self._selected_piece = None
        self.screen = pygame.display.set_mode((self.board_size * Board.square_size, self.board_size * Board.square_size))
        pygame.display.set_caption("People's republic of checkers")

    def draw_board(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])

        mouse_square = self.get_square_position(mouse_pos.x, mouse_pos.y)

        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                pos: Vector2 = Vector2(x, y)
                color = Board.BLACK
                if mouse_square == pos:
                    color = Board.BLUE
                if not Square.is_playable(pos):
                    color = Board.WHITE

                pygame.draw.rect(self.screen
                                 , color
                                 , [x * Board.square_size, self.board_size * Board.square_size - (y + 1) * Board.square_size,
                                    Board.square_size, Board.square_size], 0)

        piece: Piece

        for piece in self.db.get_all_pieces():
            color = Board.RED if piece.bottom_side else Board.GREEN
            if piece == self.selected_piece:
                color = Board.YELLOW
            pygame.draw.ellipse(self.screen, color, self.piece_coordinates(piece.position), 0)

    def piece_coordinates(self, position: Vector2):
        width = 80
        height = 50
        return [(position.x - 1) * Board.square_size + (Board.square_size - width) / 2
            , (Board.square_size * self.board_size) - position.y * Board.square_size + (Board.square_size - height) / 2
            , width
            , height]

    @staticmethod
    def get_square_position(mouse_x: int, mouse_y: int):
        x: int = int(mouse_x / Board.square_size)
        y: int = Database.board_size - int(mouse_y / Board.square_size) - 1
        return Vector2(x, y)

    @staticmethod
    def translate_to_db_coordinates(pos: Vector2)-> Vector2:
        return pos + Vector2(1, 1)

    def get_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        return self.db.get_piece_at(self.translate_to_db_coordinates(self.get_square_position(mouse_x, mouse_y)))

    def select_piece_at_mouse_pos(self, mouse_x: int, mouse_y: int):
        self.select_piece(self.get_piece_at_mouse_pos(mouse_x, mouse_y))

    def select_piece(self, piece: Piece):
        self._selected_piece = piece

    @property
    def selected_piece(self):
        return self._selected_piece

    BLACK = (0,0,0)
    WHITE = (255,255,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    YELLOW = (255,255,0)
