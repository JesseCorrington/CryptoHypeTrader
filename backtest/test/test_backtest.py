from datetime import datetime
from unittest import TestCase
from backtest import engine, strategies


class TestBackTest(TestCase):

    # TODO: double check all these calcs, and do a negative one too
    def test_position(self):
        p1 = engine.Position(1, 2, 1.5)
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
        coins, data_frames = engine.load_data()

        btc = 1
        eth = 2

        start_date = datetime(2016, 11, 1)
        end_date = datetime(2017, 11, 1)

        buy_hold1 = strategies.BuyAndHoldStrategy([btc], start_date, end_date)
        buy_hold2 = strategies.BuyAndHoldStrategy([eth], start_date, end_date)
        buy_hold3 = strategies.BuyAndHoldStrategy([btc, eth], start_date, end_date)
        buy_hold_all = strategies.BuyAndHoldStrategy("all", start_date, end_date)

        reddit_growth1 = strategies.RedditGrowthStrategy(0, .01)
        reddit_growth2 = strategies.RedditGrowthStrategy(0, .03)

        random = strategies.RandomStrategy()

        test_strategies = [
            #("hold btc", buy_hold1),
            #("hold eth", buy_hold2),
            ("hold btc and eth", buy_hold3),
            ("reddit growth 1", reddit_growth1),
            ("reddit growth 2", reddit_growth2),
            ("hold all", buy_hold_all),
            ("random", random)
        ]

        tests = []
        for name, strategy in test_strategies:
            back_test = engine.BackTest(name, coins, data_frames, strategy)
            back_test.generate_signals()
            back_test.run(start_date, end_date)

            back_test.create_report_csv("trades_{}.csv".format(name))
            tests.append(back_test)

        engine.create_equity_compare_graph(tests)

        #backtest.create_equity_graph(tests[0])
