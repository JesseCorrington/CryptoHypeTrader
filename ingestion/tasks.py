import concurrent.futures
import datetime
import pymongo
import urllib.request

from common import database as db, util
from ingestion import config, manager as mgr
from ingestion.datasources import reddit, twitter, cryptocompare as cc, coinmarketcap as cmc, stocktwits as st
from ingestion import analysis


def init():
    db.init(config.database)
    db.create_indexes()
    reddit.init_api()
    twitter.init_api()


class ImportCoinList(mgr.IngestionTask):
    """ Task to import the list of coins from coinmarketcap.com and cryptocompare.com
    This checks all coins on every run, and only makes updates to new/changed items in the db
    while this is inefficient, this only needs to run a couple times a day
    and it's better to be sure we have correct info, as all other tasks depend on it
    """

    def __get_links(self, coin):
        links = self._get_data(cmc.CoinLinks(coin))
        if links is None:
            return None

        # If we have a subreddit, make sure it's valid, because some links are broken on cmc
        if "subreddit" in links:
            if not reddit.is_valid(links["subreddit"]):
                self._warn("Invalid subreddit {}".format(links["subreddit"]))
                del links["subreddit"]

        missing_links = {"subreddit", "twitter", "btctalk_ann"} - set(links.keys())
        if len(missing_links) > 0 and "cc_id" in coin:
            cc_links = self._get_data(cc.CoinLinks(coin["cc_id"]))

            if cc_links:
                for missing_link in missing_links:
                    if missing_link in cc_links:
                        links[missing_link] = cc_links[missing_link]

        return links

    @staticmethod
    def __duplicate_symbols(coins):
        """Returns a list of symbols that have duplicates in the coin list"""

        symbols = set()
        duplicate_symbols = set()
        for coin in coins:
            sym = coin["symbol"]
            if sym in symbols:
                duplicate_symbols.add(sym)
            else:
                symbols.add(sym)

        return duplicate_symbols

    def __merge_cc_data(self, coins, cc_coins):
        """Merges the cryptocompare ids into the coin list
        this allows us to pull coin data from both sources
        """

        def full_id(coin):
            return "{}_{}".format(coin["symbol"], coin["name"]).lower()

        # Symbols are not guaranteed to be unique, so to be sure we map a coin from
        # coinmarketcap to cryptocompare we use <symbol_name> as the id
        cc_lookup = {}
        for coin in cc_coins:
            cid = full_id(coin)
            if cid in cc_lookup:
                self._fatal("Duplicate cid {}".format(cid))
            else:
                cc_lookup[cid] = coin

        for coin in coins:
            cid = full_id(coin)
            if cid in cc_lookup:
                coin["cc_id"] = cc_lookup[cid]["cc_id"]
                coin["icon"] = cc_lookup[cid]["icon"]

    def _run(self):
        current_coins = self._get_data(cmc.CoinList())
        cc_coins = self._get_data(cc.CoinList())

        if not current_coins or not cc_coins:
            self._fatal("Failed to get coinlists from remotes")

        stored_coins = db.get_coins()

        # Find the set of ids that we don't have in the database yet
        current_ids = util.list_to_set(current_coins, "cmc_id")
        stored_ids = util.list_to_set(stored_coins, "cmc_id")
        new_ids = current_ids - stored_ids

        # map from coinmarketcap id to coins
        stored_coins_map = util.list_to_dict(stored_coins, "cmc_id")

        print("Total current coins (coinmarketcap.com):", len(current_ids))
        print("Locally stored coins:", len(stored_ids))
        print("New coins to process:", len(new_ids))

        self.__merge_cc_data(current_coins, cc_coins)

        processed = 0
        coin_updates = 0
        for coin in current_coins:
            links = self.__get_links(coin)
            if links is None:
                continue

            for name, val in links.items():
                coin[name] = val

            in_db = coin["cmc_id"] in stored_ids
            if not in_db:
                coin["_id"] = db.next_sequence_id("coins")
                self._db_insert("coins", coin)
            else:
                stored_coin = stored_coins_map[coin["cmc_id"]]
                coin["_id"] = stored_coin["_id"]

                # Update only if changed
                if coin != stored_coin:
                    # fields will allow to be updated only if not empty.
                    # This prevents removing good data if we simply failed to get the data this time.
                    # This has the drawback that bad data won't get removed
                    # The only draw back is that if bad data got corrected to be empty
                    # we would not remove it here, but we can deal with that manually for now

                    updateable = {"cc_id", "subreddit", "twitter", "btctalk_ann", "icon"}
                    updates = {}
                    for field in updateable:
                        current = coin[field] if field in coin else ""
                        stored = stored_coin[field] if field in stored_coin else ""

                        if current != stored and len(current) > 0:
                            updates[field] = current

                    if len(updates) > 0:
                        coin_updates += 1
                        self._db_update_one("coins", coin["_id"], updates)

            processed += 1
            self._progress(processed, len(current_coins))

        print("Total coins", len(current_coins))
        print("Added", len(new_ids), "new coins")
        print("Updated", coin_updates)


