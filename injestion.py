from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp


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

    for coin in stored_coins:
        stored_symbols.add(coin["symbol"])

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
    print("Total coins", len(current_coins))
    print("Added", len(added_symbols), "new coins")
    print("Missing subreddits", len(missing_subreddits), missing_subreddits)

    # TODO: errors

    return coins


if __name__ == '__main__':
    start_time = timestamp()
    processed = 0
    new_coins = 0
    errors = 0
    warnings = 0

    coins = update_coin_list()

    for symbol in coins:
        print("Processing", symbol)

        stats = get_current_stats(subreddit)
        print("Current reddit Stats:\n", stats)

        print("Saving historic price and social data")
        save_historic_data(cmcId, symbol)
        save_historic_stats(subreddit, symbol)

        processed += 1
        print("Processed", processed, "/", total)
        print("")


        break


    end_time = timestamp()
    elapsed_time = end_time - start_time

    print("elapsed time (ms):", elapsed_time)