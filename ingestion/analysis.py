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


def coin_growth_summaries():
    now = datetime.utcnow()
    oldest = now - timedelta(days=6)

    stats = []
    coins = list(db.mongo_db.coins.find({"subreddit": {"$exists": True}}))

    all_stats = db.mongo_db.reddit_stats.find({"date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING)
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
            coin_stats["_" + name + "_g"] = amount
            coin_stats["_" + name + "_p"] = percent

    return stats
