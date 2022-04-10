#dependencies:
# mysql-connector-python


from http.server import HTTPServer
from Server.RequestHandler import RequestHandler

hostName = "localhost"
serverPort = 8000

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