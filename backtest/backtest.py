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
            if progress >= 5:
                break

        # TODO: now add a couple columns to capture ranking
        # subreddit growth
        # subreddit growth / total subreddit growth
        # growth rank



    def run(self):
        # init start and end dates
        # iterate over dates
        # for each date, find the set of available coins
        # rank coins by reddit growth
        # buy coin at open, sell at next open

        start_date = datetime(2015, 1, 1)
        end_date = datetime(2017, 11, 1)

        positions = []

        start_money = 1000
        current_money = start_money

        for current_day in daterange(start_date, end_date):
            daily_growth = []
            for coin in self.data:
                df = coin["df"]
                dfp = coin["dfp"]

                try:
                    day = df.loc[current_day]
                    day_change = dfp.loc[current_day]

                except KeyError:
                    # TODO: prob just this coin wasn't active yet, can we prep data better
                    continue

                # close our position if we had one from yesterday
                i = 0
                for pos in positions:
                    if pos["coin"]["_id"] == coin["coin_id"]:
                        sell_price = day["open"]
                        change = (sell_price - pos["buy_price"]) * pos["amount"]
                        current_money += change
                        print(pos["coin"]["symbol"], "gain/loss of", change)
                        del positions[i]
                        break

                    i += 1

                rs = day_change["reddit_subs"]
                daily_growth.append({"coin_id": coin["coin_id"], "sub_growth": rs})

            daily_growth.sort(key=lambda x: x["sub_growth"], reverse=True)

            portfolio_size = 5
            top_pics = daily_growth[:5]

            print("Current money", current_money)

            print(current_day, "Pics ------------------")
            #assert (len(positions) == 0)

            # TODO: this is an issue if the position didn't get closed above
            positions = []

            for pick in top_pics:
                cid = pick["coin_id"]
                coin = self.coinid_map[cid]

                # TODO: in reality we'd not reinvestie 100% each day, but take out profits
                allocation = current_money / portfolio_size
                amount = allocation / day["open"]

                # TODO: this is getting the same values for all the coins,
                # because day is not correct

                positions.append({"coin": coin, "buy_price": day["open"], "amount": amount})

                print(coin["symbol"], "{0:.0f}%".format(pick["sub_growth"] * 100), amount)


# taking the top 5 daily
# Total gain 30368.4297886

# taking the bottom 5 daily
# Total gain 10805.1391073

# buying a random coin each day

# just holding bitcoin

# holding all coins