class ImportHistoricalData(mgr.IngestionTask):
    """Task to Import historical daily data from a specified DataSource"""

    def __init__(self, collection, data_source, coin_filter=None):
        """
        :param collection: the db collection to store the data
        :param data_source: the DataSource used to get the data
        :param coin_filter: optional to filter which coins to use
        """
        super().__init__()

        self.__collection = collection
        self.__data_source = data_source
        self.__coin_filter = coin_filter
        self._name += "-" + collection

    @staticmethod
    def _outdated(coins, latest_updates):
        """Returns a list of coins with outdated data in the db"""

        coins_to_update = {}
        # Make a list of coins that don't have up to date historical data
        for coin in coins:
            coin_id = coin["_id"]
            update_start = datetime.datetime(2011, 1, 1)

            if coin_id in latest_updates:
                most_recent = latest_updates[coin_id]["date"]
                today = datetime.datetime.utcnow()

                if today.day - most_recent.day <= 1:
                    continue

                update_start = most_recent + datetime.timedelta(days=1)

            coins_to_update[coin_id] = update_start

        return coins_to_update

    def _run(self):
        coins = db.get_coins(self.__coin_filter)
        latest_data = db.get_latest(self.__collection)
        coins_to_update = self._outdated(coins, latest_data)

        print("Coins with no {} data: {}".format(self.__collection, len(coins) - len(latest_data)))
        print("Coins with out of date {} data: {}".format(self.__collection, len(coins_to_update)))

        processed = 0
        coins = util.list_to_dict(coins, "_id")

        for coin_id in coins_to_update:
            coin = coins[coin_id]
            update_start = coins_to_update[coin_id]

            new_data = self._get_data(self.__data_source(coin, start=update_start))
            if new_data:
                for day in new_data:
                    day["coin_id"] = coin["_id"]

                self._db_insert(self.__collection, new_data)

                print("Added all historical", self.__collection, "data for", coin["symbol"])
            else:
                self._error("no historical data found for {}, starting on {}".format(coin["symbol"], update_start))

            processed += 1
            self._progress(processed, len(coins_to_update))


class ImportPrices(mgr.IngestionTask):
    """Task to import current prices for all coins"""

    def _run(self):
        data = self._get_data(cmc.Ticker())
        if not data:
            self._fatal("Failed to get coinmarketcap ticker")

        # Need to map coinmarketcap ids back to ours
        stored_coins = db.get_coins()
        id_map = {}
        for coin in stored_coins:
            id_map[coin["cmc_id"]] = coin["_id"]

        for coin in data:
            cmc_id = coin["cmc_id"]

            if cmc_id in id_map:
                coin["coin_id"] = id_map[cmc_id]
                del coin["cmc_id"]
            else:
                self._error("Can't add price data to unknown coin {}".format(cmc_id))

        # filter out coins we haven't seen yet
        # we'll pick them up after our ImportCoinList runs again
        data = [x for x in data if "coin_id" in x]

        self._db_insert("prices", data)


