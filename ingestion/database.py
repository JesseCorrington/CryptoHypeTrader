import pymongo
from pymongo import MongoClient

from ingestion import config

MONGO_CLIENT = MongoClient(
    config.database["host"],
    config.database["port"],
    username=config.database["username"],
    password=config.database["password"],
    serverSelectionTimeoutMS=3)

MONGO_DB = MONGO_CLIENT[config.database["name"]]


def connected():
    try:
        MONGO_CLIENT.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        return False
    
    return True


# TODO: need error handling on db stuff

def cursor_to_dict(cursor, key="_id"):
    l = list(cursor)
    output = {}
    for li in l:
        output[li[key]] = li

    return output


def get_coins(filter=None):
    coins = MONGO_DB.coins.find(filter)
    return cursor_to_dict(coins)


def get_prices(symbol):
    return list(MONGO_DB.prices.find({"symbol": symbol}))


def get_latest(collection):
    docs = MONGO_DB[collection].aggregate([
        {"$sort": { "date": pymongo.DESCENDING}},
        {"$group": {"_id": "$symbol", "date": {'$first': '$date'}}}
    ], allowDiskUse=True)

    return cursor_to_dict(docs)


def insert(collection, items):
    MONGO_DB[collection].insert(items)


def create_indexes():
    # TODO: is there any way to used HASHED on symbol, is it faster

    MONGO_DB.prices.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
    MONGO_DB.social_stats.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
