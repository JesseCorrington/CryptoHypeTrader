from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import plotly
from plotly.graph_objs import Scatter, Layout
from random import randint


# TODO: database/util should be moved to a common/util package
from ingestion import util, database as db

TRADE_FEE = .0025
TRADE_SLIPPAGE = .02


# TODO: do all calcs in BTC too, or ETH
class Position:
    def __init__(self, coin_id, amount, coin_price, date):
        self.coin_id = coin_id
        self.amount = amount
        self.coin_buy_price = coin_price
        self.buy_date = date
        self.coin_sell_price = None
        self.full_sell_price = None
        self.closed = False
        self.sell_date = None

        # Add slippage to full buy cost
        self.full_buy_price = self.amount * self.coin_buy_price
        self.full_buy_price += self.full_buy_price * TRADE_SLIPPAGE

        # and the trade fee
        fee = self.full_buy_price * TRADE_FEE
        self.full_buy_price += fee
        self.fees_paid = fee

    def close(self, coin_price, date):
        if self.closed:
            return

        self.coin_sell_price = coin_price
        self.sell_date = date

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
        if self.coin_ids == "all" or coin_id in self.coin_ids:
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

# TODO: only trade coins with high enough market cap
# and size positions based on market cap to reduce slippage
class RedditGrowthStrategy(Strategy):
    def __init__(self, min_market_cap, sub_growth_threshold):
        self.min_market_cap = min_market_cap
        self.sub_growth_threshold = sub_growth_threshold

    def generate_signals(self, coin_id, df):

        # TODO: the base class should handle creating this for better abstraction
        df_signals = pd.DataFrame(index=df.index)
        df_change = df.pct_change(1)

        holding = False
        buy_price = 1

        for index, row in df_change.iterrows():
            market_cap = df.loc[index, "market_cap"]
            current_price = df.loc[index, "close"]

            profit_percent = (current_price - buy_price) / buy_price

            # TODO: consider stop losses, and add config for threshold, trailing stops too

            if not holding and row["reddit_subs"] > self.sub_growth_threshold and market_cap > self.min_market_cap:
                df_signals.loc[index, "signals"] = Signal.BUY
                holding = True
                buy_price = current_price
            elif holding and (row["reddit_subs"] < self.sub_growth_threshold or profit_percent > 5):
                df_signals.loc[index, "signals"] = Signal.SELL
                holding = False

        return df_signals

    def allocation(self, current_cash):
        size = current_cash / 8
        size = min(size, 10000)
        size = current_cash
        return size


class RandomStrategy(Strategy):
    def generate_signals(self, coin_id, df):
        holding = False
        df_signals = pd.DataFrame(index=df.index)

        for index, row in df.iterrows():
            if not holding and randint(1, 20) == 1:
                df_signals.loc[index, "signals"] = Signal.BUY
                holding = True
            elif holding and randint(1, 20) == 1:
                df_signals.loc[index, "signals"] = Signal.SELL
                holding = False

        return df_signals

    def allocation(self, current_cash):
        size = current_cash / 8
        size = min(size, 10000)
        return size


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class BackTest:
    def __init__(self, name, coins, data_frames, strategy):
        self.name = name
        self.coins = util.list_to_dict(coins, "_id")
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

                # TODO: this is an issue somewhere upstream, just use previous days price for now
                try:
                    current_price = self.data_frames[coin_id].loc[date - timedelta(days=1)]["close"]
                except:
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
                buy_cash = self.strategy.allocation(current_cash)
                amount = buy_cash / close_price

                pos = Position(coin_id, amount, close_price, self.current_day)
                self.positions[coin_id] = pos

                current_cash -= pos.full_buy_price

            elif days_signal == Signal.SELL:
                # TODO: remove this
                if coin_id not in self.positions:
                    continue

                assert(coin_id in self.positions)

                pos = self.positions[coin_id]
                pos.close(close_price, self.current_day)
                self.closed_positions.append(pos)
                del self.positions[coin_id]

                current_cash += pos.full_sell_price

        # TODO: if we just sold, then this equity update seems a bit wonky

        #assert(current_cash > 0)

        self.update_equity(self.current_day, current_cash)
        self.current_day += timedelta(days=1)

        return True

    def create_trades_csv(self, filename):
        import csv
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            headers = ["Symbol",
                       "buy date", "coin buy price", "full buy price",
                       "sell date", "coin sell price", "full sell price",
                       "days held", "profit", "percent profit"]

            writer.writerow(headers)

            for pos in self.positions:
                pass

            for pos in self.closed_positions:
                coin = self.coins[pos.coin_id]
                days_held = pos.sell_date - pos.buy_date
                writer.writerow([coin["symbol"],
                                pos.buy_date, pos.coin_buy_price, pos.full_buy_price,
                                pos.sell_date, pos.coin_sell_price, pos.full_sell_price,
                                days_held.days, pos.profit(), pos.pct_profit()])

    def summary(self):
        if len(self.closed_positions) == 0:
            return {
                "trades": 0,
                "trades_unclosed": len(self.positions)
            }

        trade_data = {
            "days_held": [],
            "profit": [],
            "percent_profit": []
        }

        for pos in self.closed_positions:
            days_held = pos.sell_date - pos.buy_date
            trade_data["days_held"].append(days_held)
            trade_data["profit"].append(pos.profit())
            trade_data["percent_profit"].append(pos.pct_profit())

        df = pd.DataFrame(trade_data, columns=["days_held", "profit", "percent_profit"])

        stats = {
            "trades": len(self.closed_positions),
            "trades_unclosed": len(self.positions),
            "days_mean": df.days_held.mean().days,
            "days_min": df.days_held.min().days,
            "days_max": df.days_held.max().days,
            "profit_mean": df.profit.mean(),
            "profit_min": df.profit.min(),
            "profit_max": df.profit.max(),
            "pct_profit_mean": df.percent_profit.mean(),
            "pct_profit_min": df.percent_profit.min(),
            "pct_profit_max": df.percent_profit.max(),
            "winning_trades": df[df.profit > 0].sum(),
            "losing_trades": df[df.profit <= 0].sum(),
            #"best_trade": df[df.profit].max(),
            #"worst_trade": df[df.profit].min(),
            #"win_percent": df[df.profit > 0].sum() / len(self.closed_positions)
        }

        # ratio between hold duration and gain
        # ratio between signal strength (ie: sub growth) and gain
        # ratio between market cap and avg gain
        # max drawdown
        # max value
        # min value

        return stats


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
            "market_cap": [],
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
            price_data["market_cap"].append(price["market_cap"])

            prev_date = price["date"]

        for sub in subs:
            social_data["date"].append(sub["date"])
            social_data["reddit_subs"].append(sub["reddit_subscribers"])

        dfp = pd.DataFrame(price_data, columns=["date", "open", "close", "market_cap"])
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
        df["market_cap"] = df["market_cap"].combine_first(s2)
        df["market_cap"].interpolate()
        df["reddit_subs"] = df["reddit_subs"].combine_first(s2)
        df["reddit_subs"].interpolate()

        if df.isnull().values.any():
            print("ERROR: nulls in data")
            #raise Exception("missing data")

        data_frames[coin["_id"]] = df

        progress += 1
        print("progress: {} / {}".format(progress, len(coins)))

        # TODO: for now test on a small sub set (for quicker iteration)
        # TODO: this is very bad look ahead bias, because we're trading
        # the top coins as of today, but when we start the test a year ago they may not even exist
        # so this is a HUGE filtering out of failed coins
        if progress >= 5:
            break

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
