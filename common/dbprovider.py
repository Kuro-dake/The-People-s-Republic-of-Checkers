"""
A kind of a service container for providing the right type of DB, primarily for RuleObserver
(ServerData creates a new instance every time the server responds, so we need to keep track of that)
Would keep it in common.database.Database but there were lots of circular import problems
"""
class DBProvider(object):
    _inst = None
    _game = None
    _initialized = False

    @staticmethod
    def init(arg, is_game: bool):
        if DBProvider._initialized:
            raise Exception("Trying to reinitialize Database. This shouldn't be necessary.")
        if not is_game:
            DBProvider._inst = arg
        else:
            DBProvider._game = arg

        DBProvider._initialized = True

    @staticmethod
    def get():
        if not DBProvider._initialized:
            raise Exception("Database was not initialized")
        if DBProvider._inst is not None:
            return DBProvider._inst
        if DBProvider._game is not None:
            return DBProvider._game.server_data
        else:
            raise Exception("No database was set.")