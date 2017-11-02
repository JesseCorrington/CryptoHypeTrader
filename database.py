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


def get_latest_prices():
    coins = MONGO_DB.prices.aggregate([
        # TODO: test by reversing the index to make sure we are getting sorted items
        #{"$sort": { "date": 1}},
        {"$group": {"_id" : "$symbol", "date": {'$last': '$date'}}}
    ])

    return cursor_to_dict(coins)


def get_latest_social_stats():
    coins = MONGO_DB.social_stats.aggregate([
        # TODO: test by reversing the index to make sure we are getting sorted items
        #{"$sort": { "date": 1}},
        {"$group": {"_id" : "$symbol", "date": {'$last': '$date'}}}
    ])

    return cursor_to_dict(coins)


def insert_coin(coin):
    coin["_id"] = coin["symbol"]
    MONGO_DB.coins.insert(coin)


def insert_prices(prices):
    MONGO_DB.prices.insert(prices)


def insert_social_stats(stats):
    MONGO_DB.social_stats.insert(stats)


def create_indexes():
    # TODO: is there any way to used HASHED on symbol, is it faster

    MONGO_DB.prices.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)

    MONGO_DB.social_stats.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)