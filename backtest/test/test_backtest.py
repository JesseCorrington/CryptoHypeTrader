from datetime import datetime

from unittest import TestCase
from backtest import backtest


class TestBackTest(TestCase):
    def test(self):
        coins, data_frames = backtest.load_data()

        btc = 1
        eth = 2

        start_date = datetime(2016, 11, 1)
        end_date = datetime(2017, 11, 1)

        buy_hold1 = backtest.BuyAndHoldStrategy([btc], start_date, end_date)
        buy_hold2 = backtest.BuyAndHoldStrategy([eth], start_date, end_date)
        buy_hold3 = backtest.BuyAndHoldStrategy([btc, eth], start_date, end_date)

        strategies = [buy_hold1, buy_hold2, buy_hold3]

        testers = []
        for strategy in strategies:
            tester = backtest.BackTester(coins, data_frames)
            tester.generate_signals(strategy)

            while tester.tick():
                pass

            testers.append(tester)

        backtest.create_equity_compare_graph(testers)
