from datetime import datetime

from unittest import TestCase
from backtest import backtest


class TestBackTest(TestCase):
    def test(self):
        tester = backtest.BackTester()
        tester.load_data()

        btc = 1
        eth = 2

        start_date = datetime(2016, 11, 1)
        end_date = datetime(2017, 11, 1)

        buy_hold = backtest.BuyAndHoldStrategy([btc, eth], start_date, end_date)

        tester.generate_signals(buy_hold)

        while tester.tick():
            pass

        tester.create_equity_graph()