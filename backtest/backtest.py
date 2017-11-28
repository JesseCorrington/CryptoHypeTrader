from datetime import datetime, timedelta
import pandas as pd
import pymongo

# TODO: database/util should be moved to a common/util package
from ingestion import util, database as db

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


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


class BackTester():
    def __init__(self):
        self.data = []
        self.coins = []

    @staticmethod
    def __data_for_coin(data, coin):
        data = [x for x in data if x["coin_id"] == coin["_id"]]

        # TODO: why doesn't db index take care of this already
        # likely has to do with indexing on id and price
        data.sort(key=lambda x: x["date"])
        return data

    def load_data(self):
        self.coins = db.get_coins({"subreddit": {"$exists": True}})

        self.coinid_map = util.list_to_dict(self.coins, "_id")

        all_prices = db.MONGO_DB.historical_prices.find()
        all_reddit_subs = db.MONGO_DB.historical_social_stats.find()

        all_prices = list(all_prices)
        all_reddit_subs = list(all_reddit_subs)

        # build a pandas data frame (datetime, price, reddit subs)
        progress = 0
        for coin in self.coins:
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

            # TODO: if our frame contained data about the overall market grwoth (reddit and price)
            # then we should be able to more easily determine daily rank

            dfp = pd.DataFrame(price_data, columns=["date", "open", "close"])
            dfs = pd.DataFrame(social_data, columns=["date", "reddit_subs"])
            df = pd.merge(dfp, dfs, on="date")

            # ensure correct date type
            #df['date'] = pd.to_datetime(df['date'])

            # make date the index
            df.index = df['date']
            del df['date']

            self.data.append({"coin_id": coin["_id"], "df": df, "dfp": df.pct_change(1)})

            progress += 1
            print("progress: {} / {}".format(progress, len(self.coins)))

            # TODO: for now test on a small sub set (for quicker iteration)
            #if progress >= 10:
            #    break

    def run(self):
        # init start and end dates
        # iterate over dates
        # for each date, find the set of available coins
        # rank coins by reddit growth
        # buy coin at open, sell at next open

        start_date = datetime(2015, 1, 1)
        end_date = datetime(2017, 11, 1)
        for current_day in daterange(start_date, end_date):

            daily_growth = []
            for coin in self.data:
                dfp = coin["dfp"]

                try:
                    day = dfp.loc[current_day]
                except KeyError:
                    # # TODO: prob just this coin wasn't active yet, can we prep data better
                    continue

                rs = day["reddit_subs"]
                daily_growth.append({"coin_id": coin["coin_id"], "sub_growth": rs})

            daily_growth.sort(key=lambda x: x["sub_growth"], reverse=True)

            top_pics = daily_growth[:3]

            print(current_day, "Pics ------------------")
            for pick in top_pics:
                cid = pick["coin_id"]
                coin = self.coinid_map[cid]
                print(coin["symbol"], "{0:.0f}%".format(pick["sub_growth"] * 100))
