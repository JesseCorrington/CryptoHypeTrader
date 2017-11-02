from coinmarketcap import *
from reddit import *


if __name__ == '__main__':
    coins = get_coin_list()

    cmcId = coins["btc"]["id"]
    coinSymbol = coins["btc"]["symbol"]

    subreddit = get_subreddit(cmcId)
    print("reddit.com/r/" + subreddit)

    prices = get_historical_prices(cmcId)
    print("Historical Prices:\n", prices)

    stats = get_current_stats(subreddit)
    print("Historical Stats:\n", stats)

    stats = get_historical_stats(subreddit)
    print("Current Stats:\n", stats)


    save_historic_data(cmcId, coinSymbol)
    save_historic_stats(subreddit, coinSymbol)