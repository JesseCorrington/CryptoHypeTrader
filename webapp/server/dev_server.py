import flask
import os
import json
import pymongo
from webapp.server import config
from bson import ObjectId
from datetime import datetime

# TODO: prob want to move database out of ingestion module, maybe

# This is just a basic dev server for easy internal testing
# Basic REST API access is provided to the database with Eve,
# and static files are hosted out of the client directory

cwd = os.path.dirname(os.path.realpath(__file__))
public_dir = cwd + "/../client"


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return int(o.timestamp() * 1000)

        return json.JSONEncoder.default(self, o)


def json_response(items, key_filter=None, filter_out=False):
    if not isinstance(items, list):
        items = list(items)

    if key_filter == None:
        return JSONEncoder().encode(items)

    filtered = []
    for item in items:
        filtered_item = {}
        filtered.append(filtered_item)

        if not filter_out:
            for key in key_filter:
                filtered_item[key] = item[key]
        else:
            for key in item:
                if key not in key_filter:
                    filtered_item[key] = item[key]

    return JSONEncoder().encode(filtered)


app = flask.Flask(__name__)

username = None
password = None
if "username" in config.database and "password" in config.database:
    username = config.database["username"]
    password = config.database["password"]


MONGO_CLIENT = pymongo.MongoClient(
    config.database["host"],
    config.database["port"],
    username=username,
    password=password,
    authSource='hype-db',
    authMechanism='SCRAM-SHA-1',
    serverSelectionTimeoutMS=3)

MONGO_DB = MONGO_CLIENT[config.database["name"]]


@app.route('/<path:path>')
def static_proxy(path):
    return flask.send_from_directory(public_dir, path)


def to_bool(s):
    return s.lower() == "true"


@app.route('/api/ingestion_tasks')
def get_tasks():
    running = flask.request.args.get("running")
    query = {}
    if running:
        query["running"] = to_bool(running)

    tasks = MONGO_DB.ingestion_tasks.find(query)
    return json_response(tasks)


@app.route('/api/coins')
def get_coins():
    coins = MONGO_DB.coins.find()
    return json_response(coins, {"cmc_id"}, True)


@app.route('/api/historic_prices')
def get_historic_prices():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = MONGO_DB.historic_prices.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    # TODO: need ways to get candle data too

    prices = list(prices)

    ret = []
    for price in prices:
        ret.append([price["date"], price["close"]])

    return json_response(ret)


@app.route('/api/historic_social_stats')
def get_historic_social_stats():
    coin_id = int(flask.request.args.get("coin_id"))

    stats = MONGO_DB.historic_social_stats.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    stats = list(stats)

    ret = []
    for s in stats:
        ret.append([s["date"], s["reddit_subscribers"]])

    return json_response(ret)

@app.route('/api/prices')
def get_prices():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = MONGO_DB.prices.find({"coin_id": coin_id})

    return json_response(prices, {"_id", "coin_id"}, True)


app.run()
