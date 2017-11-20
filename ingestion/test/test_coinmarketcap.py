from datetime import datetime, timedelta
from unittest import TestCase

from ingestion.datasources import coinmarketcap as cmc


class TestCoinMarketCap(TestCase):
    def test_get_list(self):
        data = cmc.CoinList().get()
        self.assertTrue(len(data) > 1200)

    def test_get_links(self):
        test_coin = {"cmc_id": "bitcoin"}
        links = cmc.CoinLinks(test_coin).get()
        self.assertEqual(links["subreddit"], "bitcoin")
        self.assertEqual(links["twitter"], "bitcoin")
        self.assertTrue("btctalk_ann" not in links)

        test_coin2 = {"cmc_id": "ethereum"}
        links = cmc.CoinLinks(test_coin2).get()
        self.assertEqual(links["subreddit"], "ethereum")
        self.assertEqual(links["twitter"], "ethereumproject")
        self.assertEqual(links["btctalk_ann"], "428589.0")

    def test_get_historical_prices(self):
        test_coin = {"cmc_id": "bitcoin"}
        prices = cmc.HistoricalPrices(test_coin).get()

        prices.sort(key=lambda x: x["date"], reverse=True)

        newest = prices[0]["date"]
        oldest = prices[-1]["date"]

        today = datetime.utcnow()

        self.assertTrue(newest > oldest)
        self.assertTrue(today - newest < timedelta(days=2))

        # test using a date range
        start = datetime(2017, 1, 1)
        end = start + timedelta(days=3)
        prices = cmc.HistoricalPrices(test_coin, start, end).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertTrue(end == prices[0]["date"])
        self.assertTrue(start == prices[-1]["date"])

    def test_ticker(self):
        current_prices = cmc.Ticker().get()
        self.assertTrue(len(current_prices) > 1200)