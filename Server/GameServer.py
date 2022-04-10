import pickle
from Database import Database

class GameServer(object):

    _db = Database()

    def __init__(self):
        self.players = {}

    @property
    def db(self) -> Database:
        return self._db

    def handle_request(self, parameters: dict):


        pass

    def new_game(self):

        self.players = {}

        return

        dataset = ['hello', 'test']
        outputFile = 'test.data'
        fw = open(outputFile, 'wb')
        pickle.dump(dataset, fw)
        fw.close()
        # load data:


        inputFile = 'test.data'
        fd = open(inputFile, 'rb')
        dataset = pickle.load(fd)

