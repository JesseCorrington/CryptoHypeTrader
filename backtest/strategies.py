from random import randint
import pandas as pd
from backtest.engine import Strategy, Signal


class BuyAndHoldStrategy(Strategy):
    def __init__(self, coin_ids, buy_date, sell_date):
        self.coin_ids = coin_ids
        self.buy_date = buy_date
        self.sell_date = sell_date
        self.starting_cash = None
        self.hold_count = 0

    def generate_signals(self, coin_id, df):
        if self.coin_ids == "all" or coin_id in self.coin_ids:

            # TODO: probably the engine should pass in it's start and end date, but good enough for now
            self.buy_date = max(self.buy_date, df.index.min())
            self.sell_date = min(self.sell_date, df.index.max())

            df = pd.DataFrame(index=df.index)
            df["signals"] = Signal.NONE

            df.loc[self.buy_date:self.sell_date, "signals"] = Signal.HOLD
            df.loc[self.buy_date, "signals"] = Signal.BUY
            df.loc[self.sell_date, "signals"] = Signal.SELL

            self.hold_count += 1

            return df

    def allocation(self, available_cash):
        if not self.starting_cash:
            self.starting_cash = available_cash

        return self.starting_cash / self.hold_count


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
