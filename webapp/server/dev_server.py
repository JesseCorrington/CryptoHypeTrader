import json
import os
from datetime import datetime, timedelta

import flask
import pymongo
from bson import ObjectId

from common import util, database as db
from webapp.server import config

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

    if key_filter is None:
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


def time_series(items, keys):
    if not isinstance(items, list):
        items = list(items)

    if not isinstance(keys, list):
        keys = [keys]

    series = []
    for item in items:
        entry = [item["date"]]
        for key in keys:
            entry.append(item[key])

        series.append(entry)

    return series


app = flask.Flask(__name__)

cfg = config.prod

db.init(cfg["database"])


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

    tasks = db.mongo_db.ingestion_tasks.find(query).sort("date", pymongo.DESCENDING).limit(100)
    return json_response(tasks)


@app.route('/api/coins')
def get_coins():
    coins = list(db.mongo_db.coins.find())

    id_map = util.list_to_dict(coins, "_id")

    growth_summaries = coin_growth_summaries()
    for summary in growth_summaries:
        coin = id_map[summary["coin_id"]]

        for key, value in summary.items():
            if key != "coin_id":
                coin[key] = value

    return json_response(coins)


@app.route('/api/coin_summaries')
def get_coin_summaries():
    # coin list joined with latest price and stats table
    # as well as 1, 3, and 7 day stats for growth of price and other stats
    pass


@app.route('/api/historical_prices')
def get_historical_prices():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = db.mongo_db.historical_prices.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    series = time_series(prices, ["close", "volume"])
    return json_response(series)


@app.route('/api/historical_social_stats')
def get_historical_social_stats():
    coin_id = int(flask.request.args.get("coin_id"))

    stats = db.mongo_db.historical_social_stats.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    series = time_series(stats, "reddit_subscribers")
    return json_response(series)


@app.route('/api/prices')
def get_prices():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = db.mongo_db.prices.find({"coin_id": coin_id})

    series = time_series(prices, "price")
    return json_response(series)


@app.route('/api/reddit_stats')
def get_reddit_stats():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = db.mongo_db.reddit_stats.find({"coin_id": coin_id})

    series = time_series(prices, "subscribers")
    return json_response(series)


app.run()
