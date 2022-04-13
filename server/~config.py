"""
Template for configuration file of the server. Create a copy named config.py
"""

DB_HOST = "localhost"
DATABASE = "checkers"
USER = ""
PASSWORD = ""

SERVER_HOST = "localhost"
SERVER_PORT = 8000

# set true if you want to debug on a single client - the client will start with only the green/top player playing
# (good for server dev/debug)
SINGLE_CLIENT_DEBUG = False
