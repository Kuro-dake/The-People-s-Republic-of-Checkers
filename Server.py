"""
The main Server script to run

installed dependencies:
 mysql-connector-python
 requests

(might have forgotten something, please let me know if you have to install any python module to make this thing
 executable)
"""
from http.server import HTTPServer
from server.requesthandler import RequestHandler
from server.mysqldata import MysqlData
import common.dbprovider
from server import config


common.dbprovider.DBProvider.init(MysqlData(), False)

hostName = config.SERVER_HOST
serverPort = config.SERVER_PORT

webServer = HTTPServer((hostName, serverPort), RequestHandler)

print("server started")

webServer.serve_forever()

