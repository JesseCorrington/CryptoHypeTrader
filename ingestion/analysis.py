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


# TODO: make this work for twitter too
def social_growth():
    now = datetime.utcnow()
    oldest = now - timedelta(days=10)

    stats = []
    coins = list(db.mongo_db.coins.find({"subreddit": {"$exists": True}}))

    all_stats = db.mongo_db.reddit_stats.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING)
    all_stats = list(all_stats)

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

    for coin in coins:
        entries = [x for x in all_stats if x["coin_id"] == coin["_id"]]

        if len(entries) == 0:
            continue

        coin_stats = {"coin_id": coin["_id"]}
        stats.append(coin_stats)
        for name, time_range in time_ranges.items():
            from_date = now - time_range
            amount, percent = growth(entries, "subscribers", from_date, now)
            coin_stats[name] = amount
            coin_stats[name + "_pct"] = percent

    return stats
