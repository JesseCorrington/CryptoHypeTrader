from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp
from datetime import date


# TODO: periodically we need to make sure the reddit's haven't changed
# add a param that will just force a full update of all and run every few days
def update_coin_list():
    print("Updating coins list")

    start_time = timestamp()

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

    end_time = timestamp()
    elapsed_time = (end_time - start_time) / 1000

    print("Updating coin list completed in", elapsed_time, "seconds")

    if len(new_symbols) > 0:
        print("Total coins", len(current_coins))
        print("Added", len(added_symbols), "new coins")
        print("Missing subreddits", len(missing_subreddits))
    else:
        print("No new coins to add")

    # TODO: errors

    return current_coins


def save_historic_prices():
    # TODO: we may not even need this
    coins = db.get_coins()
    latest_prices = db.get_latest_prices()
    coins_to_update = {}

    for symbol in coins:
        coin = coins[symbol]
        start_time = datetime.date(2011, 1, 1)

        if symbol in latest_prices:
            most_recent = latest_prices[symbol]["date"]
            today = date.today()

            if most_recent.year == today.year and most_recent.month == today.month and most_recent.day == today.day - 1:
                continue

            start_time = most_recent + datetime.timedelta(days=1)

        coins_to_update[symbol] = start_time


    # TODO: this is slightly broken, because it will continue to think we have missing data for coins
    # that are dead (https://coinmarketcap.com/currencies/paypeer/)
    # or maybe they don't always get updated on cmc
    for symbol in coins_to_update:
        coin = coins[symbol]
        start_time = coins_to_update[symbol]

        all_prices = get_historical_prices(coin["cmc_id"], start=start_time)

        if all_prices:
            for day in all_prices:
                day["symbol"] = coin["symbol"]

            db.insert_prices(all_prices)

            print("added all prices for", coin["symbol"])
        else:
            print("Error: no price data found", symbol, start_time)


def save_historic_reddit_stats():
    #daily_stats = get_historical_stats(subreddit, symbol)
    #db.insert_historic_social_stats(daily_stats)

    coins = db.get_coins()
    coins = [x for x in coins if "subreddit" in x]

    # TODO: start by making a list of the missing data similar to when we get the coin list
    # then we can report progress and time remaining properly
    for coin in coins:
        get_historical_stats(coin["subreddit"], coin["symbol"])


if __name__ == '__main__':
    start_time = timestamp()

    # TODO: where does this belong, is it okay to run it every time?
    db.create_indexes()

    update_coin_list()
    save_historic_prices()
    save_historic_reddit_stats()

    end_time = timestamp()
    elapsed_time = end_time - start_time

    # TODO: write a row to injestion table (start time, end time, elapsed time, errors, processed, list of import fns run)

    print("Injestion complete, elapsed time (ms):", elapsed_time)