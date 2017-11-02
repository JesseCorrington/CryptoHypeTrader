from pymongo import MongoClient
import pymongo
from util import *

MONGO_CLIENT = MongoClient(CONFIG["database_host"], CONFIG["database_port"])
MONGO_DB = MONGO_CLIENT["hype-db"]

def insert_historic_social_stats(stats):
    collection = MONGO_DB.social_stats
    collection.insert(stats)


def get_coins():
    coins = MONGO_DB.coins.find()

    # convert to a mapping from symbol to dates
    coins = list(coins)
    output = {}
    for coin in coins:
        output[coin["_id"]] = coin

    return output


def get_prices(symbol):
    return list(MONGO_DB.prices.find({"symbol": symbol}))


def get_latest_prices():
    coins = MONGO_DB.prices.aggregate([
        # TODO: test by reversing the index to make sure we are getting sorted items
        #{"$sort": { "date": 1}},
        {"$group": {"_id" : "$symbol", "date": {'$last': '$date'}}}
    ])

    # convert to a mapping from symbol to dates
    coins = list(coins)
    output = {}
    for coin in coins:
        output[coin["_id"]] = coin

    return output


def insert_coin(coin):
    coin["_id"] = coin["symbol"]

    collection = MONGO_DB.coins
    collection.insert(coin)

# TODO: need error handling on db stuff

def insert_prices(prices):
    MONGO_DB.prices.insert(prices)


def create_indexes():
    # TODO: only create if they don't exist
    # TODO: add uniqueness to indexes

    # TODO: is there any way to used HASHED on symbol, is it faster

    MONGO_DB.prices.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
