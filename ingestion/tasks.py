import sys
import datetime
from urllib.parse import urlparse
from ingestion import database as db
from ingestion import util
from ingestion import coinmarketcap as cmc
from ingestion import cryptocompare as cc


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
            self.__db_inserts += len(items)
        except Exception as e:
            self._error("Database insert failed: " + str(e))

    def _get_data(self, datasource):
        self.__http_requests += 1

        try:
            data = datasource.get()
            return data
        except Exception as err:
            # TODO: it would be nice to distinguish between http and parse/format errors
            self.__errors_http.append(str(err))
            return None

    def __update_db_status(self):
        now = datetime.datetime.today()

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
            print("{0} ({1}):".format(error_list, len(error_list)))
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
                        subreddit = urlparse(subreddit).path.replace("/r/", "").replace("/", "")
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
    def __init__(self, collection, get_data, coin_filter=None):
        super().__init__()

        self.__collection = collection
        self.__get_data = get_data
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

            new_data = self.__get_data(coin, start=update_start)
            if new_data:
                for day in new_data:
                    day["coin_id"] = coin["_id"]

                self._db_insert(self.__collection, new_data)

                print("Added all historic", self.__collection, "data for", coin["symbol"])
            else:
                self._error("no historic data found for {0}, starting on {1}".format(coin["symbol"], update_start))

            processed += 1
            self._progress(processed, len(coins_to_update))


class ImportCurrentData(IngestionTask):
    def __init__(self, collection, get_data):
        super().__init__()

        self.__collection = collection
        self.__get_data = get_data
        self._name += "-" + collection

    def _run(self):
        data = self.__get_data()
        self._db_insert(self.__collection, data)

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
        #ImportHistoricData("historic_prices", cmc.get_historical_prices),
        #ImportHistoricData("historic_social_stats", reddit.get_historical_stats, {"subreddit": {"$exists": True}})
    ]
    __run_tasks(tasks)


def import_current_data():
    tasks = [
        ImportCoinList(),
        ImportCurrentData("ticker", cmc.get_ticker)
    ]
    __run_tasks(tasks)
