from datetime import datetime, timedelta
from unittest import TestCase

from ingestion.datasources import coinmarketcap as cmc


class TestCoinMarketCap(TestCase):
    def test_get_list(self):
        data = cmc.CoinList().get()
        self.assertGreater(len(data), 1200)

    def test_get_links(self):
        test_coin2 = {"cmc_id": "ethereum"}
        links = cmc.CoinLinks(test_coin2).get()
        self.assertEqual(links["subreddit"], "ethereum")
        self.assertEqual(links["twitter"], "ethereum")
        self.assertEqual(links["btctalk_ann"], "428589.0")

        test_coin = {"cmc_id": "ripple"}
        links = cmc.CoinLinks(test_coin).get()
        self.assertEqual(links["subreddit"], "ripple")
        self.assertEqual(links["twitter"], "Ripple")
        self.assertTrue("btctalk_ann" not in links)

    def test_get_historical_prices(self):
        test_coin = {"cmc_id": "bitcoin"}
        prices = cmc.HistoricalPrices(test_coin).get()

        prices.sort(key=lambda x: x["date"], reverse=True)

        newest = prices[0]["date"]
        oldest = prices[-1]["date"]

        today = datetime.utcnow()

        self.assertGreater(newest, oldest)
        self.assertLess(today - newest, timedelta(days=2))

        # test using a date range
        start = datetime(2017, 1, 1)
        end = start + timedelta(days=3)
        prices = cmc.HistoricalPrices(test_coin, start, end).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertEqual(end, prices[0]["date"])
        self.assertEqual(start, prices[-1]["date"])

    def test_ticker(self):
        current_prices = cmc.Ticker().get()
        self.assertGreater(len(current_prices), 1200)
