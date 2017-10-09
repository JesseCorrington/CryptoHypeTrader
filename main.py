from coinmarketcap import *
from reddit import *


if __name__ == '__main__':
    coins = get_coin_list()

    #subreddit = get_subreddit(coins["link"]["id"])
    #print(subreddit)

    #prices = get_historical_prices(coins["link"]["id"])
    #print(prices)

    #stats = get_current_stats("bitcoin")
    #print(stats)

    stats = get_historical_stats("loopring")
    print(stats)
