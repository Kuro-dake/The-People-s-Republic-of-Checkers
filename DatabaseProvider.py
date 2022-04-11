class DatabaseProvider(object):

    game = None
    database = None

    @staticmethod
    def get_database():
        if DatabaseProvider.game is not None and DatabaseProvider.database is not None:
            raise Exception("Both game and database are set. Can't decide which database to use.")
        if DatabaseProvider.game is None and DatabaseProvider.database is None:
            raise Exception("Neither database nor game is set. No database to provide.")
        if DatabaseProvider.game is not None:
            return DatabaseProvider.game.server_data
        return DatabaseProvider.database