import sys
import datetime
import urllib
import concurrent.futures

from ingestion import database as db
from ingestion import util
from ingestion import coinmarketcap as cmc
from ingestion import cryptocompare as cc
from ingestion import reddit


class IngestionTask:
    def __init__(self):
        self._name = type(self).__name__
        self.__id = None

        # Status
        self.__running = False
        self.__start_time = None
        self.__end_time = None
        self.__percent_done = 0.0
        self.__failed = False
        self.__canceled = False

        # Error tracking
        self.__errors = []
        self.__errors_http = []
        self.__warnings = []

        # Profiling
        self.__db_inserts = 0
        self.__http_requests = 0

        # TODO: print http errors and request count at the end
        # and also update them when we insert our task into the db

    def __str__(self):
        return "{0} - running={1}, errors={2}, warnings={3}".\
            format(self._name, self.__running, len(self.__errors), len(self.__warnings))

    def _error(self, msg):
        print("Ingestion error:", msg)
        self.__errors.append(msg)

    def _error_http(self, msg):
        print("Ingestion HTTP error:", msg)
        self.__errors_http.append(msg)

    def _fatal(self, msg):
        print("Ingestion FATAL error:", msg)
        self._error("FATAL - " + msg)
        self.__failed = True

    def _warn(self, msg):
        print("Ingestion warning:", msg)
        self.__warnings.append(msg)

    def _progress(self, completed, total):
        self.__percent_done = completed / total

        now = datetime.datetime.today()
        elapsed = now - self.__start_time
        avg_time_per = elapsed / completed
        est_time_left = (avg_time_per * (total - completed))

        print("Progress {0}/{1} - est. time remaining {2}".format(completed, total, est_time_left))

        self.__update_db_status()

    def _run(self):
        raise NotImplementedError("Subclass must implement _run method")

    def _db_insert(self, collection, items):
        try:
            db.insert(collection, items)
            count = len(items) if isinstance(items, list) else 1
            self.__db_inserts += count
        # TODO: catch correct exception type
        except Exception as e:
            # TODO: we should keep a seperate count of db errors
            self._error("Database insert failed: " + str(e))

    def _get_data(self, datasource, arg=None):
        self.__http_requests += 1
        # TODO: this can be wrong, in the case where we have a fn data source that makes many requests
        # ie: reddit requests via praw
        # ideally we'll ditch praw and make this only take datasources and not fns

        data = None
        try:
            # TODO: allow this to call an async task
            data = datasource(arg) if callable(datasource) else datasource.get()
            return data
        except (urllib.error.URLError, urllib.error.HTTPError) as err:
            # TODO: log that url
            self._error_http(str(err))
            return None
        except Exception as err:
            self._error(str(err))

        return data


    def __update_db_status(self):
        now = datetime.datetime.today()

        # TODO: consider saving all the error messages too

        status = {
            "name": self._name,
            "start_time": self.__start_time,
            "end_time": self.__end_time,
            "running": self.__running,
            "errors": len(self.__errors),
            "errors_http": len(self.__errors_http),
            "warnings": len(self.__warnings),
            "percent_done": self.__percent_done,
            "failed": self.__failed,
            "db_inserts": self.__db_inserts,
            "http_requests": self.__http_requests,
            "canceled": self.__canceled,
            "last_update": now
        }

        try:
            if self.__id is None:
                self.__id = db.MONGO_DB.ingestion_tasks.insert(status)
            else:
                # TODO: is it better to just replace what is updated in the doc
                db.MONGO_DB.ingestion_tasks.replace_one({'_id': self.__id}, status)
        except Exception as e:
            self._error("Failed to update db status for ingestion tasks: " + str(e))

    def cancel(self):
        self.__running = False
        self.__canceled = True
        self.__end_time = datetime.datetime.today()

        self.__update_db_status()

    def run(self):
        self.__running = True
        self.__start_time = datetime.datetime.today()

        print("Running ingestion task:", self._name)
        self.__update_db_status()

        # TODO: should prob wrap in a try catch block
        self._run()

        self.__end_time = datetime.datetime.today()
        self.__running = False
        self.__percent_done = 1.0
        self.__update_db_status()

        elapsed_time = self.__end_time - self.__start_time

        sf = "Failure" if self.__failed else "Success"
        print("Ingestion task {0} ({1})".format(self._name, sf))
        print("Elapsed time:", elapsed_time)
        print("HTTP requests:", self.__http_requests)
        print("Database inserts:", self.__db_inserts)

        def print_errors(name, error_list):
            print("{0} ({1}):".format(name, len(error_list)))
            for msg in error_list:
                print("  *", msg)

        print_errors("Errors", self.__errors)
        print_errors("HTTP Errors", self.__errors_http)
        print_errors("Warnings", self.__warnings)


