from Database import Database
from PositionQueryHandler import PositionQueryHandler
from Piece import Piece
from Square import Square, InvalidPositionQueryException
from Vector2 import Vector2

# this serves for development purposes so you can play the game
# by console commands
class OfflineLoop(object):

    def __init__(self):
        self.checkers_server = Database()

    @staticmethod
    def main():
        loop = OfflineLoop()
        db: Database = loop.checkers_server
        bottom_side_turn: bool = True

        pqh: PositionQueryHandler = PositionQueryHandler()

        while db.both_sides_have_pieces():

            db.console_output_board()

            move_query: str = input("{0} side turn. Input move query(e.g.A2toB3):"
                                    .format("Bottom" if bottom_side_turn else "Top"))

            result = pqh.handle(move_query)

            print(result)

            bottom_side_turn = not bottom_side_turn


