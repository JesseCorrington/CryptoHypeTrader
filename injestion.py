from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp


# TODO: periodically we need to make sure the reddit's haven't changed, so do a scan all
def update_coin_list():
    print("Updating coins list")

    current_coins = get_coin_list()

    stored_coins = db.get_coins()
    stored_symbols = set()
    added_symbols = set()
    missing_subreddit = set()

    for coin in stored_coins:
        stored_symbols.add(coin["symbol"])

    for symbol in current_coins:
        if symbol in stored_symbols:
            # We already have the data about this coin
            continue

        coin = current_coins[symbol]
        cmc_id = coin["cmc_id"]

        try:
            coin["subreddit"] = get_subreddit(cmc_id)
        except Exception as err:
            # TODO: try looking it up on cryptocompare too, maybe that should be our first source of data
            print("Error getting subreddit: ", err)
            missing_subreddit.add(symbol)

        db.insert_coin(coin)
        added_symbols.add(symbol)
        print("Added coin", symbol)

    print("Updatting coin list completed")
    print("Total coins", len(current_coins))
    print("Added", len(added_symbols), "new coins")
    print("Missing subreddits", len(missing_subreddit))

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