# TODO: periodically we need to make sure the reddit's haven't changed
# or check if a reddit link that was missing has been added
# add a param that will just force a full update of all and run once per day
class ImportCoinList(IngestionTask):
    def _run(self):
        try:
            current_coins = self._get_data(cmc.CoinList())
        except Exception as e:
            self._fatal("get_coin_list failed " + str(e))
            return

        stored_coins = db.get_coins()

        # Find the set of ids that we don't have in the database yet
        current_ids = util.list_to_set(current_coins, "cmc_id")
        stored_ids = util.list_to_set(stored_coins, "cmc_id")
        new_ids = current_ids - stored_ids

        # Find the coins with missing subreddits, so we can look again for them
        missing_subreddit_ids = set()
        for coin in stored_coins:
            if "subreddit" not in coin:
                missing_subreddit_ids.add(coin["cmc_id"])

        print("Total current coins (coinmarketcap.com):", len(current_ids))
        print("Locally stored coins:", len(stored_ids))
        print("Locally stored coins without subreddit links:", len(missing_subreddit_ids))
        print("New coins to process:", len(new_ids))

        processed = 0
        missing_subreddits = 0
        new_coins = [x for x in current_coins if x["cmc_id"] in new_ids]

        if len(new_coins) == 0:
            print("No new coins to add")
            return

        cc_coins = self._get_data(cc.CoinList())
        cc_by_symbol = {}
        for coin in cc_coins:
            cc_by_symbol[coin["symbol"]] = coin

        for coin in new_coins:
            try:
                subreddit = self._get_data(cmc.SubredditName(coin["cmc_id"]))
                if subreddit:
                    coin["subreddit"] = subreddit
                else:
                    # Reddit link isn't on coinmarketcap, so check cryptocompare

                    # TODO: we could at least log an error if the names don't match after looking up by symbol

                    # Note that technically there is a very minor issue here in that
                    # symbols aren't truly unique and cryptocompare treats them as unique,
                    # whereas coinmarketcap doesn't. This means there is the tiniest potential
                    # this line looks up the wrong coin. In practice though, this likely will
                    # never happen as only a couple coins share symbols

                    symbol = coin["symbol"]
                    cc_id = cc_by_symbol[symbol]["cc_id"]
                    stats = self._get_data(cc.SocialStats(cc_id))

                    if "Reddit" in stats and "link" in stats["Reddit"] and stats["Reddit"]["link"]:
                        subreddit = stats["Reddit"]["link"]
                        subreddit = urllib.urlparse(subreddit).path.replace("/r/", "").replace("/", "")
                        coin["subreddit"] = subreddit
                    else:
                        self._warn("missing subreddit for symbol " + symbol)

            except Exception as err:
                self._error("failed to lookup subreddit on cmc: " + str(err))
                missing_subreddits += 1

            coin["_id"] = db.next_sequence_id("coins")
            self._db_insert("coins", coin)

            processed += 1
            self._progress(processed, len(new_ids))

        print("Total coins", len(current_coins))
        print("Added", len(new_ids), "new coins")
        print("Missing subreddits", missing_subreddits)



