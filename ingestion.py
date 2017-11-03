from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp



# TODO: move the get url into here, and then we can track how many requests are made too

class IngestionTask:

    # TODO: can ones only seen in base chase be __
    def __init__(self):
        self._name = "Unknown Task"
        self._errors = []
        self._warnings = []
        self._start_time = None
        self._end_time = None
        self._running = False
        self._percent_done = 0
        self._failed = False
        self._db_inserts = 0

    def __str__(self):
        return "{0} - running={1}, errors={2}, warnings={3}".\
            format(self._name, self._running, self._errors, self._warnings)

    def _error(self, msg):
        self._errors.append(msg)

    def _fatal(self, msg):
        self._error("FATAL - " + msg)
        self._failed = True

    def _warn(self, msg):
        self._warnings.append(msg)

    # TODO: we should be able to get avg time per item
    # and then do est. time remaining (so we need to set sub items afterall)
    def _progress(self, completed, total):
        self._percent_done = completed / total

        elapsed = timestamp() - self._start_time
        avg_time_per = elapsed / completed
        est_time_left = (avg_time_per * (total - completed)) / 1000

        print("Progress {0}/{1} - est. time remaining {2} seconds".format(completed, total, est_time_left))


    def _run(self):
        raise NotImplementedError("Subclass must implement _run method")

    def _dbinsert(self, collection, items):
        db.insert(collection, items)

        # TODO: error handling
        self._db_inserts += 1

    def run(self):
        self._running = True
        self._start_time = timestamp()

        print("Running ingestion task:", self._name)
        self._run()

        self._end_time = timestamp()
        self._running = False

        elapsed_time = self._end_time - self._start_time

        sf = "Failure" if self._failed else "Success"
        print("Ingestion task {0} ({1})".format(self._name, sf))
        print("Elapsed time (seconds):", elapsed_time / 1000)
        print("Database inserts:", self._db_inserts)

        ec = len(self._errors)
        wc = len(self._warnings)
        if ec > 0:
            print("errors ({0}):".format(ec))
            for e in self._errors:
                print("  *", e)
        if wc > 0:
            print("warnings ({0}):".format(wc))
            for w in self._warnings:
                print("  *", w)

        # TODO:
        # write a row to ingestion table (start time, end time,
        # elapsed time, errors, processed, list of import fns run)


class ImportCoinListTask(IngestionTask):
    def __init__(self):
        super().__init__()
        self._name = "Import-Coins"

    def _run(self):
        # TODO: periodically we need to make sure the reddit's haven't changed
        # add a param that will just force a full update of all and run every few days

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
                coin["subreddit"] = get_subreddit(cmc_id)
            except Exception as err:
                # TODO: try looking it up on cryptocompare too, maybe that should be our first source of data
                print("Error getting subreddit: ", err)
                self._error("Error getting subreddit: " + str(err))
                missing_subreddits.add(symbol)

            coin["_id"] = coin["symbol"]
            self._dbinsert("coins", coin)

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
    # TODO: how to do timing in clean generic way
    # TODO: write a record to the ingestion collection

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