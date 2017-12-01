from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import plotly
from plotly.graph_objs import Scatter, Layout


# TODO: database/util should be moved to a common/util package
from ingestion import util, database as db

TRADE_FEE = .0025
TRADE_SLIPPAGE = .03


# TODO: do all calcs in BTC too, or ETH
class Position:
    def __init__(self, coin_id, amount, coin_price):
        self.coin_id = coin_id
        self.amount = amount
        self.coin_buy_price = coin_price
        self.coin_sell_price = None
        self.full_sell_price = None
        self.closed = False

        # Add slippage to full buy cost
        self.full_buy_price = self.amount * self.coin_buy_price
        self.full_buy_price += self.full_buy_price * TRADE_SLIPPAGE

        # and the trade fee
        fee = self.full_buy_price * TRADE_FEE
        self.full_buy_price += fee
        self.fees_paid = fee

    def close(self, coin_price):
        if self.closed:
            return

        self.coin_sell_price = coin_price

        # Reduce sell value by slippage
        self.full_sell_price = self.amount * self.coin_sell_price
        self.full_sell_price -= self.full_sell_price * TRADE_SLIPPAGE

        # and reduce by fee
        fee = self.full_sell_price * TRADE_FEE
        self.full_sell_price -= fee
        self.fees_paid += fee

        self.closed = True

    def current_value(self, current_price):
        base = self.amount * current_price
        base -= base * TRADE_SLIPPAGE
        base -= base * TRADE_FEE
        return base

    def profit(self):
        return self.full_sell_price - self.full_buy_price

    def pct_profit(self):
        return self.profit() / self.full_buy_price


