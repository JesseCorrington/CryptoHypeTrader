from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import plotly
from plotly.graph_objs import Scatter, Layout


# TODO: database/util should be moved to a common/util package
from ingestion import util, database as db


class Position:
    def __init__(self, coin_id, amount, buy_price):
        self.coin_id = coin_id
        self.amount = amount
        self.buy_price = buy_price
        self.sell_price = None
        self.closed = False

    def close(self, sell_price):
        self.sell_price = sell_price
        self.closed = True

    # TODO: fees and slippage
    # TODO: do all calcs in BTC too, or ETH
    # TODO: value seems like the wrong word too

    def buy_value(self):
        return self.amount * self.buy_price

    def current_value(self, current_price):
        return self.amount * current_price

    def current_profit(self, current_price):
        return self.current_value(current_price) - self.buy_value()

    def sell_value(self):
        return self.amount * self.sell_price

    def sell_profit(self):
        return self.sell_value() - self.buy_value()


class Portfolio:
    def __init__(self):
        self.holdings = []
    pass


class Signal(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3
    NONE = 4


class Strategy:
    def generate_signals(self, coin_id, dataframe):
        raise NotImplementedError("Must implement generate_signals")


class BuyAndHoldStrategy(Strategy):
    def __init__(self, coin_ids, buy_date, sell_date):
        self.coin_ids = coin_ids
        self.buy_date = buy_date
        self.sell_date = sell_date

    def generate_signals(self, coin_id, df):
        if coin_id in self.coin_ids:
            df = pd.DataFrame(index=df.index)
            df["signals"] = Signal.NONE

            df.loc[self.buy_date:self.sell_date]["signals"] = Signal.HOLD
            df.loc[self.buy_date]["signals"] = Signal.BUY
            df.loc[self.sell_date]["signals"] = Signal.SELL

            return df


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


class BackTester:
    def __init__(self, name, coins, data_frames):
        self.name = name
        self.coins = coins
        self.data_frames = data_frames
        self.signals = {}
        self.slippage_percent = 0.02
        self.fee_percent = 0.0025

        # TODO: this needs to be configurable
        self.start_date = datetime(2016, 11, 1)
        self.end_date = datetime(2017, 11, 1)
        self.current_day = self.start_date

        # TODO:
        # mapping coin_id to position limits us to a single position for a coin
        # down the road we'll want to remove this restriction so we can build positions over time
        self.positions = {}
        self.closed_positions = []

        self.initial_cash = 1000
        self.value_over_time = pd.DataFrame(columns=["date", "cash", "equity"])


    def estimate_price(self, price, amount, buy_or_sell):
        total = price * amount

        slippage = total * self.slippage_percent
        if buy_or_sell == "buy":
            total += slippage
        else:
            total -= slippage

        total += total * self.fee_percent
        return total

    def current_cash(self):
        if len(self.value_over_time) == 0:
            return self.initial_cash

        return self.value_over_time.iloc[-1].cash

    def current_equity(self):
        if len(self.value_over_time) == 0:
            return 0

        return self.value_over_time.iloc[-1].cash

    def generate_signals(self, strategy):
        for coin_id, df in self.data_frames.items():
            signals = strategy.generate_signals(coin_id, df)
            self.signals[coin_id] = signals

    def update_equity(self, date, current_cash):
        total_value = 0
        for coin_id, pos in self.positions.items():

            # TODO: this feels kinda ugly
            current_price = self.data_frames[coin_id].loc[date]["open"]
            total_value += pos.current_value(current_price)

        self.value_over_time.loc[len(self.value_over_time)] = [date, current_cash, total_value]

    def tick(self):
        if self.current_day > self.end_date:
            assert(len(self.positions) == 0)

            for pos in self.closed_positions:
                print("buy value", pos.buy_value())
                print("sell value", pos.sell_value())
                print("profit", pos.sell_profit())

            return False

        current_cash = self.current_cash()
        for coin_id, df in self.data_frames.items():
            signals = self.signals[coin_id]
            if signals is None:
                # No actions to take for this coin
                continue

            days_signal = signals.loc[self.current_day]["signals"]
            day = df.loc[self.current_day]
            open_price = day["open"]

            if days_signal == Signal.BUY:
                # TODO: config for position sizing, and it needs to take into account fees and slip, real price
                # and strategies should be able to do position sizing, or have strengths for signals
                # currently this only works with a buy and hold strategy
                amount = current_cash / open_price

                pos = Position(coin_id, amount, open_price)
                self.positions[coin_id] = pos

                current_cash -= pos.buy_value()

            elif days_signal == Signal.SELL:
                assert(coin_id in self.positions)

                pos = self.positions[coin_id]
                pos.close(open_price)
                self.closed_positions.append(pos)
                del self.positions[coin_id]

                current_cash += pos.sell_value()

        self.update_equity(self.current_day, current_cash)
        self.current_day += timedelta(days=1)

        return True




    def run(self):
        # init start and end dates
        # iterate over dates
        # for each date, find the set of available coins
        # rank coins by reddit growth
        # buy coin at open, sell at next open

        start_date = datetime(2016, 11, 1)
        end_date = datetime(2017, 11, 1)

        positions = []

        start_money = 100000
        current_money = start_money
        money_in_positions = 0

        total_fees_paid = 0


        # TODO: looks like there may be some issues with df padding
        # so it looks like currencies are alive that aren't

        for current_day in daterange(start_date, end_date):
            #print(current_day)

            daily_growth = []
            for coin_id, coin in self.data_frames.items():
                df = coin["df"]
                dfp = coin["dfp"]

                try:
                    day = df.loc[current_day]
                    day_change = dfp.loc[current_day]
                    prev_day = df.loc[current_day - timedelta(days=1)]
                    reddit_growth = day["reddit_subs"] - prev_day["reddit_subs"]


                except KeyError:
                    # TODO: prob just this coin wasn't active yet, can we prep data better
                    continue

                # close our position if we had one from yesterday
                i = 0
                for pos in positions:
                    if pos["coin"]["_id"] == coin_id:
                        pos["days"] += 1

                        # TODO: estimate slippage based on market size
                        est_sell = self.estimate_price(day["open"], pos["amount"], "sell")
                        gain = (est_sell - pos["est_price"])

                        percent_gain = gain / pos["est_price"]

                        if percent_gain > .1 or pos["days"] > 10 or current_day >= end_date - timedelta(days=5):
                            current_money += est_sell

                            # TODO: we need to update money in positons daily
                            money_in_positions -= pos["est_price"]

                            print("POSITION CLOSE: {}, buy: {}, est_sell: {}, gain {}".format(
                                pos["coin"]["symbol"], pos["est_price"], est_sell, gain
                            ))

                            del positions[i]
                            break

                            # TODO: doh, this break only allows us to close 1 position each day

                    i += 1

                rs = day_change["reddit_subs"]
                daily_growth.append({"coin_id": coin_id, "sub_growth": rs})

            daily_growth.sort(key=lambda x: x["sub_growth"], reverse=True)

            portfolio_size = 20
            top_pics = daily_growth[:portfolio_size]

            print("Current money, in pos", current_money, money_in_positions)

            # TODO: don't open position on the last day

            if current_money <= 10:
                continue

            for pick in top_pics:
                cid = pick["coin_id"]
                coin = self.coinid_map[cid]

                skip = False
                for p in positions:
                    if cid == p["coin"]["_id"]:
                        skip = True
                        break

                if skip:
                    continue

                #if skip or pick["sub_growth"] < .07:
                #    continue

                df = self.data_frames[cid]["df"]
                day = df.loc[current_day]

                allocation = current_money / 10

                amount = allocation / day["open"]

                est_price = self.estimate_price(day["open"], amount, "buy")
                positions.append({"coin": coin, "est_price": est_price, "amount": amount, "days": 0})

                print("POSITION OPEN: symbol {}, sub_growth {}, est_price {}, amount {}".format(
                    coin["symbol"], "{0:.0f}%".format(pick["sub_growth"] * 100), est_price, amount
                ))

                money_in_positions += est_price
                current_money -= est_price

        for p in positions:
            print(p)

        print("final balance", current_money)
        print("total fees paid", total_fees_paid)


def data_for_coin(data, coin):
    data = [x for x in data if x["coin_id"] == coin["_id"]]

    # TODO: why doesn't db index take care of this already
    # likely has to do with indexing on id and price
    data.sort(key=lambda x: x["date"])
    return data


def load_data():
    coins = db.get_coins({"subreddit": {"$exists": True}})

    # TODO: would be cleaner if the frames were stored in each coin maybe
    data_frames = {}

    all_prices = db.MONGO_DB.historical_prices.find()
    all_reddit_subs = db.MONGO_DB.historical_social_stats.find()

    all_prices = list(all_prices)
    all_reddit_subs = list(all_reddit_subs)

    # build a pandas data frame (datetime, price, reddit subs)
    progress = 0
    for coin in coins:
        prices = data_for_coin(all_prices, coin)
        subs = data_for_coin(all_reddit_subs, coin)

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

        if df.isnull().values.any():
            # TODO: use linear interpolation for small gaps
            raise Exception("missing data")

        data_frames[coin["_id"]] = df

        progress += 1
        print("progress: {} / {}".format(progress, len(coins)))

        # TODO: for now test on a small sub set (for quicker iteration)
        if progress >= 2:
            break

    # TODO: now add a couple columns to capture ranking
    # subreddit growth
    # subreddit growth / total subreddit growth
    # growth rank

    return coins, data_frames

def create_equity_graph(backtest):
    data = [Scatter(x=backtest.value_over_time.date, y=backtest.value_over_time.equity),
            Scatter(x=backtest.value_over_time.date, y=backtest.value_over_time.cash)]
    plotly.offline.plot(data)



def create_equity_compare_graph(backtests):
    data = []
    for bt in backtests:
        bt.value_over_time.equity_and_cash = bt.value_over_time.equity + bt.value_over_time.cash
        s = Scatter(x=bt.value_over_time.date, y=bt.value_over_time.equity_and_cash, name=bt.name)
        data.append(s)

    plotly.offline.plot(data)
