from coinmarketcap import *
from reddit import *
import database as db
from util import timestamp

def update_coin_list():
    print("Updating coins list")

    coins = get_coin_list()

    total = len(coins)

    current_coins = db.get_coins()
    current_symbols = set()
    for coin in current_coins:
        current_symbols.add(coin["symbol"])

    print("current coins")

    for doc in current_coins:
        print(doc)

    # TODO: periodically we need to make sure the reddit's haven't changed, so do a scan all

    # TODO: for all new coins lookup reddit and any other general info
    new_coins = coins

    for symbol in coins:
        if symbol in current_symbols:
            continue

        coin = coins[symbol]
        cmcId = coin["cmc_id"]

        try:
            coin["subreddit"] = get_subreddit(cmcId)
        except Exception as err:
            # TODO: try looking it up on cryptocompare too, maybe that should be our first source of data
            print("Error getting subreddit: ", err)

        db.insert_coin(coin)


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