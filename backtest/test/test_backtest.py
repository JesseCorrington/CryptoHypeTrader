from unittest import TestCase
from backtest import backtest


class TestBackTest(TestCase):
    def test(self):
        tester = backtest.BackTester()
        tester.load_data()