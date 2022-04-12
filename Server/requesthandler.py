from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl
from Server.gameserver import GameServer

import cgi

import json

from profilehooks import profile

class RequestHandler(BaseHTTPRequestHandler):

    game_server = GameServer()
    @profile
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)

        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = dict(parse_qsl(
                self.rfile.read(length).decode("UTF-8"),keep_blank_values=1))

        else:
            postvars = {}

        response = self.game_server.handle_request(postvars)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self):

        reply = "Server is live"

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(reply, "utf-8") )