class ImportHistoricData(IngestionTask):
    def __init__(self, collection, data_source, coin_filter=None):
        super().__init__()

        self.__collection = collection
        self.__data_source = data_source
        self.__coin_filter = coin_filter
        self._name += "-" + collection

    def _outdated(self, coins, latest_updates):
        coins_to_update = {}
        # Make a list of coins that don't have up to date historic data
        for coin in coins:
            coin_id = coin["_id"]
            update_start = datetime.datetime(2011, 1, 1)

            if coin_id in latest_updates:
                most_recent = latest_updates[coin_id]["date"]
                today = datetime.datetime.today()

                if today.day - most_recent.day <= 1:
                    continue

                update_start = most_recent + datetime.timedelta(days=1)

            coins_to_update[coin_id] = update_start

        return coins_to_update

    def _run(self):
        coins = db.get_coins(self.__coin_filter)
        latest_data = db.get_latest(self.__collection)
        coins_to_update = self._outdated(coins, latest_data)

        print("Coins with no {0} data: {1}".format(self.__collection, len(coins) - len(latest_data)))
        print("Coins with out of date {0} data: {1}".format(self.__collection, len(coins_to_update)))

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

                print("Added all historic", self.__collection, "data for", coin["symbol"])
            else:
                self._error("no historic data found for {0}, starting on {1}".format(coin["symbol"], update_start))

            processed += 1
            self._progress(processed, len(coins_to_update))


class ImportPrices(IngestionTask):
    def _run(self):
        data = self._get_data(cmc.Ticker())

        # Need to map our ids to coin market cap ids
        coins = db.get_coins()
        id_map = {}
        for coin in coins:
            id_map[coin["cmc_id"]] = coin["_id"]

        for coin in data:
            coin["coin_id"] = id_map[coin["cmc_id"]]
            del coin["cmc_id"]

        self._db_insert("prices", data)


class ImportRedditStats(IngestionTask):
    def __init__(self, collection, get_stats):
        super().__init__()

        self.__collection = collection
        self.__get_stats = get_stats
        self._name += "-" + collection

    def _run(self):
        coins = db.get_coins({"subreddit": {"$exists": True}})

        # TODO: this feels a little odd not being a proper data source, but okay for now

        processed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_coin = {executor.submit(self._get_data, self.__get_stats, coin["subreddit"]): coin for coin in coins}
            for future in concurrent.futures.as_completed(future_to_coin):
                coin = future_to_coin[future]

                try:
                    today = datetime.datetime.today()
                    stats = future.result()
                    if stats:
                        stats["date"] = today
                        stats["coin_id"] = coin["_id"]
                        self._db_insert(self.__collection, stats)
                    else:
                        self._error("Failed to get reddit stats for r/{}".format(coin["subreddit"]))
                except Exception as err:
                    self.__("Failed to get future results for r/{}, {}".format(coin["subreddit"]), err)

                processed += 1
                self._progress(processed, len(coins))


def __run_tasks(tasks):
    if not db.connected():
        print("Database not connected, exiting")
        return

    start_time = datetime.datetime.today()

    # TODO: where does this belong
    db.create_indexes()

    for task in tasks:
        try:
            task.run()
        except (KeyboardInterrupt, SystemExit):
            # TODO: this cleanup is good, but won't work if we crash or are terminated forcefully
            # prob can just kill any running tasks on startup, assuming we only use one process
            # but that won't scale to having multiple nodes doing processing
            task.cancel()
            sys.exit()

    end_time = datetime.datetime.today()
    elapsed_time = end_time - start_time

    print("Ingestion complete, elapsed time:", elapsed_time)


def import_historic_data():
    tasks = [
        ImportCoinList(),
        ImportHistoricData("historic_prices", cmc.HistoricalPrices),
        ImportHistoricData("historic_social_stats", reddit.HistoricalStats, {"subreddit": {"$exists": True}})
    ]

    __run_tasks(tasks)


def import_current_data():
    tasks = [
        ImportCoinList(),
        ImportPrices(),
        ImportRedditStats("reddit_stats", reddit.get_current_stats),
        ImportRedditStats("reddit_sentiment", reddit.get_avg_sentiment)
    ]
    __run_tasks(tasks)
