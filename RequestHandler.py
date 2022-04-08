from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from PositionQueryHandler import PositionQueryHandler
from Database import Database
from Square import Square
from Vector2 import Vector2

import json
class RequestHandler(BaseHTTPRequestHandler):

    _checkers_server = Database()

    @property
    def checkers_server(self) -> Database:
        return self._checkers_server

    def do_GET(self):
        
        attr: dict = parse_qs(urlparse(self.path).query, keep_blank_values=True)
        pqh: PositionQueryHandler = PositionQueryHandler()
        reply = "no attributes provided"
        if len(attr) != 0:

            cs: Database = self.checkers_server

            if "new" in attr.keys():
                cs.new_game()

            move_query = attr["move"][0]

            reply = pqh.handle(move_query)

            self.checkers_server.console_output_board()





        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(reply, "utf-8") )

