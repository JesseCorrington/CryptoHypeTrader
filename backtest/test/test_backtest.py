from datetime import datetime

from unittest import TestCase
from backtest import backtest


class TestBackTest(TestCase):

    # TODO: double check all these calcs, and do a negative one too
    def test_position(self):
        p1 = backtest.Position(1, 2, 1.5)
        self.assertEqual(p1.coin_buy_price, 1.5)
        self.assertEqual(p1.full_buy_price, 3.1278)
        self.assertEqual(p1.fees_paid, 0.0078000000000000005)
        self.assertEqual(p1.current_value(3.2), 6.12864)

        p1.close(3.2)
        self.assertEqual(p1.closed, True)
        self.assertEqual(p1.coin_sell_price, 3.2)
        self.assertEqual(p1.full_sell_price, 6.12864)
        self.assertEqual(p1.fees_paid, 0.02316)
        self.assertEqual(p1.profit(), 3.0008399999999997)
        self.assertEqual(p1.pct_profit(), 0.9594091693842316)

    def test(self):
        coins, data_frames = backtest.load_data()

        btc = 1
        eth = 2

        start_date = datetime(2016, 11, 1)
        end_date = datetime(2017, 11, 1)

        buy_hold1 = backtest.BuyAndHoldStrategy([btc], start_date, end_date)
        buy_hold2 = backtest.BuyAndHoldStrategy([eth], start_date, end_date)
        buy_hold3 = backtest.BuyAndHoldStrategy([btc, eth], start_date, end_date)

        reddit_growth1 = backtest.RedditGrowthStrategy(0, .01)
        reddit_growth2 = backtest.RedditGrowthStrategy(0, .02)
        reddit_growth3 = backtest.RedditGrowthStrategy(0, .03)

        random = backtest.RandomStrategy()

        strategies = [
            ("hold btc", buy_hold1),
            ("hold eth", buy_hold2),
            ("hold btc and eth", buy_hold3),
            #("reddit growth 1", reddit_growth1),
            #("reddit growth 3", reddit_growth2),
            ("reddit growth 5", reddit_growth3),
            ("random", random)
        ]

        # TODO: add a hold whole market strategy too

        tests = []
        for name, strategy in strategies:
            back_test = backtest.BackTest(name, coins, data_frames, strategy)
            back_test.generate_signals()
            back_test.run(start_date, end_date)

            back_test.print_results()
            back_test.print_trades()

            tests.append(back_test)

        backtest.create_equity_compare_graph(tests)

        #backtest.create_equity_graph(tests[3])
