import pymongo
from pymongo import MongoClient

from ingestion import config
from ingestion import util

username = None
password = None
if "username" in config.database and "password" in config.database:
    username = config.database["username"]
    password = config.database["password"]

MONGO_CLIENT = MongoClient(
    config.database["host"],
    config.database["port"],
    username=username,
    password=password,
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
    return list(coins)


def get_latest(collection):
    docs = MONGO_DB[collection].aggregate([
        {"$sort": { "date": pymongo.DESCENDING}},
        {"$group": {"_id": "$coin_id", "date": {'$first': '$date'}}}
    ], allowDiskUse=True)

    return cursor_to_dict(docs)


def insert(collection, items):
    MONGO_DB[collection].insert(items)


def next_sequence_id(name):
    ret = MONGO_DB["seq_counters"].find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER)

    return ret["seq"]


def create_indexes():
    # TODO: is there any way to use HASHED on symbol, is it faster

    MONGO_DB.coins.create_index([("cmc_id", pymongo.ASCENDING)], unique=True)
    MONGO_DB.prices.create_index([("coin_id", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
    MONGO_DB.social_stats.create_index([("coin_id", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
