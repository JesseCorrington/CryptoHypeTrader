from unittest import TestCase
from ingestion import coinmarketcap as cmc
from datetime import datetime, timedelta

class TestCoinMarketCap(TestCase):
    def test_get_list(self):
        data = cmc.CoinList().get()
        self.assertTrue(len(data) > 1200)

    def test_get_reddit(self):
        coins = cmc.CoinList().get()

        name = cmc.SubredditName("bitcoin").get()
        self.assertEqual(name, "bitcoin")

    def test_get_historical_prices(self):
        prices = cmc.HistoricalPrices("bitcoin").get()

        prices.sort(key=lambda x: x["date"], reverse=True)

        newest = prices[0]["date"]
        oldest = prices[-1]["date"]

        today = datetime.today()

        self.assertTrue(newest > oldest)
        self.assertTrue(today - newest < timedelta(days=2))

        # test using a date range
        start = datetime(2017, 1, 1)
        end = start + timedelta(days=3)
        prices = cmc.HistoricalPrices("bitcoin", start, end).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertTrue(end == prices[0]["date"])
        self.assertTrue(start == prices[-1]["date"])

    def test_ticker(self):
        current_prices = cmc.Ticker().get()
        self.assertTrue(len(current_prices) > 1200)