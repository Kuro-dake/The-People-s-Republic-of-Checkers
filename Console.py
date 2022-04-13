"""
A dev console version that lets you manipulate the MySQL DB of the game with move queries.
The rules are still imposed, but the player turn switching is not enforced
Also the piece colors and man/king are not visibly distinguished, so it's only usable to give you a general overview
of the board state
"""

from server.movequeryhandler import MoveQueryHandler
from server.mysqldata import MysqlData
from common.rules import RuleObserver
from common.dbprovider import DBProvider


class OfflineLoop(object):

    @staticmethod
    def main():
        db: MysqlData = MysqlData()

        DBProvider.init(db, False)

        bottom_side_turn: bool = True

        pqh: MoveQueryHandler = MoveQueryHandler(RuleObserver())

        while db.both_sides_have_pieces():

            db.console_output_board()

            move_query: str = input("{0} side turn. Input move query(e.g.A2toB3):"
                                    .format("Bottom" if bottom_side_turn else "Top"))

            result = pqh.handle(move_query)

            print(result)

            bottom_side_turn = not bottom_side_turn


OfflineLoop.main()
print("The game ended.")