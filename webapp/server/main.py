import json
import os
import signal
from datetime import datetime
import flask
import pymongo
from bson import ObjectId
from common import database as db
from webapp.server import config

# This is just a basic dev server for easy internal testing
# Basic REST API access is provided, and static files are hosted out of the client directory
# Not safe for production use

app = flask.Flask(__name__)


def run(config_name):
    """Runs the API server with the specified configuration
    :param config_name: must be either "dev" or "prod"
    """

    cfg = None
    if config_name == "dev":
        cfg = config.dev
    elif config_name == "prod":
        cfg = config.prod
    else:
        print("Error: invalid configuration -", config_name)
        print("Valid configs: dev, prod")
        return

    print("Running server with config -", config_name)

    db.init(cfg["database"])

    # TODO: takeout CORS, and setup nginx properly to redirect
    # https://stackoverflow.com/questions/28925304/javascript-stack-web-server-and-api-server-together-or-separate
    from flask_cors import CORS
    CORS(app)

    app.run()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return int(o.timestamp() * 1000)

        return json.JSONEncoder.default(self, o)


def json_response(items, key_filter=None, filter_out=False):
    """Encode the items object into a JSON response
    key_filter can be used to filter items so the response contains only relevant data
    """

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
    """Convert an array of objects into a compact time series representation
    Converts objects of the form
    [{"date": d1, k1: v1-1, k2: v2-1}, {"date": d2, k1: v1-2, k2-2: v2}, {"date": dn, k1: v1-n, k2: v2-n}]

    To arrays of the form
    [[d1, v1-1, v2-1], [d2, v1-2, v2-2], ... [dn, v1-n, v2-n]
    """

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


@app.route('/api/ingestion_tasks')
def get_tasks():
    # get the n most recent of each task type, group by task type, sort by date
    docs = db.mongo_db.ingestion_tasks.aggregate([
        {"$sort": {"start_time": pymongo.DESCENDING}},
        {"$group": {"_id": "$name"}}
    ])

    resp = []
    for doc in list(docs):
        name = doc["_id"]
        tasks = db.mongo_db.ingestion_tasks.find({"name": name}).sort("date", pymongo.DESCENDING).limit(1)
        resp.append(list(tasks)[0])

    return JSONEncoder().encode(resp)


@app.route('/api/ingestion_tasks/<string:name>')
def get_tasks_by_name(name):
    tasks = db.mongo_db.ingestion_tasks.find({"name": name})
    if tasks is not None:
        return json_response(tasks)
    else:
        return json_response({"error": "No tasks with name {}".format(name)})


# TODO: test this with the UI
@app.route('/api/ingestion_tasks/cancel/<string:id>')
def cancel_task(id):
    task = dict(db.mongo_db.ingestion_tasks.find({"id": id}))
    success = False

    if task is not None:
        os.kill(task["pid"], signal.SIGKILL)
        success = True

    return json_response({"success": success})


@app.route('/api/coin/<int:coin_id>')
def get_coin(coin_id):
    coin = dict(db.mongo_db.coins.find_one({"_id": coin_id}))
    if coin is not None:
        return JSONEncoder().encode(coin)
    else:
        return json_response({"error": "No coin with id: {}".format(coin_id)})


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
    if prices is not None:
        series = time_series(prices, ["close", "volume"])
        return json_response(series)
    else:
        return json_response({"error": "No historical price data for coin id {}".format(coin_id)})


@app.route('/api/historical_social_stats/<int:coin_id>')
def get_historical_social_stats(coin_id):
    stats = db.mongo_db.historical_social_stats.find({"coin_id": coin_id}).sort("date", pymongo.ASCENDING)
    if stats is not None:
        series = time_series(stats, "reddit_subscribers")
        return json_response(series)
    else:
        return json_response({"error": "No historical social stats for coin id {}".format(coin_id)})


@app.route('/api/prices/<int:coin_id>')
def get_prices(coin_id):
    prices = db.mongo_db.prices.find({"coin_id": coin_id})
    if prices is not None:
        series = time_series(prices, "price")
        return json_response(series)
    else:
        return json_response({"error": "No price data for coin id {}".format(coin_id)})


@app.route('/api/reddit_stats/<int:coin_id>')
def get_reddit_stats(coin_id):
    stats = db.mongo_db.reddit_stats.find({"coin_id": coin_id})
    if stats is not None:
        series = time_series(stats, ["subscribers", "active"])
        return json_response(series)
    else:
        return json_response({"error": "No reddit stats for coin id {}".format(coin_id)})


@app.route('/api/twitter_comments/<int:coin_id>')
def get_twitter_comments(coin_id):
    comments = db.mongo_db.twitter_comments.find({"coin_id": coin_id})
    if comments is not None:
        series = time_series(comments, ["avg_sentiment", "count", "strong_pos", "strong_neg", "avg_score", "sum_score"])
        return json_response(series)
    else:
        return json_response({"error": "No twitter comments for coin id".format(coin_id)})


@app.route('/api/reddit_comments/<int:coin_id>')
def get_reddit_comments(coin_id):
    comments = db.mongo_db.reddit_comments.find({"coin_id": coin_id})
    if comments is not None:
        series = time_series(comments, ["avg_sentiment", "count", "strong_pos", "strong_neg", "avg_score", "sum_score"])
        return json_response(series)
    else:
        return json_response({"error": "No reddit comments for coin id".format(coin_id)})


@app.route('/api/recent_comments/<string:platform>/<int:coin_id>')
def get_recent_comments(platform, coin_id):
    comments = db.mongo_db.recent_comments.find({"coin_id": coin_id}).limit(10)
    if comments is not None:
        return json_response(comments)
    else:
        return json_response({"error": "No recent comments on {} for coin id {}".format(platform, coin_id)})


@app.route('/api/db_stats')
def get_db_stats():
    return json_response(db.mongo_db.db_stats.find())
