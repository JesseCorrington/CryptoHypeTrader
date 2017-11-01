from coinmarketcap import *
from reddit import *


if __name__ == '__main__':
    coins = get_coin_list()

    linkId = coins["btc"]["id"]

    subreddit = get_subreddit(linkId)
    print("reddit.com/r/" + subreddit)

    prices = get_historical_prices(linkId)
    print("Historical Prices:\n", prices)

    stats = get_current_stats(subreddit)
    print("Historical Stats:\n", stats)

    stats = get_historical_stats(subreddit)
    print("Current Stats:\n", stats)


    #save_historic_data(linkId, coins["link"]["symbol"])

    #save_historic_stats(subreddit, coins["link"]["symbol"])