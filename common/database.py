import pymongo
from pymongo import MongoClient


mongo_client = None
mongo_db = None


def init(config):
    global mongo_client, mongo_db

    username = None
    password = None
    auth_source = config["name"]

    if "username" in config and "password" in config:
        username = config["username"]
        password = config["password"]

    if "auth_source" in config:
        auth_source = config["auth_source"]

    mongo_client = MongoClient(
        config["host"],
        config["port"],
        username=username,
        password=password,
        serverSelectionTimeoutMS=3,
        authSource=auth_source
    )

    mongo_db = mongo_client[config["name"]]


def connected():
    try:
        mongo_client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        return False
    
    return True


def cursor_to_dict(cursor, key="_id"):
    l = list(cursor)
    output = {}
    for li in l:
        output[li[key]] = li

    return output


def get_coins(coin_filter=None):
    coins = mongo_db.coins.find(coin_filter)
    return list(coins)


def get_latest(collection):
    docs = mongo_db[collection].aggregate([
        {"$sort": { "date": pymongo.DESCENDING}},
        {"$group": {"_id": "$coin_id", "date": {'$first': '$date'}}}
    ], allowDiskUse=True)

    return cursor_to_dict(docs)


def insert(collection, items):
    mongo_db[collection].insert(items)


def next_sequence_id(name):
    ret = mongo_db["seq_counters"].find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER)

    return ret["seq"]


def create_date_coin_index(collection):
    mongo_db[collection].create_index([("coin_id", pymongo.ASCENDING), ("date", pymongo.ASCENDING)])


def create_indexes():
    mongo_db.coins.create_index([("cmc_id", pymongo.ASCENDING)], unique=True)
    mongo_db.ingestion_tasks.create_index([("start_time", pymongo.DESCENDING)])

    mongo_db.historical_prices.create_index([("coin_id", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)
    mongo_db.historical_social_stats.create_index([("coin_id", pymongo.ASCENDING), ("date", pymongo.DESCENDING)], unique=True)

    create_date_coin_index("prices")
    create_date_coin_index("reddit_comments")
    create_date_coin_index("reddit_stats")
    create_date_coin_index("twitter_comments")
    create_date_coin_index("cryptocompare_stats")
    create_date_coin_index("recent_comments")
