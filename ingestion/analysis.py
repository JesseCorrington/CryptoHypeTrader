import pymongo
from datetime import datetime, timedelta
from common import database as db

def dict_access(d, key):
    current = d
    for subkey in key.split("."):
        current = current[subkey]

    return current

def growth(records, field, from_date, to_date):
    records = [x for x in records
               if from_date <= x["date"] <= to_date]

    if len(records) < 2:
        return 0, 0

    try:
        end = dict_access(records[0], field)
        start = dict_access(records[-1], field)
    except KeyError:
        return 0, 0

    if end is None or start is None:
        return 0, 0

    growth_amount = end - start

    # hack to prevent division by zero
    if start == 0:
        start = 1

    growth_percent = growth_amount / start

    return growth_amount, growth_percent


def growth_stats(coin, stats, key, end_time):
    time_ranges = {
        "h12": timedelta(hours=12),
        "d1": timedelta(days=1),
        "d3": timedelta(days=3),
        "d5": timedelta(days=5),
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
    oldest = now - timedelta(days=8)

    all_stats = []
    coins = list(db.mongo_db.coins.find())

    def get_stats(collection, coin_id):
        return list(db.mongo_db[collection].find({"coin_id": coin_id,
                                                  "date": {"$gte": oldest}}).sort('date', pymongo.DESCENDING))

    stats_to_calc = [
        ("price", "prices", "price"),
        ("volume", "prices", "volume"),
        ("reddit", "reddit_stats", "subscribers"),
        ("twitter", "twitter_comments", "count"),
        ("cc_points", "cryptocompare_stats", "total_points"),
        ("code_points", "cryptocompare_stats", "code_repo.points"),
        ("facebook_points", "cryptocompare_stats", "facebook.points"),
        ("twitter_followers", "cryptocompare_stats", "twitter.followers")
    ]

    for coin in coins:
        cid = coin["_id"]
        coin_stats = {"coin_id": cid}
        all_stats.append(coin_stats)

        for name, collection, key in stats_to_calc:
            entries = get_stats(collection, cid)
            stats = growth_stats(coin, entries, key, now)
            if stats:
                coin_stats[name] = stats
            else:
                coin_stats[name] = {}

    return all_stats
