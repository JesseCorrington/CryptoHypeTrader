from pymongo import MongoClient
import pymongo
from util import *

MONGO_CLIENT = MongoClient(CONFIG["database_host"], CONFIG["database_port"])
MONGO_DB = MONGO_CLIENT["hype-db"]


# TODO: need error handling on db stuff

def cursor_to_dict(cursor, key="_id"):
    l = list(cursor)
    output = {}
    for li in l:
        output[li[key]] = li

    return output


def get_coins():
    coins = MONGO_DB.coins.find()
    return cursor_to_dict(coins)


def get_coins_with_subreddits():
    coins = MONGO_DB.coins.find({"subreddit": {"$exists": True}})
    return cursor_to_dict(coins)


def get_prices(symbol):
    return list(MONGO_DB.prices.find({"symbol": symbol}))


def get_latest(collection):
    docs = MONGO_DB[collection].aggregate([
        {"$sort": { "date": pymongo.DESCENDING}},
        {"$group": {"_id": "$symbol", "date": {'$last': '$date'}}}
    ], allowDiskUse=True)

    return cursor_to_dict(docs)


def insert(collection, items):
    MONGO_DB[collection].insert(items)


def create_indexes():
    # TODO: is there any way to used HASHED on symbol, is it faster

    MONGO_DB.prices.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
    MONGO_DB.social_stats.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
