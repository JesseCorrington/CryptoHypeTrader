from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp
from datetime import date


# TODO: periodically we need to make sure the reddit's haven't changed
# add a param that will just force a full update of all and run every few days
def update_coin_list():
    current_coins = get_coin_list()

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
            missing_subreddits.add(symbol)

        db.insert_coin(coin)
        added_symbols.add(symbol)
        print("Added coin", symbol)

        processed += 1
        print("Progress", processed, "/", len(new_symbols))

    if len(new_symbols) > 0:
        print("Total coins", len(current_coins))
        print("Added", len(added_symbols), "new coins")
        print("Missing subreddits", len(missing_subreddits))
    else:
        print("No new coins to add")

    # TODO: errors

    return current_coins


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
    tasks = {
        "Update coin list": update_coin_list,
        "Update historic prices": save_historic_prices,
        "Update historic reddit stats": save_historic_reddit_stats
    }

    for name, task in tasks.items():
        task_start = timestamp()
        print("Running ingestion task:", name)

        # TODO: write error and warning count to db
        errors = task()
        task_elapsed = timestamp() - task_start

        print("Ingestion task", name, "completed in", task_elapsed / 1000, "seconds")
        # TODO: write a row to ingestion table (start time, end time, elapsed time, errors, processed, list of import fns run)

    elapsed_time = timestamp() - start_time

    print("Ingestion complete, elapsed time (ms):", elapsed_time)


if __name__ == '__main__':
    run_all()