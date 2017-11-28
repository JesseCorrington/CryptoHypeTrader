import pandas as pd
import pymongo

# TODO: database should be moved to a common/util package
from ingestion import database as db

class Holding:
    def __init__(self, coin_id, amount, buy_price):
        self.coin_id = coin_id
        self.amount = amount
        self.buy_price = buy_price


class Portfolio:
    def __init__(self):
        self.holdings = []
    pass


class Strategy:
    pass


class BackTester():
    def __init__(self):
        self.series = []
        self.coins = []
        self.prices = []
        self.reddit_subs = []

    @staticmethod
    def __data_for_coin(data, coin):
        data = [x for x in data if x["coin_id"] == coin["_id"]]

        # TODO: why doesn't db index take care of this already
        # likely has to do with indexing on id and price
        data.sort(key=lambda x: x["date"])
        return data

    def load_data(self):
        coins = db.get_coins({"subreddit": {"$exists": True}})
        all_prices = db.MONGO_DB.historical_prices.find()
        all_reddit_subs = db.MONGO_DB.historical_social_stats.find()

        all_prices = list(all_prices)
        all_reddit_subs = list(all_reddit_subs)

        # build a pandas data frame (datetime, price, reddit subs)
        for coin in coins:
            prices = self.__data_for_coin(all_prices, coin)
            subs = self.__data_for_coin(all_reddit_subs, coin)

            price_data = {
                "date": [],
                "open": [],
                "close": [],
            }

            social_data = {
                "date": [],
                "reddit_subs": []
            }

            for price in prices:
                price_data["date"].append(price["date"])
                price_data["open"].append(price["open"])
                price_data["close"].append(price["close"])

            for sub in subs:
                social_data["date"].append(sub["date"])
                social_data["reddit_subs"].append(sub["reddit_subscribers"])

            dfp = pd.DataFrame(price_data, columns=["date", "open", "close"])
            dfs = pd.DataFrame(social_data, columns=["date", "reddit_subs"])
            all = pd.merge(dfp, dfs, on="date")

    def tick(self):
        pass

    def marketValue(self, base="usd"):
        pass
