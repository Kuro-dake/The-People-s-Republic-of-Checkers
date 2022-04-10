from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from PositionQueryHandler import PositionQueryHandler
from Database import Database
from Server.GameServer import GameServer
import pickle

import cgi

import json
class RequestHandler(BaseHTTPRequestHandler):

    game_server = GameServer()

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length),keep_blank_values=1)
        else:
            postvars = {}

        self.game_server.handle_request(postvars)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps({"result_code" : 1}), "utf-8"))

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

