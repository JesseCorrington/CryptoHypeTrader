from datetime import datetime
from unittest import TestCase
from backtest import engine, strategies
from common import database as db


db_config = {
    "host": "localhost",
    "port": 27017,
    "name": "hype-db"
}


class TestBackTest(TestCase):
    def test_position(self):
        today = datetime.utcnow()

        p1 = engine.Position(1, 2, today, 100)
        self.assertEqual(p1.coin_buy_price, 2)
        self.assertEqual(p1.full_buy_price, 100)
        self.assertEqual(p1.fees_paid, 0.24449877750611249)
        self.assertEqual(p1.current_value(3.2), 152.96625916870417)

        p1.close(3.2, today)
        self.assertEqual(p1.closed, True)
        self.assertEqual(p1.coin_sell_price, 3.2)
        self.assertEqual(p1.full_sell_price, 152.96625916870417)
        self.assertEqual(p1.fees_paid, 0.6278728606356969)
        self.assertEqual(p1.profit(), 52.96625916870417)
        self.assertEqual(p1.pct_profit(), 0.5296625916870417)

    def test(self):
        db.init(db_config)

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
            ("hold btc", buy_hold1),
            ("hold eth", buy_hold2),
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
