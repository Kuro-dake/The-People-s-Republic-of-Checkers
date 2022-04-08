#dependencies:
# mysql-connector-python


from http.server import BaseHTTPRequestHandler, HTTPServer
from RequestHandler import RequestHandler
import Database

from OfflineLoop import OfflineLoop

import time, json


hostName = "localhost"
serverPort = 8000

#cs = CheckersServer()
#cs.new_game()
#print(cs.get_pieces_from_db())

#OfflineLoop.main()

#exit()

webServer = HTTPServer((hostName, serverPort), RequestHandler)
#print("Server started http://%s:%s" % (hostName, serverPort))

#try:
webServer.serve_forever()

#except KeyboardInterrupt:
#    pass

webServer.server_close()
print("Server stopped.")