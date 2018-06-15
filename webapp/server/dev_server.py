import json
import os, signal
from datetime import datetime

import flask
import pymongo
from bson import ObjectId

from common import database as db
from webapp.server import config

# This is just a basic dev server for easy internal testing
# Basic REST API access is provided, and static files are hosted out of the client directory
# Not safe for production use


cwd = os.path.dirname(os.path.realpath(__file__))
public_dir = cwd + "/../client"


# TODO: take out static file hosting, will host on nginx
# TODO: takeout CORS, and setup nginx properly to redirect
# https://stackoverflow.com/questions/28925304/javascript-stack-web-server-and-api-server-together-or-separate

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


# TODO: need fix this for deploy
from flask_cors import CORS
CORS(app)


@app.route('/<path:path>')
def static_proxy(path):
    if path.find(".") == -1:
        path = path + ".html"

    return flask.send_from_directory(public_dir, path)


def to_bool(s):
    return s.lower() == "true"


@app.route('/api/ingestion_tasks')
def get_tasks():
    running = flask.request.args.get("running")
    query = {}
    if running:
        query["running"] = to_bool(running)

    tasks = db.mongo_db.ingestion_tasks.find(query).sort("start_time", pymongo.DESCENDING).limit(100)

    return json_response(tasks)


@app.route('/api/ingestion_tasks/cancel/<string:id>')
def cancel_task(id):
    task = dict(db.mongo_db.ingestion_tasks.find({"id": id}))
    os.kill(task["pid"], signal.SIGKILL)


@app.route('/api/coin/<int:coin_id>')
def get_coin(coin_id):
    coin = dict(db.mongo_db.coins.find_one({"_id": coin_id}))
    if coin is not None:
        return JSONEncoder().encode(coin)
    else:
        return json_response({"error": "no coin withs id: {}".format(coin_id)})

@app.route('/api/coins')
def get_coins():
    coins = list(db.mongo_db.coins.find())
    return json_response(coins)


@app.route('/api/coin_summaries')
def get_coin_summaries():
    summaries = list(db.mongo_db.coin_summaries.find())
    return json_response(summaries)


@app.route('/api/historical_prices/<int:coin_id>')
def get_historical_prices(coin_id):
    prices = db.mongo_db.historical_prices.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)
    series = time_series(prices, ["close", "volume"])
    return json_response(series)


@app.route('/api/historical_social_stats/<int:coin_id>')
def get_historical_social_stats(coin_id):
    stats = db.mongo_db.historical_social_stats.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)
    series = time_series(stats, "reddit_subscribers")
    return json_response(series)


@app.route('/api/prices/<int:coin_id>')
def get_prices(coin_id):
    prices = db.mongo_db.prices.find({"coin_id": coin_id})
    series = time_series(prices, "price")
    return json_response(series)


@app.route('/api/reddit_stats/<int:coin_id>')
def get_reddit_stats(coin_id):
    stats = db.mongo_db.reddit_stats.find({"coin_id": coin_id})
    series = time_series(stats, ["subscribers", "active"])
    return json_response(series)


@app.route('/api/twitter_comments/<int:coin_id>')
def get_twitter_comments(coin_id):
    stats = db.mongo_db.twitter_comments.find({"coin_id": coin_id})
    series = time_series(stats, ["avg_sentiment", "count", "strong_pos", "strong_neg", "avg_score", "sum_score"])
    return json_response(series)


@app.route('/api/reddit_comments/<int:coin_id>')
def get_reddit_comments(coin_id):
    stats = db.mongo_db.reddit_comments.find({"coin_id": coin_id})
    series = time_series(stats, ["avg_sentiment", "count", "strong_pos", "strong_neg", "avg_score", "sum_score"])
    return json_response(series)


@app.route('/api/recent_comments/<string:platform>/<int:coin_id>')
def get_recent_comments(platform, coin_id):
    comments = db.mongo_db.recent_comments.find({"coin_id": coin_id}).limit(10)
    return json_response(comments)


@app.route('/api/db_stats')
def get_db_stats():
    return json_response(db.mongo_db.db_stats.find())
