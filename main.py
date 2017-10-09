from coinmarketcap import *
from reddit import *
from database import *

if __name__ == '__main__':
    coins = get_coin_list()

    linkId = coins["link"]["id"]

    subreddit = get_subreddit(linkId)
    print(subreddit)

    prices = get_historical_prices(linkId)
    print(prices)

    stats = get_current_stats(subreddit)
    print(stats)

    stats = get_historical_stats(subreddit)
    print(stats)