class ImportRedditStats(mgr.IngestionTask):
    """Task to import current reddit stats"""

    def __init__(self, collection, get_stats):
        super().__init__()

        self.__collection = collection
        self.__get_stats = get_stats
        self._name += "-" + collection

    def _run(self):
        coins = db.get_coins({"subreddit": {"$exists": True}})

        processed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_coin = {executor.submit(self._get_data, self.__get_stats, coin["subreddit"]): coin for coin in coins}
            for future in concurrent.futures.as_completed(future_to_coin):
                coin = future_to_coin[future]

                try:
                    today = datetime.datetime.utcnow()
                    stats = future.result()
                    if stats:
                        stats["date"] = today
                        stats["coin_id"] = coin["_id"]
                        self._db_insert(self.__collection, stats)
                    else:
                        self._error("Failed to get reddit stats for r/{}".format(coin["subreddit"]))
                except Exception as err:
                    self._error("Failed to get future results for r/{}, {}".format(coin["subreddit"], err))

                processed += 1
                self._progress(processed, len(coins))


class ImportStockTwits(mgr.IngestionTask):
    """Task to import recent StockTwits posts"""

    def __init__(self, collection, num_posts=2):
        super().__init__()
        self.__collection = collection
        self.num_posts = num_posts

    def _run(self):
        coins = st.CoinList()
        coins = self._get_data(coins)

        for coin in range(len(coins.iloc[:self.num_posts,:])):
            posts = st.recentPosts(coins.loc[coin, 'symbol'] + '.X',
                                   coins.loc[coin, 'coin_id'],
                                   coins.loc[coin, 'name'])
            posts = self._get_data(posts)
            self._db_insert(self.__collection, posts)


class ImportCommentStats(mgr.IngestionTask):
    """Task to import social media comment stats"""

    def __init__(self, collection, comment_scanner, coin_filter, max_workers=5):
        super().__init__()
        self.__comment_scanner = comment_scanner
        self.__collection = collection
        self.__coin_filter = coin_filter
        self.__max_workers = max_workers

        self._name += "-" + collection

    def _run(self):
        coins = db.get_coins(self.__coin_filter)
        hours = 1
        processed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__max_workers) as executor:
            future_to_coin = {}
            for coin in coins:
                scanner = self.__comment_scanner(coin, hours)
                fut = executor.submit(scanner.find_comments)
                future_to_coin[fut] = (coin, scanner)

            for future in concurrent.futures.as_completed(future_to_coin):
                coin, scanner = future_to_coin[future]

                try:
                    now = datetime.datetime.utcnow()

                    record = {
                        "date": now,
                        "coin_id": coin["_id"],
                        "count": scanner.count(),
                        "sum_score": scanner.sum_score(),
                        "avg_score": scanner.avg_score(),
                        "avg_sentiment": scanner.avg_sentiment(),
                        "strong_pos": scanner.count_strong_pos(),
                        "strong_neg": scanner.count_strong_neg()
                    }

                    self._db_insert(self.__collection, record)

                    strong_pos = scanner.strong_pos()
                    strong_neg = scanner.strong_neg()

                    # Remove old comments to reduce storage requirements
                    now = datetime.datetime.utcnow()
                    max_age = now - datetime.timedelta(days=200)
                    db.mongo_db.recent_comments.remove({"date": {"$lt": max_age}})

                    for comment in strong_pos + strong_neg:
                        r = {
                            "date": now,
                            "coin_id": coin["_id"],
                            "text": comment.text,
                            "score": comment.score,
                            "sentiment": comment.sentiment,
                            "platform": self.__collection
                        }
                        self._db_insert("recent_comments", r)

                except Exception as err:
                    self._error("Failed to get future results for r/{}, {}".format(coin["subreddit"], err))

                processed += 1
                self._progress(processed, len(coins))


