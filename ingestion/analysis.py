import pymongo
from datetime import datetime, timedelta
from common import database as db


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


def growth_stats(coin, stats, key, end_time):
    time_ranges = {
        "h2": timedelta(hours=2),
        "h6": timedelta(hours=6),
        "h12": timedelta(hours=12),
        "d1": timedelta(days=1),
        "d2": timedelta(days=2),
        "d3": timedelta(days=3),
        "d4": timedelta(days=4),
        "d5": timedelta(days=5),
        "d6": timedelta(days=6),
        "d7": timedelta(days=7)
    }

    entries = [x for x in stats if x["coin_id"] == coin["_id"]]

    if len(entries) == 0:
        return None

    coin_stats = {}
    for name, time_range in time_ranges.items():
        from_date = end_time - time_range
        amount, percent = growth(entries, key, from_date, end_time)
        coin_stats[name] = amount
        coin_stats[name + "_pct"] = percent

    return coin_stats


def social_growth():
    now = datetime.utcnow()
    oldest = now - timedelta(days=10)

    all_stats = []
    coins = list(db.mongo_db.coins.find({"subreddit": {"$exists": True}}))

    reddit_stats = list(db.mongo_db.reddit_stats.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING))
    twitter_stats = list(db.mongo_db.twitter_comments.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING))
    prices = list(db.mongo_db.prices.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING))

    stats_to_calc = [
        ("price", prices, "price"),
        ("reddit", reddit_stats, "subscribers"),
        ("twitter", twitter_stats, "count")
    ]

    for coin in coins:
        coin_stats = {"coin_id": coin["_id"]}
        all_stats.append(coin_stats)

        for name, value, key in stats_to_calc:
            stats = growth_stats(coin, value, key, now)
            if stats:
                coin_stats[name] = stats

    return all_stats