class Signal(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3
    NONE = 4


class Strategy:
    def generate_signals(self, coin_id, dataframe):
        raise NotImplementedError("Must implement generate_signals")

    def allocation(self, current_cash):
        raise NotImplementedError("Must implement allocation")


class BuyAndHoldStrategy(Strategy):
    def __init__(self, coin_ids, buy_date, sell_date):
        self.coin_ids = coin_ids
        self.buy_date = buy_date
        self.sell_date = sell_date
        self.starting_cash = None

    def generate_signals(self, coin_id, df):
        if coin_id in self.coin_ids:
            df = pd.DataFrame(index=df.index)
            df["signals"] = Signal.NONE
            df["allocation"] = 0

            df.loc[self.buy_date:self.sell_date, "signals"] = Signal.HOLD
            df.loc[self.buy_date, "signals"] = Signal.BUY
            df.loc[self.sell_date, "signals"] = Signal.SELL

            # TODO: there must be a better way to do position sizing
            df.loc[self.buy_date, "allocation"] = 1 / len(self.coin_ids)

            return df

    def allocation(self, available_cash):
        if not self.starting_cash:
            self.starting_cash = available_cash

        return self.starting_cash / len(self.coin_ids)


class RedditGrowthStrategy(Strategy):
    def generate_signals(self, coin_id, df):
        df_signals = pd.DataFrame(index=df.index)
        df_change = df.pct_change(1)

        holding = False
        for index, row in df_change.iterrows():
            if not holding and row["reddit_subs"] > .05:
                df_signals.loc[index, "signals"] = Signal.BUY
                holding = True
            if holding and row["reddit_subs"] < .05:
                df_signals.loc[index, "signals"] = Signal.SELL
                holding = False

        return df_signals

    def allocation(self, current_cash):
        size = current_cash / 10
        size = min(size, 5000)
        return size


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class BackTest:
    def __init__(self, name, coins, data_frames, strategy):
        self.name = name
        self.coins = coins
        self.data_frames = data_frames
        self.strategy = strategy
        self.signals = {}
        self.start_date = None
        self.end_date = None
        self.current_day = None

        # TODO:
        # mapping coin_id to position limits us to a single position for a coin
        # down the road we'll want to remove this restriction so we can build positions over time
        self.positions = {}
        self.closed_positions = []

        self.initial_cash = 1000
        self.value_over_time = pd.DataFrame(columns=["date", "cash", "equity"])

    def current_cash(self):
        if len(self.value_over_time) == 0:
            return self.initial_cash

        return self.value_over_time.iloc[-1].cash

    def current_equity(self):
        if len(self.value_over_time) == 0:
            return 0

        return self.value_over_time.iloc[-1].cash

    def generate_signals(self):
        for coin_id, df in self.data_frames.items():
            signals = self.strategy.generate_signals(coin_id, df)
            self.signals[coin_id] = signals

    def update_equity(self, date, current_cash):
        total_value = 0
        for coin_id, pos in self.positions.items():

            # TODO: we shouldn't need to try catch here if we've properly cleaned the data
            # fix upstream setup errors and remove
            try:
                current_price = self.data_frames[coin_id].loc[date]["close"]
            except:
                print("ERROR: missing days price")
                current_price = 0

            total_value += pos.current_value(current_price)

        self.value_over_time.loc[len(self.value_over_time)] = [date, current_cash, total_value]

    def run(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.current_day = self.start_date

        while self.tick():
            pass

    def tick(self):
        if self.current_day > self.end_date:
            #assert(len(self.positions) == 0)
            return False

        current_cash = self.current_cash()
        for coin_id, df in self.data_frames.items():
            signals = self.signals[coin_id]
            if signals is None:
                # No actions to take for this coin
                continue

            # TODO: we need better handling around missing data, and date ranges the coins existed
            try:
                days_signal = signals.loc[self.current_day]["signals"]
            except Exception:
                continue

            day = df.loc[self.current_day]
            close_price = day["close"]

            if days_signal == Signal.BUY:
                # TODO: config for position sizing, and it needs to take into account fees and slip, real price
                # and strategies should be able to do position sizing, or have strengths for signals
                # currently this only works with a buy and hold strategy
                #percent = signals.loc[self.current_day]["allocation"]
                #amount = self.initial_cash * percent / close_price

                #buy_cash = current_cash / 10
                #buy_cash = min(buy_cash, 5000)

                buy_cash = self.strategy.allocation(current_cash)

                amount = buy_cash / close_price

                pos = Position(coin_id, amount, close_price)
                self.positions[coin_id] = pos

                current_cash -= pos.full_buy_price

            elif days_signal == Signal.SELL:
                # TODO: remove this
                if coin_id not in self.positions:
                    continue

                assert(coin_id in self.positions)

                pos = self.positions[coin_id]
                pos.close(close_price)
                self.closed_positions.append(pos)
                del self.positions[coin_id]

                current_cash += pos.full_sell_price

        # TODO: if we just sold, then this equity update seems a bit wonky

        self.update_equity(self.current_day, current_cash)
        self.current_day += timedelta(days=1)

        return True


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

        prev_date = None
        for price in prices:
            if prev_date and price["date"] - prev_date > timedelta(days=1):
                print("missed previous day(s), curr={}, prev={}".format(price["date"], prev_date))

            price_data["date"].append(price["date"])
            price_data["open"].append(price["open"])
            price_data["close"].append(price["close"])

            prev_date = price["date"]

        for sub in subs:
            social_data["date"].append(sub["date"])
            social_data["reddit_subs"].append(sub["reddit_subscribers"])

        dfp = pd.DataFrame(price_data, columns=["date", "open", "close"])
        dfs = pd.DataFrame(social_data, columns=["date", "reddit_subs"])
        df = pd.merge(dfp, dfs, on="date")

        # make date the index
        df.index = df['date']
        del df['date']

        if len(df) == 0:
            # TODO: handle this cleaner, this also breaks progress count
            print("ERROR: No data for coin", coin["symbol"])
            continue

        datetime_index = [df.index.min(), df.index.max()]
        s2 = pd.Series(None, datetime_index)
        df["open"] = df["open"].combine_first(s2)
        df["open"].interpolate()
        df["close"] = df["close"].combine_first(s2)
        df["close"].interpolate()
        df["reddit_subs"] = df["reddit_subs"].combine_first(s2)
        df["reddit_subs"].interpolate()

        if df.isnull().values.any():
            raise Exception("missing data")

        data_frames[coin["_id"]] = df

        progress += 1
        print("progress: {} / {}".format(progress, len(coins)))

        # TODO: for now test on a small sub set (for quicker iteration)
        #if progress >= 100:
        #    break

    return coins, data_frames


def create_equity_graph(backtest):
    data = [Scatter(x=backtest.value_over_time.date, y=backtest.value_over_time.equity, name="Equity"),
            Scatter(x=backtest.value_over_time.date, y=backtest.value_over_time.cash, name="Cash")]
    plotly.offline.plot(data)


def create_equity_compare_graph(backtests):
    data = []
    for bt in backtests:
        bt.value_over_time.equity_and_cash = bt.value_over_time.equity + bt.value_over_time.cash
        s = Scatter(x=bt.value_over_time.date, y=bt.value_over_time.equity_and_cash, name=bt.name)
        data.append(s)

    plotly.offline.plot(data)