class ImportCryptoCompareStats(mgr.IngestionTask):
    """Task to import stats from cryptocompare"""

    def _run(self):
        coins = db.get_coins({"cc_id": {"$exists": True}})
        processed = 0

        for coin in coins:
            stats = self._get_data(cc.SocialStats(coin["cc_id"]))
            if stats:
                stats["date"] = datetime.datetime.utcnow()
                stats["coin_id"] = coin["_id"]
                self._db_insert("cryptocompare_stats", stats)
            else:
                self._warn("No stats for coin {}".format(coin["symbol"]))

            processed += 1
            self._progress(processed, len(coins))


class DownloadCoinIcons(mgr.IngestionTask):
    """Task to download icon image files for all coins"""

    def _run(self):
        coins = db.get_coins({"icon": {"$exists": True}})
        processed = 0

        for coin in coins:
            missing = db.mongo_db.coin_icons.find_one({"coin_id": coin["_id"]}) is None

            if "icon" in coin and len(coin["icon"]) > 0 and missing:
                req = urllib.request.Request(coin["icon"])

                # Need to fake being a browser, or we get a 403
                req.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36')

                with urllib.request.urlopen(req) as response:
                    data = response.read()

                    item = {
                        "coin_id": coin["_id"],
                        "data": data
                    }

                    self._db_insert("coin_icons", item)

            processed += 1
            self._progress(processed, len(coins))


class SaveDBStats(mgr.IngestionTask):
    """Task to save database statistics so we can track over time"""

    def _run(self):
        stats = db.mongo_db.command("dbstats")
        stats["date"] = datetime.datetime.utcnow()
        self._db_insert("db_stats", stats)


class CreateCoinSummaries(mgr.IngestionTask):
    """Task to analyse statistics and create summary reports for each coin
    This is run periodically, as it's a slow process and we want to do it in
    the background and cache the results for later use
    """

    def _run(self):
        coins = db.get_coins()

        prices = db.mongo_db["prices"].aggregate([
            {"$sort": {"date": pymongo.DESCENDING}},
            {"$group": {"_id": "$coin_id", "data": {'$first': '$$ROOT'}}}
        ], allowDiskUse=True)

        prices = db.cursor_to_dict(prices)
        growth = analysis.social_growth()
        growth = util.list_to_dict(growth, "coin_id")

        processed = 0
        for coin in coins:
            cid = coin["_id"]

            if cid not in prices:
                self._warn("No current price data for {}".format(cid))
                continue

            p = prices[cid]["data"]

            record = {
                "coin_id": coin["_id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "market_cap": p["market_cap"],
                "price": p["price"],
                "volume": p["volume"]
            }

            # Add in optional vals
            for key in ["subreddit", "twitter", "cmc_id", "cc_id"]:
                if key in coin:
                    record[key] = coin[key]

            if cid in growth:
                del growth[cid]["coin_id"]
                record["growth"] = growth[cid]

            db.mongo_db.coin_summaries.replace_one({"coin_id": cid}, record, upsert=True)

            processed += 1
            if processed % 50 == 0:
                self._progress(processed, len(coins))


# Helper function for task runs
def historical_data_tasks():
    return [
        ImportHistoricalData("historical_prices", cmc.HistoricalPrices),
        ImportHistoricalData("historical_social_stats", reddit.HistoricalStats, {"subreddit": {"$exists": True}})
    ]


def current_data_tasks():
    return [
        ImportPrices(),
        ImportRedditStats("reddit_stats", reddit.get_current_stats),
        ImportCommentStats("reddit_comments", reddit.CommentScanner, {"subreddit": {"$exists": True}})
    ]


def twitter_tasks():
    # TODO: this has to be run separately because it takes much longer than the other tasks
    # due to the low twitter API rate limit, which on average only allows us to process
    # around 90 coins every 15 minutes, which means this takes 3+ hours
    # look into distributing this across several server nodes with different twitter API keys

    return [
        ImportCommentStats("twitter_comments", twitter.CommentScanner, {"twitter": {"$exists": True}}, 1),
    ]


def analysis_tasks():
    return [CreateCoinSummaries()]
