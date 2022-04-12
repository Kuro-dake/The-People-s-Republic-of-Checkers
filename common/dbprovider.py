from __future__ import annotations

from typing import Union

import client.game
import common.database


class DBProvider(object):
    _inst = None
    _game: client.game.Game = None
    _initialized = False

    @staticmethod
    def init(arg):
        if DBProvider._initialized:
            raise Exception("Trying to reinitialize Database. This shouldn't be necessary.")
        if type(arg) is common.database.Database:
            DBProvider._inst = arg
        elif type(arg) is client.game.Game:
            DBProvider._game = arg
        else:
            raise Exception("Trying to initialize Database with '{0}'".format(arg))
        DBProvider._initialized = True

    @staticmethod
    def get() -> common.database.Database:
        if not DBProvider._initialized:
            raise Exception("Database was not initialized")
        if DBProvider._inst is not None:
            return DBProvider._inst
        if DBProvider._game is not None:
            return DBProvider._game.server_data
        else:
            raise Exception("No database was set.")
