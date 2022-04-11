#dependencies:
# mysql-connector-python
# requests

from http.server import HTTPServer
from Server.RequestHandler import RequestHandler
from Database import Database
from DatabaseProvider import DatabaseProvider
from Server import Config

DatabaseProvider.database = Database()

hostName = Config.SERVER_HOST
serverPort = Config.SERVER_PORT

#cs = CheckersServer()
#cs.new_game()
#print(cs.get_pieces_from_db())

#OfflineLoop.main()

#exit()



webServer = HTTPServer((hostName, serverPort), RequestHandler)

#print("Server started http://%s:%s" % (hostName, serverPort))

print("Server started")

#try:
webServer.serve_forever()

#except KeyboardInterrupt:
#    pass

webServer.server_close()
print("Server stopped.")