from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp


class IngestionTask:
    def __init__(self):
        self.__name = type(self).__name__
        self.__errors = []
        self.__warnings = []
        self.__start_time = None
        self.__end_time = None
        self.__running = False
        self.__percent_done = 0.0
        self.__failed = False
        self.__db_inserts = 0
        self.__id = None

    def __str__(self):
        return "{0} - running={1}, errors={2}, warnings={3}".\
            format(self.__name, self.__running, len(self.__errors), len(self.__warnings))

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

        elapsed = timestamp() - self.__start_time
        avg_time_per = elapsed / completed
        est_time_left = (avg_time_per * (total - completed)) / 1000

        print("Progress {0}/{1} - est. time remaining {2} seconds".format(completed, total, est_time_left))

        self.__update_db_status()

    def _run(self):
        raise NotImplementedError("Subclass must implement _run method")

    def _db_insert(self, collection, items):
        try:
            db.insert(collection, items)
        except Exception as e:
            self._error("Database insert failed: " + str(e))

    def __update_db_status(self):
        # TODO: at start and end, also log start/end memory usage for the db

        status = {
            "name": self.__name,
            "start_time": self.__start_time,
            "running": self.__running,
            "errors": len(self.__errors),
            "warnings": len(self.__warnings),
            "percent_done": self.__percent_done,
            "failed": self.__failed,
            "db_inserts": self.__db_inserts
        }

        try:
            if self.__id is None:
                self.__id = db.MONGO_DB.ingestion_tasks.insert(status)
            else:
                # TODO: is it better to just replace what is updated in the doc
                db.MONGO_DB.ingestion_tasks.replace_one({'_id': self.__id}, status)
        except Exception as e:
            self._error("Failed to update db status for ingestion tasks: " + str(e))

    def run(self):
        self.__running = True
        self.__start_time = timestamp()

        print("Running ingestion task:", self.__name)
        self.__update_db_status()

        self._run()

        self.__end_time = timestamp()
        self.__running = False

        elapsed_time = self.__end_time - self.__start_time

        sf = "Failure" if self.__failed else "Success"
        print("Ingestion task {0} ({1})".format(self.__name, sf))
        print("Elapsed time (seconds):", elapsed_time / 1000)
        print("Database inserts:", self.__db_inserts)

        ec = len(self.__errors)
        wc = len(self.__warnings)
        if ec > 0:
            print("errors ({0}):".format(ec))
            for e in self.__errors:
                print("  *", e)
        if wc > 0:
            print("warnings ({0}):".format(wc))
            for w in self.__warnings:
                print("  *", w)


# TODO: periodically we need to make sure the reddit's haven't changed
# add a param that will just force a full update of all and run every few days
class ImportCoinListTask(IngestionTask):
    def _run(self):
        try:
            current_coins = get_coin_list()
        except Exception as e:
            self._fatal("get_coin_list failed" + str(e))
            return

        stored_coins = db.get_coins()
        stored_symbols = set()
        added_symbols = set()
        missing_subreddits = set()
        new_symbols = set()

        for symbol in stored_coins:
            stored_symbols.add(symbol)

        for symbol in current_coins:
            if symbol not in stored_symbols:
                new_symbols.add(symbol)

        print("Total current coins (coinmarketcap.com):", len(current_coins))
        print("Locally stored coins:", len(stored_symbols))
        print("New coins to process:", len(new_symbols))

        processed = 0
        for symbol in new_symbols:
            coin = current_coins[symbol]
            cmc_id = coin["cmc_id"]

            try:
                subreddit = get_subreddit(cmc_id)
                if subreddit:
                    coin["subreddit"] = get_subreddit(cmc_id)
                else:
                    self._warn("missing subreddit for symbol " + symbol)
            except Exception as err:
                # TODO: try looking it up on cryptocompare too, maybe that should be our first source of data
                self._error("failed to lookup subreddit on cmc: " + str(err))
                missing_subreddits.add(symbol)

            coin["_id"] = coin["symbol"]
            self._db_insert("coins", coin)

            added_symbols.add(symbol)

            processed += 1
            self._progress(processed, len(new_symbols))

        if len(new_symbols) > 0:
            print("Total coins", len(current_coins))
            print("Added", len(added_symbols), "new coins")
            print("Missing subreddits", len(missing_subreddits))
        else:
            print("No new coins to add")


class ImportHistoricPricesTask(IngestionTask):
    def _run(self):
        return




def _outdated_historic(coins, latest_updates):
    coins_to_update = {}
    # Make a list of coins that don't have up to date historic data
    for symbol in coins:
        update_start = datetime.date(2011, 1, 1)

        if symbol in latest_updates:
            most_recent = latest_updates[symbol]["date"]
            today = datetime.datetime.today()

            if today - most_recent < datetime.timedelta(days=1):
                continue

            update_start = most_recent + datetime.timedelta(days=1)

        coins_to_update[symbol] = update_start

    return coins_to_update


def _ingest_historic(name, get_latest_saved, get_new_data, insert_data):
    coins = db.get_coins()
    latest_data = get_latest_saved()
    print("Coins with no", name, "data", len(coins) - len(latest_data))

    coins_to_update = _outdated_historic(coins, latest_data)
    print("Coins with out of date", name, "data:", len(coins_to_update))
    processed = 0

    for symbol in coins_to_update:
        coin = coins[symbol]
        update_start = coins_to_update[symbol]

        new_data = get_new_data(coin, start=update_start)
        if new_data:
            for day in new_data:
                day["symbol"] = coin["symbol"]

            insert_data(new_data)

            print("Added all historic", name, "data for", coin["symbol"])
        else:
            print("Error: no historic data found for", symbol, "starting on", update_start)

        processed += 1
        print("Progress", processed, "/", len(coins_to_update))


def save_historic_prices():
    _ingest_historic("Prices", db.get_latest_prices, get_historical_prices, db.insert_prices)


def save_historic_reddit_stats():
    _ingest_historic("Reddit stats", db.get_latest_social_stats, get_historical_stats, db.insert_social_stats)


def run_all():
    start_time = timestamp()

    # TODO: where does this belong, is it okay to run it every time?
    db.create_indexes()

    # TODO: do the timing here
    tasks = [
        ImportCoinListTask(),
        #"Update historic prices": save_historic_prices,
        #"Update historic reddit stats": save_historic_reddit_stats
    ]

    for task in tasks:
        task.run()

    elapsed_time = timestamp() - start_time

    print("Ingestion complete, elapsed time (ms):", elapsed_time)


if __name__ == '__main__':
    run_all()