from pymongo import MongoClient
from util import *

MONGO_CLIENT = MongoClient(CONFIG["database_host"], CONFIG["database_port"])
MONGO_DB = MONGO_CLIENT["hype-db"]

def insert_historic_social_stats(stats):
    collection = MONGO_DB.social_stats
    collection.insert(stats)


def get_coins():
    return list(MONGO_DB.coins.find())


def insert_coin(coin):
    collection = MONGO_DB.coins
    collection.insert(coin)
