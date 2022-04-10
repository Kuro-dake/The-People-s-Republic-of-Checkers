from __future__ import annotations

from Database import Database

import random
import time

import requests
import ClientState
import json
import ServerCredentials

class ServerData(Database):

    URL = "http://{0}:{1}".format(ServerCredentials.HOST, ServerCredentials.PORT)
    CLIENT_ID = time.time_ns() + random.randint(-10000, 10000)

    @staticmethod
    def get_server_data(self, state: ClientState) -> ServerData:
        return ServerData(requests.post(ServerData.URL, {"client_id" : ServerData.CLIENT_ID, "client_state" : str(state)}).json())

    def __init__(self, response_data: dict):
        self.data = response_data
        self.response_code = response_data["response_code"]



    #def both_sides_have_pieces(self):

