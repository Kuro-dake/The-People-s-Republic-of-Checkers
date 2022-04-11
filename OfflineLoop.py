from PositionQueryHandler import PositionQueryHandler

from DatabaseProvider import DatabaseProvider

# this serves for development purposes so you can play the game
# by console commands
class OfflineLoop(object):

    @staticmethod
    def main():
        loop = OfflineLoop()
        db = DatabaseProvider.get_database()
        bottom_side_turn: bool = True

        pqh: PositionQueryHandler = PositionQueryHandler()

        while db.both_sides_have_pieces():

            db.console_output_board()

            move_query: str = input("{0} side turn. Input move query(e.g.A2toB3):"
                                    .format("Bottom" if bottom_side_turn else "Top"))

            result = pqh.handle(move_query)

            print(result)

            bottom_side_turn = not bottom_side_turn


