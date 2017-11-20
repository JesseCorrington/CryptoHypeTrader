import flask
import os
import json
import pymongo
from webapp.server import config
from bson import ObjectId
from datetime import datetime, timedelta
from ingestion import util

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


def time_series(items, key):
    if not isinstance(items, list):
        items = list(items)

    series = []
    for item in items:
        series.append([item["date"], item[key]])

    return series


app = flask.Flask(__name__)

cfg = config.dev

username = None
password = None
if "username" in cfg["database"] and "password" in cfg["database"]:
    username = cfg["database"]["username"]
    password = cfg["database"]["password"]


MONGO_CLIENT = pymongo.MongoClient(
    cfg["database"]["host"],
    cfg["database"]["port"],
    username=username,
    password=password,
    authSource='hype-db',
    authMechanism='SCRAM-SHA-1',
    serverSelectionTimeoutMS=3)

MONGO_DB = MONGO_CLIENT[cfg["database"]["name"]]


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
    coins = list(MONGO_DB.coins.find())

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

    prices = MONGO_DB.historic_prices.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    series = time_series(prices, "close")
    return json_response(series)


@app.route('/api/historical_social_stats')
def get_historical_social_stats():
    coin_id = int(flask.request.args.get("coin_id"))

    stats = MONGO_DB.historic_social_stats.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)

    series = time_series(stats, "reddit_subscribers")
    return json_response(series)


@app.route('/api/prices')
def get_prices():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = MONGO_DB.prices.find({"coin_id": coin_id})

    series = time_series(prices, "price")
    return json_response(series)


@app.route('/api/reddit_stats')
def get_reddit_stats():
    coin_id = int(flask.request.args.get("coin_id"))

    prices = MONGO_DB.reddit_stats.find({"coin_id": coin_id})

    series = time_series(prices, "subscribers")
    return json_response(series)


# TODO: this is very slow and should be processed periodically and cached, not on demand
def coin_growth_summaries():
    now = datetime.utcnow()
    oldest = now - timedelta(days=6)

    stats = []
    coins = list(MONGO_DB.coins.find({"subreddit": {"$exists": True}}))

    all_stats = MONGO_DB.reddit_stats.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING)
    all_stats = list(all_stats)

    time_ranges = {
        "6h": timedelta(hours=6),
        "1d": timedelta(days=1),
        "3d": timedelta(days=3),
        "5d": timedelta(days=5)
    }

    for coin in coins:
        entries = [x for x in all_stats if x["coin_id"] == coin["_id"]]

        if len(entries) == 0:
            continue

        coin_stats = {"coin_id": coin["_id"]}
        stats.append(coin_stats)
        for name, time_range in time_ranges.items():
            from_date = now - time_range
            amount, percent = growth(entries, "subscribers", from_date, now)
            coin_stats[name + "_g"] = amount
            coin_stats[name + "_p"] = percent

    return stats


def growth(records, field, from_date, to_date):
    records = [x for x in records
               if from_date <= x["date"] <= to_date]

    if len(records) < 2:
        return 0, 0

    end = records[0][field]
    start = records[-1][field]

    growth_amount = end - start

    # hack to prevent division by zero
    if start == 0:
        start = 1

    growth_percent = growth_amount / start

    return growth_amount, growth_percent


app.run()
