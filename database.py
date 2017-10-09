from pymongo import MongoClient
from util import *

MONGO_CLIENT = MongoClient(CONFIG["database_host"], CONFIG["database_port"])
MONGO_DB = MONGO_CLIENT["hype-db"]