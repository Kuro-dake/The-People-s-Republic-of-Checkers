#dependencies:
# mysql-connector-python
# requests

from http.server import HTTPServer
from Server.requesthandler import RequestHandler
from Server.mysqldata import MysqlData
import common.database
from Server import Config

#TODO: rename to ServerMain
# or rename to Server, and rename ClientMain to Clien

common.database.Database.init(MysqlData())

hostName = Config.SERVER_HOST
serverPort = Config.SERVER_PORT

webServer = HTTPServer((hostName, serverPort), RequestHandler)

print("Server started")

webServer.serve_forever()

